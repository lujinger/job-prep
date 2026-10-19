# FastAPI Bookmark API

基于 FastAPI 的 RESTful 书签管理 API，支持用户注册登录、JWT 认证、书签 CRUD 及用户数据隔离。

## 1.技术栈

- **Python 3.11**
- **FastAPI** — Web 框架
- **SQLAlchemy** — ORM
- **SQLite** — 开发数据库（可切换 PostgreSQL/MySQL）
- **Alembic** — 数据库迁移
- **JWT (HS256)** — 用户认证
- **Pytest + TestClient** — 单元测试
- **GitHub Actions** — CI 自动测试

## 2.功能特性

- 用户注册与登录（JWT Token，30 分钟过期）
- 书签增删改查（CRUD）
- 搜索（按标题/URL 关键词）
- 分页查询
- 用户数据隔离（跨用户访问返回 404）
- 自动生成 OpenAPI 文档（`/docs`）
- 单元测试 + CI 自动跑测

## 3.如何运行

### 3.1. 克隆项目并进入目录

```bash
git clone https://github.com/lujinger/job-prep.git

cd Python/fastapi
```

### 3.2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv

.venv\Scripts\activate # Windows

pip install -r requirements.txt
```

### 3.3. 初始化数据库
```bash
alembic upgrade head
```

### 3.4. 运行项目
```bash
uvicorn app.main:app --reload
```


访问 http://localhost:8000/docs 查看交互式 API 文档。

## 4.API 接口说明

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/register` | 否 | 用户注册 |
| POST | `/login` | 否 | 用户登录，返回 JWT Token |
| POST | `/bookmarks/` | 是 | 创建书签 |
| GET | `/bookmarks/` | 是 | 获取书签列表（支持 `?q=` 搜索、`?skip=` 分页） |
| GET | `/bookmarks/{id}` | 是 | 获取单条书签 |
| PUT | `/bookmarks/{id}` | 是 | 更新书签（支持部分更新） |
| DELETE | `/bookmarks/{id}` | 是 | 删除书签 |

## 5.示例请求/响应

### 5.1.注册用户 (register)
**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/register' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "haihai",
  "password": "123456"
}'
```
**Response:**
HTTP/1.1 200 OK
```json
{
  "id": 3,
  "username": "haihai"
}
```
### 5.2.登录用户 (login)
**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/login' \
  -H 'accept: */*' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=haihai&password=123456&scope=&client_id=string&client_secret=********'
```
**Response:**
HTTP/1.1 200 OK

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkyNDI0MzEwfQ.tMVh2ZSjZ6U-VS1GNRt44J0_106MIz9WxkRGiauDBtI",
  "token_type": "bearer"
}
```
### 5.3.创建书签 (create_bookmark)  
**Request:**    
```bash
curl -X 'POST' \
  'http://localhost:8000/bookmarks/' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkyNDI0NDgzfQ.HCVfcT9i6sy0A16Tz05XK48dkECqPu-EBZNUU6l4d8M' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Google",
  "url": "https://www.google.com"
}'
```
**Response:**
HTTP/1.1 201 Created
```json
{
  "id": 3,
  "title": "Google",
  "url": "https://www.google.com",
  "created_at": "2026-10-19T15:27:11.895217"
}
```
### 5.4.获取书签列表 (get_bookmarks)  
**Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/bookmarks/?skip=0&limit=10' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkyNDI0NDgzfQ.HCVfcT9i6sy0A16Tz05XK48dkECqPu-EBZNUU6l4d8M'
```
**Response:**
HTTP/1.1 200 OK
```json
[
  {
    "id": 3,
    "title": "Google",
    "url": "https://www.google.com",
    "created_at": "2026-10-19T15:27:11.895217"
  }
]
```
### 5.5.获取单条书签 (get_bookmark)  
**Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/bookmarks/3' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkyNDI5MDU0fQ.PJtfDeeloc0ZnvMxQ5up1_UdWDl99De1HSVnk-CaYkk'
```
**Response:**
HTTP/1.1 200 OK
```json
{
  "id": 3,
  "title": "Google",
  "url": "https://www.google.com",
  "created_at": "2026-10-19T15:27:11.895217"
}
```
### 5.6.更新书签 (update_bookmark)  
**Request:**    
```bash
curl -X 'PUT' \
  'http://localhost:8000/bookmarks/3' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkyNDI5MDU0fQ.PJtfDeeloc0ZnvMxQ5up1_UdWDl99De1HSVnk-CaYkk' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Google update",
  "url": "https://www.google.com"
}'
```
**Response:**
HTTP/1.1 200 OK
```json
{
  "id": 3,
  "title": "Google update",
  "url": "https://www.google.com",
  "created_at": "2026-10-19T15:27:11.895217"
}
```
### 5.7.删除书签 (delete_bookmark)  
**Request:**
```bash
curl -X 'DELETE' \
  'http://localhost:8000/bookmarks/3' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzkyNDI5MDU0fQ.PJtfDeeloc0ZnvMxQ5up1_UdWDl99De1HSVnk-CaYkk'
```
**Response:**
HTTP/1.1 204 No Content
```json
{
  "id": 3,
  "title": "Google Updated",
  "url": "https://www.google.com",
  "created_at": "2026-10-19T15:27:11.895217"
}
```

## 6.项目结构
fastapi/

├── app/

│   ├── main.py          # FastAPI 应用入口

│   ├── database.py      # 数据库连接

│   ├── models/          # SQLAlchemy 模型

│   │   ├── user.py

│   │   └── bookmark.py

│   ├── schemas/         # Pydantic 数据校验模型

│   │   └── bookmark.py

│   ├── auth.py          # JWT 认证逻辑

│   ├── dependencies.py  # 依赖注入（密码哈希等）

│   └── routers/         # 路由模块

│       └── bookmarks.py

├── alembic/             # 数据库迁移

├── tests/               # 单元测试

│   ├── conftest.py

│   ├── test_auth.py

│   └── test_bookmarks.py

├── alembic.ini

├── requirements.txt

└── README.md

## 7.测试
### 7.1. 运行全部测试
```bash
pytest tests/ -v
```
### 7.2. 运行单个测试文件
```bash
pytest tests/test_bookmarks.py -v
```
### 7.3. 运行单个测试用例
```bash
pytest tests/test_bookmarks.py::test_create_bookmark
```
### 7.4. 查看覆盖率
```bash
coverage run -m pytest tests/ -v
coverage report
```
## 7.CI/CD

每次 push 到 `main` 分支，GitHub Actions 自动执行：
- 安装依赖
- 数据库迁移
- 运行全部测试
- 生成覆盖率报告
