# FastAPI 项目模板

这是一个FastAPI 项目模板，包含了一套用户认证系统。

## 功能特性

- **用户注册**: 基于邮件验证码的安全用户注册流程。
- **用户登录**: 基于 JWT 的认证机制（包含 `access_token` 和 `refresh_token`）。
- **令牌刷新**: 使用 `refresh_token` 刷新过期的 `access_token`。
- **安全退出**: 通过在 Redis 中将 `refresh_token` 加入黑名单，实现服务端安全登出。
- **密码管理**: 提供带验证逻辑的安全的密码修改功能。
- **数据库集成**: 使用 SQLAlchemy 作为 ORM，并已配置 MySQL。
- **缓存与黑名单**: 使用 Redis 进行缓存和令牌黑名单管理。
- **配置管理**: 通过 Pydantic 实现集中化的配置管理。
- **邮件服务**: 集成了邮件服务，用于发送验证码。

## 项目依赖

本项目主要依赖以下库：

- `fastapi`: 核心 Web 框架。
- `uvicorn[standard]`: 用于运行应用的 ASGI 服务器。
- `pydantic` & `pydantic-settings`: 用于数据校验和配置管理。
- `SQLAlchemy`: 用于数据库对象关系映射 (ORM)。
- `pymysql`: MySQL 驱动。
- `redis`: 用于连接 Redis 服务器。
- `python-jose[cryptography]`: 用于处理 JSON Web Tokens (JWT)。
- `passlib[bcrypt]`: 用于密码的哈希与验证。
- `email-validator`: 用于校验邮箱格式。
- `fastapi-mail`: 用于发送邮件。
- `python-multipart`: 用于处理表单数据（Swagger UI 授权流程需要）。

## 安装与启动

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/JimmyPowell/fastapi-project-template.git
    cd fastapi-project-template
    ```

2.  **创建并激活虚拟环境:**
    ```bash
    python -m venv env
    source env/bin/activate  # Windows 系统请使用 `env\Scripts\activate`
    ```

3.  **安装依赖:**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **配置环境变量:**
    -   在 `backend` 目录下，复制 `.env.example` 文件为 `.env`。
    -   在 `backend/.env` 文件中，填入您的数据库、Redis 和邮件服务凭据。

5.  **运行应用:**
    ```bash
    cd backend
    uvicorn app.main:app --reload
    ```
    应用将在 `http://127.0.0.1:8000` 上可用。

## API 端点

所有端点都以 `/api/v1` 为前缀。

### 认证 (`/auth`)

-   `POST /request-code`: 请求发送验证码到指定邮箱。
-   `POST /verify-code`: 校验验证码，并获取用于注册的会话令牌。
-   `POST /register`: 完成用户注册流程。
-   `POST /login`: 使用用户名/邮箱和密码登录，获取令牌。
-   `POST /token`: (供 Swagger UI 使用) 使用表单数据登录，获取令牌。
-   `POST /refresh`: 使用 `refresh_token` 刷新 `access_token`。
-   `POST /logout`: 将 `refresh_token` 加入黑名单以实现登出。
-   `POST /change-password`: 修改当前用户的密码（需要 `access_token` 授权）。
