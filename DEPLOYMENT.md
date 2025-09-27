# NEUSteel Agent 部署指南

## 🎯 同源部署配置

本项目已配置为同源部署模式，前端和后端运行在同一个域名下：`https://agent.hamaiqiji.xyz`

## 📋 部署架构

```
https://agent.hamaiqiji.xyz/
├── /                    # 前端应用 (Vue.js SPA)
├── /api/v1/            # 后端API接口
├── /health             # 健康检查端点
└── /assets/            # 静态资源
```

## 🚀 快速部署

### 1. 构建应用
```bash
# 一键构建前端到后端static目录
./build.sh
```

### 2. 启动生产环境
```bash
# 启动生产服务器
./start-production.sh
```

## 🔧 详细部署步骤

### 1. 环境准备

#### 系统要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Redis 6.0+

#### 安装依赖
```bash
# Python依赖
pip install -r backend/requirements.txt

# Node.js依赖
cd frontend && npm install
```

### 2. 环境配置

#### 后端配置 (`backend/.env`)
```bash
# MySQL Configuration
MYSQL_USER="your_mysql_user"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_HOST="localhost"
MYSQL_PORT=3306
MYSQL_DB="knowledge"

# Redis Configuration
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0

# JWT Configuration
JWT_SECRET_KEY="your_super_secret_key_change_me"
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
MAIL_HOST="smtp.qq.com"
MAIL_PORT=465
MAIL_USERNAME="your_email@qq.com"
MAIL_PASSWORD="your_email_password"
MAIL_FROM="your_email@qq.com"
MAIL_TLS=False
MAIL_SSL=True

# LLM Configuration
SILICONFLOW_API_KEY="your_api_key"
LLM_DEFAULT_MODEL="moonshotai/Kimi-K2-Instruct-0905"

# Chroma Vector DB
CHROMA_HOST="localhost"
CHROMA_PORT=8001
```

#### 前端配置
生产环境配置已自动设置为：`https://agent.hamaiqiji.xyz`

### 3. 数据库初始化
```bash
# 创建数据库表
mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DB < sql/schema.sql
```

### 4. 构建和部署
```bash
# 构建前端
./build.sh

# 启动服务
./start-production.sh
```

## 🌐 Nginx 配置示例

如果使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name agent.hamaiqiji.xyz;

    # SSL配置
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    # 重定向HTTP到HTTPS
    if ($scheme != "https") {
        return 301 https://$server_name$request_uri;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🔍 健康检查

部署完成后，可以通过以下端点检查服务状态：

- **API健康检查**: `https://agent.hamaiqiji.xyz/health`
- **前端应用**: `https://agent.hamaiqiji.xyz/`
- **API文档**: `https://agent.hamaiqiji.xyz/docs`

## 📊 监控和日志

### 应用日志
```bash
# 查看应用日志
tail -f /var/log/neusteel-agent.log
```

### 性能监控
- CPU和内存使用情况
- 数据库连接状态
- Redis连接状态
- API响应时间

## 🛠️ 故障排除

### 常见问题

1. **静态文件404错误**
   - 确保运行了 `./build.sh`
   - 检查 `backend/static/` 目录是否存在

2. **API调用失败**
   - 检查CORS配置
   - 确认环境变量配置正确

3. **数据库连接失败**
   - 检查MySQL服务状态
   - 验证数据库凭据

4. **Redis连接失败**
   - 检查Redis服务状态
   - 验证Redis配置

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建
./build.sh

# 3. 重启服务
pkill -f "uvicorn app.main:app"
./start-production.sh
```

## 📞 技术支持

如有部署问题，请联系技术团队或查看项目文档。
