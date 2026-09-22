# 科普转化平台 (science-pop)

将学术论文自动转化为科普内容（文章 + 配图）的后端服务：按学科定时爬取论文源，
下载原文，调用 Coze 工作流生成科普稿，并将结果作为内容资产管理。

技术栈：**FastAPI + SQLAlchemy 2 (async) + PostgreSQL + Alembic + APScheduler**。

## 快速开始

```bash
# 1. 安装依赖（建议 Python 3.11+）
pip install -r requirements.txt

# 2. 准备配置：复制环境变量文件并填入真实密钥
cp .env.example .env

# 3. 启动 PostgreSQL（或使用已有的数据库实例）
#    DATABASE_URL 默认为 postgresql+asyncpg://postgres:password@localhost:5432/science_pop

# 4. 启动服务（首次启动会自动建表并写入初始学科数据）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

打开 <http://127.0.0.1:8000/docs> 查看交互式 API 文档。

数据库迁移使用 Alembic：

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## 配置项

所有配置通过环境变量（或 `.env` 文件）注入，见 `.env.example`：

| 变量 | 说明 |
| --- | --- |
| `DATABASE_URL` | async SQLAlchemy 连接串 |
| `DEBUG` | 为 `true` 时打印 SQL，并在未配置 Coze 时跳过工作流 |
| `STORAGE_PATH` | 论文原文与生成内容的存储根目录（默认 `./storage`） |
| `COZE_API_URL` / `COZE_API_KEY` | Coze 接口地址与个人访问令牌（**不要提交真实密钥**） |
| `COZE_GPT_WORKFLOW_ID` / `COZE_BANANA_WORKFLOW_ID` | 文本工作流与配图工作流 ID |
| `CRAWL_MAX_PAPERS_PER_SOURCE` | 单次爬取每个来源的论文上限 |
| `CRAWL_USER_AGENT` | 爬虫 User-Agent |

`COZE_API_KEY` 为空时服务仍可启动，工作流执行会被跳过并记录日志。

## API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| GET | `/api/papers` | 论文列表（支持 `discipline_id`、`status`、分页） |
| GET | `/api/papers/{paper_id}` | 论文详情 |
| POST | `/api/papers/upload` | 上传论文（pdf / txt） |
| GET | `/api/papers/disciplines` | 学科及其数据来源 |
| GET | `/api/contents` | 生成内容列表 |
| GET | `/api/contents/{content_id}` | 内容详情 |
| POST | `/api/workflow/convert` | 触发论文 → 科普内容转换 |
| GET | `/api/workflow/status/{content_id}` | 查询转换状态 |
| POST | `/api/crawl/trigger` | 手动触发爬取（全部或指定来源） |
| GET | `/api/crawl/tasks` | 爬取任务记录 |

## 目录结构

```text
app/
├── main.py               # FastAPI 应用、启动时建表 + 初始化 + 定时任务
├── config.py             # pydantic-settings 配置
├── database.py           # async engine / session / Base
├── api/                  # 路由层（papers / contents / workflow / crawl）
├── models/               # SQLAlchemy ORM 模型
├── schemas/              # Pydantic 响应模型
├── services/
│   ├── crawler/          # 爬虫：base + arxiv + pubmed + scheduler
│   ├── workflow.py       # Coze 工作流客户端（SSE 流式）
│   └── file_handler.py   # 文件存储
└── utils/disciplines.py  # 学科与数据来源静态配置
migrations/               # Alembic 迁移
docs/                     # 需求与项目规范
tests/                    # pytest 测试
```

## 定时任务

`app/main.py` 在应用启动时注册 APScheduler 定时任务：**每周日 02:00** 执行
`run_all()`，对已实现爬虫的来源（当前为 arXiv 与 PubMed Central）抓取论文并入库。
手动触发：`POST /api/crawl/trigger`。

新增数据来源的步骤：

1. 在 `app/utils/disciplines.py` 中声明来源；
2. 在 `app/services/crawler/` 下实现 `BaseCrawler` 子类；
3. 将来源名注册到 `app/services/crawler/scheduler.py` 的 `CRAWLERS`。

## 开发

```bash
pip install ruff pytest
ruff check .
pytest
```

提交信息遵循 `类型: 简短描述`（见 `docs/conventions.md`），且不添加
`Co-Authored-By`。

## CI

`.github/workflows/ci.yml` 在 push / PR 上安装 `requirements.txt` 并运行
`ruff check` 与 `pytest`。
