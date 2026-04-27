import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Paper, Discipline
from app.schemas.paper import PaperResponse, PaperListResponse
from app.config import settings

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=PaperListResponse)
async def list_papers(
    discipline_id: int | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Paper)
    count_query = select(func.count(Paper.id))

    if discipline_id:
        query = query.where(Paper.discipline_id == discipline_id)
        count_query = count_query.where(Paper.discipline_id == discipline_id)
    if status:
        query = query.where(Paper.status == status)
        count_query = count_query.where(Paper.status == status)

    total = (await db.execute(count_query)).scalar_one()
    items = (
        await db.execute(
            query.order_by(Paper.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    return PaperListResponse(total=total, items=items)


@router.get("/disciplines", response_model=list)
async def list_disciplines(db: AsyncSession = Depends(get_db)):
    results = (await db.execute(select(Discipline).order_by(Discipline.id))).scalars().all()
    return [
        {"id": d.id, "name": d.name, "slug": d.slug, "sources": d.sources}
        for d in results
    ]


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: int, db: AsyncSession = Depends(get_db)):
    paper = (await db.execute(select(Paper).where(Paper.id == paper_id))).scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    return paper


@router.post("/upload", response_model=PaperResponse)
async def upload_paper(
    title: str,
    file: UploadFile = File(...),
    discipline_id: int | None = None,
    doi: str | None = None,
    source_url: str | None = None,
    authors: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if discipline_id:
        disc = (await db.execute(select(Discipline).where(Discipline.id == discipline_id))).scalar_one_or_none()
        if not disc:
            raise HTTPException(400, "Invalid discipline_id")

    file_type = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "txt"
    if file_type not in ("pdf", "txt"):
        raise HTTPException(400, "Only pdf and txt files are supported")

    save_dir = settings.papers_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    from uuid import uuid4
    file_name = f"{uuid4().hex}.{file_type}"
    file_path = save_dir / file_name

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    paper = Paper(
        title=title,
        authors=authors,
        doi=doi,
        source_url=source_url,
        discipline_id=discipline_id,
        file_path=str(file_path),
        file_type=file_type,
        status="pending",
    )
    db.add(paper)
    await db.commit()
    await db.refresh(paper)
    return paper
