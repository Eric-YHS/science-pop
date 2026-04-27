from fastapi import APIRouter

from app.api.papers import router as papers_router
from app.api.content import router as content_router
from app.api.workflow import router as workflow_router
from app.api.crawl import router as crawl_router

api_router = APIRouter(prefix="/api")
api_router.include_router(papers_router)
api_router.include_router(content_router)
api_router.include_router(workflow_router)
api_router.include_router(crawl_router)
