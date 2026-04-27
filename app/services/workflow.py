import json
import logging
from typing import Any

import httpx
from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models import Content, Paper

logger = logging.getLogger(__name__)

COZE_STREAM_RUN_URL = "/v1/workflow/stream_run"
COZE_UPLOAD_URL = "/v1/files/upload"


class CozeWorkflowClient:
    def __init__(self):
        self.api_url = settings.COZE_API_URL
        self.api_key = settings.COZE_API_KEY
        self.gpt_workflow_id = settings.COZE_GPT_WORKFLOW_ID
        self.banana_workflow_id = settings.COZE_BANANA_WORKFLOW_ID

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    @property
    def _is_configured(self) -> bool:
        return bool(self.api_key and self.gpt_workflow_id)

    async def upload_file(self, file_path: str) -> str | None:
        """Upload a file to COZE, return file_id."""
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        async with httpx.AsyncClient(timeout=60) as client:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    f"{self.api_url}{COZE_UPLOAD_URL}",
                    headers=self._headers(),
                    files={"file": (path.name, f)},
                    data={"purpose": "workflow"},
                )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("file_id") or data.get("data", {}).get("id")

    async def trigger_workflow(self, content_id: int, paper: Paper, workflow_type: str) -> None:
        if not self._is_configured:
            logger.info(f"COZE not configured, skipping workflow for content_id={content_id}")
            await self._update_status(content_id, "completed" if settings.DEBUG else "pending")
            return

        workflow_id = self.gpt_workflow_id if workflow_type == "gpt" else self.banana_workflow_id

        try:
            await self._update_status(content_id, "processing")

            parameters: dict[str, Any] = {}

            if paper.file_path:
                file_id = await self.upload_file(paper.file_path)
                if file_id:
                    parameters["file"] = file_id
                else:
                    logger.warning(f"Failed to upload file for paper {paper.id}, proceeding without file")

            result = await self._run_stream(workflow_id, parameters)
            await self._save_result(content_id, result)
            await self._update_status(content_id, "completed")

        except Exception as e:
            logger.error(f"Workflow failed for content_id={content_id}: {e}")
            await self._update_status(content_id, "failed")

    async def _run_stream(self, workflow_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Run workflow via SSE stream, collect all events, return final result."""
        payload = {
            "workflow_id": workflow_id,
            "parameters": parameters,
        }

        result: dict[str, Any] = {"article": "", "images": [], "debug_url": ""}
        current_event = ""

        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream(
                "POST",
                f"{self.api_url}{COZE_STREAM_RUN_URL}",
                json=payload,
                headers={**self._headers(), "Content-Type": "application/json"},
            ) as resp:
                resp.raise_for_status()

                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("event:"):
                        current_event = line.split(":", 1)[1].strip()
                        continue

                    if not line.startswith("data:"):
                        continue

                    data_str = line.split(":", 1)[1].strip()
                    if not data_str or data_str == "{}":
                        continue

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if current_event == "Error":
                        error_msg = data.get("error_message", "Unknown error")
                        raise RuntimeError(f"COZE workflow error: {error_msg}")

                    if current_event == "Done":
                        result["debug_url"] = data.get("debug_url", "")
                        break

                    if current_event == "Message":
                        content = data.get("content", "")
                        if content:
                            try:
                                content_data = json.loads(content)
                                if isinstance(content_data, dict):
                                    if "article" in content_data:
                                        result["article"] = content_data["article"]
                                    if "images" in content_data:
                                        result["images"] = content_data["images"]
                                    if "text" in content_data:
                                        result["article"] += content_data["text"]
                            except json.JSONDecodeError:
                                result["article"] += content

        return result

    async def _update_status(self, content_id: int, status: str) -> None:
        async with async_session() as db:
            content = (await db.execute(select(Content).where(Content.id == content_id))).scalar_one_or_none()
            if content:
                content.status = status
                await db.commit()

    async def _save_result(self, content_id: int, result: dict[str, Any]) -> None:
        async with async_session() as db:
            content = (await db.execute(select(Content).where(Content.id == content_id))).scalar_one_or_none()
            if content:
                content.article_text = result.get("article", "")
                content.image_paths = result.get("images", [])
                await db.commit()
