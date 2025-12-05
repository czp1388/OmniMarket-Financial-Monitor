# OmniMarket 金融监控系统 - 部署文档

## 概述

本文档提供 OmniMarket 金融监控系统在生产环境的完整部署指南，包括系统要求、安装步骤、配置说明和运维建议。

---

## 目录

1. [系统要求](#系统要求)
2. [部署架构](#部署架构)
3. [环境准备](#环境准备)
4. [数据库配置](#数据库配置)
5. [后端部署](#后端部署)
6. [前端部署](#前端部署)
7. [Nginx 配置](#nginx-配置)
8. [Docker 部署](#docker-部署)
9. [监控和日志](#监控和日志)
10. [故障排查](#故障排查)

---

## 系统要求

### 最低配置
- **CPU**: 2核
- **内存**: 4GB RAM
- **存储**: 50GB SSD
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+

### 推荐配置
- **CPU**: 4核+
- **内存**: 8GB+ RAM
- **存储**: 100GB+ SSD
- **操作系统**: Ubuntu 22.04 LTS

### 软件依赖
- **Python**: 3.9+
- **Node.js**: 16+
- **PostgreSQL**: 13+
- **InfluxDB**: 2.0+
- **Redis**: 6.0+
- **Nginx**: 1.18+ (可选，用于反向代理)

---

## 部署架构

### 单机部署架构
```
┌─────────────────────────────────────────────┐
│              Nginx (80/443)                 │
│         (反向代理 + 静态文件)                │
└──────────────┬─────────────┬────────────────┘
               │             │
    ┌──────────▼───────┐  ┌─▼──────────────┐
    │  Frontend (静态)  │  │  Backend API   │
    │   React Build    │  │  FastAPI:8000  │
    └──────────────────┘  └─┬──────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────┐      ┌──────▼──────┐    ┌─────▼────┐
    │PostgreSQL│      │  InfluxDB   │    │  Redis   │
    │  :5432   │      │   :8086     │    │  :6379   │
    └──────────┘      └─────────────┘    └──────────┘
```

### 分布式部署架构
```
                    ┌─────────────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐     ┌─────▼─────┐
   │Backend 1│       │Backend 2  │     │Backend 3  │
   └────┬────┘       └─────┬─────┘     └─────┬─────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Database    │
                    │  Cluster    │
                    └─────────────┘
```

---

## 环境准备

### 1. 更新系统包
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. 安装 Python 3.9+
```bash
# Ubuntu/Debian
sudo apt install python3.9 python3.9-venv python3-pip -y

# CentOS/RHEL
sudo yum install python39 python39-devel -y
```

### 3. 安装 Node.js 16+
```bash
# 使用 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 验证安装
node --version
npm --version
```

### 4. 安装 Git
```bash
sudo apt install git -y
```

---

## 数据库配置

### PostgreSQL 安装和配置

#### 1. 安装 PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib -y

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. 创建数据库和用户
```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 psql 命令行中执行
CREATE DATABASE omnimarket;
CREATE USER omnimarket_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE omnimarket TO omnimarket_user;
\q
```

#### 3. 配置远程访问（可选）
编辑 PostgreSQL 配置文件：
```bash
sudo nano /etc/postgresql/13/main/postgresql.conf
```

修改：
```conf
listen_addresses = '*'
```

编辑 `pg_hba.conf`：
```bash
sudo nano /etc/postgresql/13/main/pg_hba.conf
```

添加：
```conf
host    omnimarket    omnimarket_user    0.0.0.0/0    md5
```

重启服务：
```bash
sudo systemctl restart postgresql
```

### InfluxDB 安装和配置

#### 1. 安装 InfluxDB 2.x
```bash
# 添加 InfluxDB 仓库
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/ubuntu focal stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

# 安装
sudo apt update
sudo apt install influxdb2 -y

# 启动服务
sudo systemctl start influxdb
sudo systemctl enable influxdb
```

#### 2. 初始化 InfluxDB
```bash
# 访问 Web UI 进行初始化
http://your-server:8086

# 或使用命令行
influx setup \
  --username admin \
  --password your_secure_password \
  --org omnimarket \
  --bucket market_data \
  --force
```

#### 3. 创建 API Token
```bash
influx auth create \
  --org omnimarket \
  --all-access \
  --description "OmniMarket API Token"
```

### Redis 安装和配置

#### 1. 安装 Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server -y

# 启动服务
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### 2. 配置 Redis
编辑配置文件：
```bash
sudo nano /etc/redis/redis.conf
```

修改：
```conf
# 设置密码
requirepass your_redis_password

# 允许远程访问（谨慎使用）
bind 0.0.0.0

# 持久化设置
save 900 1
save 300 10
save 60 10000
```

重启服务：
```bash
sudo systemctl restart redis-server
```

---

## 后端部署

### 1. 克隆项目
```bash
cd /opt
sudo git clone https://github.com/czp1388/OmniMarket-Financial-Monitor.git
cd OmniMarket-Financial-Monitor
```

### 2. 创建虚拟环境
```bash
cd backend
python3.9 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量
创建 `.env` 文件：
```bash
nano .env
```

添加配置（参考下面的完整配置）：
```env
# 应用配置
APP_NAME=OmniMarket Financial Monitor
VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=your-very-secure-random-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=postgresql://omnimarket_user:your_secure_password@localhost:5432/omnimarket
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token-here
INFLUXDB_ORG=omnimarket
INFLUXDB_BUCKET=market_data

# Redis 配置
REDIS_URL=redis://:your_redis_password@localhost:6379

# API 密钥（可选）
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
TUSHARE_TOKEN=
ALPHA_VANTAGE_API_KEY=

# 邮件通知配置（可选）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Telegram 通知配置（可选）
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# CORS 配置
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

### 5. 初始化数据库
```bash
# 运行数据库迁移（如果有）
# alembic upgrade head
```

### 6. 使用 Systemd 管理服务
创建服务文件：
```bash
sudo nano /etc/systemd/system/omnimarket-backend.service
```

添加内容：
```ini
[Unit]
Description=OmniMarket Backend Service
After=network.target postgresql.service influxdb.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/OmniMarket-Financial-Monitor/backend
Environment="PATH=/opt/OmniMarket-Financial-Monitor/backend/venv/bin"
ExecStart=/opt/OmniMarket-Financial-Monitor/backend/venv/bin/gunicorn main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/omnimarket/access.log \
    --error-logfile /var/log/omnimarket/error.log \
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建日志目录：
```bash
sudo mkdir -p /var/log/omnimarket
sudo chown www-data:www-data /var/log/omnimarket
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start omnimarket-backend
sudo systemctl enable omnimarket-backend
sudo systemctl status omnimarket-backend
```

---

## 前端部署

### 1. 构建前端
```bash
cd /opt/OmniMarket-Financial-Monitor/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建后的文件位于 `dist/` 目录。

### 2. 部署到 Nginx
将构建文件复制到 Web 目录：
```bash
sudo mkdir -p /var/www/omnimarket
sudo cp -r dist/* /var/www/omnimarket/
sudo chown -R www-data:www-data /var/www/omnimarket
```

---

## Nginx 配置

### 1. 安装 Nginx
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 配置站点
创建配置文件：
```bash
sudo nano /etc/nginx/sites-available/omnimarket
```

添加配置：
```nginx
# HTTP 服务器配置
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 重定向到 HTTPS（生产环境推荐）
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务器配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置（使用 Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 前端静态文件
    root /var/www/omnimarket;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_vary on;

    # 前端路由处理
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket 代理
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 超时设置
        proxy_read_timeout 86400;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # 日志
    access_log /var/log/nginx/omnimarket_access.log;
    error_log /var/log/nginx/omnimarket_error.log;
}
```

### 3. 启用站点
```bash
sudo ln -s /etc/nginx/sites-available/omnimarket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 配置 SSL 证书（Let's Encrypt）
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
```

---

## Docker 部署

### 1. 安装 Docker 和 Docker Compose
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 创建 Dockerfile（后端）
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. 创建 Dockerfile（前端）
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm ci

# 复制源代码并构建
COPY . .
RUN npm run build

# 使用 Nginx 提供静态文件
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4. 创建 docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    container_name: omnimarket-postgres
    environment:
      POSTGRES_DB: omnimarket
      POSTGRES_USER: omnimarket_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  influxdb:
    image: influxdb:2.0
    container_name: omnimarket-influxdb
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: ${INFLUXDB_PASSWORD}
      DOCKER_INFLUXDB_INIT_ORG: omnimarket
      DOCKER_INFLUXDB_INIT_BUCKET: market_data
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: ${INFLUXDB_TOKEN}
    volumes:
      - influxdb_data:/var/lib/influxdb2
    ports:
      - "8086:8086"
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    container_name: omnimarket-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: omnimarket-backend
    environment:
      DATABASE_URL: postgresql://omnimarket_user:${POSTGRES_PASSWORD}@postgres:5432/omnimarket
      INFLUXDB_URL: http://influxdb:8086
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - influxdb
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: omnimarket-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  influxdb_data:
  redis_data:
```

### 5. 创建 .env 文件
```env
POSTGRES_PASSWORD=your_postgres_password
INFLUXDB_PASSWORD=your_influxdb_password
INFLUXDB_TOKEN=your_influxdb_token
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_secret_key
```

### 6. 启动容器
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

---

## 监控和日志

### 1. 应用日志
后端日志位置：
- Systemd 部署: `/var/log/omnimarket/`
- Docker 部署: `docker-compose logs backend`

查看实时日志：
```bash
# Systemd
sudo tail -f /var/log/omnimarket/error.log

# Docker
docker-compose logs -f backend
```

### 2. Nginx 日志
```bash
# 访问日志
sudo tail -f /var/log/nginx/omnimarket_access.log

# 错误日志
sudo tail -f /var/log/nginx/omnimarket_error.log
```

### 3. 系统监控
推荐使用监控工具：
- **Prometheus + Grafana**: 系统和应用指标监控
- **ELK Stack**: 日志聚合和分析
- **Datadog / New Relic**: 商业APM解决方案

### 4. 健康检查
```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查数据库连接
curl http://localhost:8000/api/v1/health/db
```

---

## 故障排查

### 常见问题

#### 1. 后端无法启动
```bash
# 检查服务状态
sudo systemctl status omnimarket-backend

# 查看详细日志
sudo journalctl -u omnimarket-backend -n 50

# 检查端口占用
sudo netstat -tlnp | grep 8000
```

#### 2. 数据库连接失败
```bash
# 测试 PostgreSQL 连接
psql -h localhost -U omnimarket_user -d omnimarket

# 检查 PostgreSQL 服务
sudo systemctl status postgresql

# 查看 PostgreSQL 日志
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### 3. Redis 连接问题
```bash
# 测试 Redis 连接
redis-cli -a your_redis_password ping

# 检查 Redis 服务
sudo systemctl status redis-server
```

#### 4. 前端无法加载
```bash
# 检查 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 检查文件权限
ls -la /var/www/omnimarket
```

#### 5. WebSocket 连接失败
检查 Nginx 配置是否正确代理 WebSocket：
```nginx
location /ws {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    # ...其他配置
}
```

### 性能优化

#### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_kline_symbol ON kline_data(symbol);
CREATE INDEX idx_kline_timestamp ON kline_data(timestamp);

-- 定期清理旧数据
DELETE FROM kline_data WHERE timestamp < NOW() - INTERVAL '90 days';
```

#### 2. Redis 缓存优化
调整 Redis 内存策略：
```conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

#### 3. 应用优化
- 增加 Gunicorn workers 数量（CPU核心数 × 2 + 1）
- 启用 HTTP/2 和 Brotli 压缩
- 使用 CDN 加速静态资源

---

## 备份和恢复

### 数据库备份

#### PostgreSQL
```bash
# 备份
pg_dump -U omnimarket_user omnimarket > backup_$(date +%Y%m%d).sql

# 恢复
psql -U omnimarket_user omnimarket < backup_20240101.sql
```

#### InfluxDB
```bash
# 备份
influx backup /path/to/backup -t your_influxdb_token

# 恢复
influx restore /path/to/backup -t your_influxdb_token
```

### 自动备份脚本
```bash
#!/bin/bash
# /opt/backup/backup.sh

BACKUP_DIR="/opt/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份 PostgreSQL
pg_dump -U omnimarket_user omnimarket | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# 备份 InfluxDB
influx backup $BACKUP_DIR/influxdb_$DATE -t $INFLUXDB_TOKEN

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "influxdb_*" -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $DATE"
```

添加到 crontab：
```bash
crontab -e
# 每天凌晨 2 点执行备份
0 2 * * * /opt/backup/backup.sh >> /var/log/backup.log 2>&1
```

---

## 安全建议

### 1. 防火墙配置
```bash
# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许 SSH（远程管理）
sudo ufw allow 22/tcp

# 拒绝直接访问数据库端口（仅本地访问）
sudo ufw deny 5432/tcp
sudo ufw deny 8086/tcp
sudo ufw deny 6379/tcp

# 启用防火墙
sudo ufw enable
```

### 2. 定期更新
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新 Python 依赖
pip install --upgrade -r requirements.txt
```

### 3. 安全加固
- 使用强密码和 SSH 密钥认证
- 定期更换 API 密钥和数据库密码
- 启用 fail2ban 防止暴力破解
- 配置 HTTPS 和 HSTS
- 实施最小权限原则

---

## 维护检查清单

### 日常检查
- [ ] 检查服务运行状态
- [ ] 监控磁盘使用率
- [ ] 查看错误日志
- [ ] 验证备份完成

### 每周检查
- [ ] 审查系统性能指标
- [ ] 清理旧日志文件
- [ ] 测试备份恢复
- [ ] 更新安全补丁

### 每月检查
- [ ] 数据库性能优化
- [ ] 审查访问日志
- [ ] 更新依赖包
- [ ] 容量规划评估

---

## 支持和联系

如遇到部署问题，请通过以下方式获取帮助：
- GitHub Issues: https://github.com/czp1388/OmniMarket-Financial-Monitor/issues
- 项目文档: 参考 README.md 和 API_DOCS.md

---

*最后更新: 2024-01-01*
*版本: 1.0.0*
