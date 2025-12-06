# Docker 部署文档

## OmniMarket 金融监控系统 - Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署 OmniMarket 系统。

---

## 📋 前置要求

### 必需软件

- **Docker**: 版本 20.10+ 
  - Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Linux: `sudo apt-get install docker.io docker-compose`
  - macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop)

- **Docker Compose**: 版本 2.0+
  - Docker Desktop 已包含
  - Linux 独立安装: `sudo apt-get install docker-compose-plugin`

### 系统要求

- **CPU**: 2核心以上
- **内存**: 4GB+ (推荐8GB)
- **磁盘**: 20GB+ 可用空间
- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 10.15+

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/czp1388/OmniMarket-Financial-Monitor.git
cd OmniMarket-Financial-Monitor
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.docker.example .env.docker

# 编辑配置文件 (必填项)
notepad .env.docker  # Windows
nano .env.docker     # Linux/macOS
```

**必填配置项**:
```env
POSTGRES_PASSWORD=your-secure-password-123
INFLUXDB_PASSWORD=your-influxdb-password-456
INFLUXDB_TOKEN=your-influxdb-token-789
REDIS_PASSWORD=your-redis-password-abc
SECRET_KEY=your-super-secret-key-min-32-chars-xyz
```

### 3. 启动服务

```bash
# 使用自定义环境变量文件启动
docker-compose --env-file .env.docker up -d

# 或使用默认 .env 文件 (需重命名)
mv .env.docker .env
docker-compose up -d
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问服务
# 前端: http://localhost
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

---

## 📦 服务架构

### 容器列表

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| **Frontend** | omnimarket-frontend | 80 | Nginx + React |
| **Backend** | omnimarket-backend | 8000 | FastAPI + Uvicorn |
| **PostgreSQL** | omnimarket-postgres | 5432 | 关系型数据库 |
| **InfluxDB** | omnimarket-influxdb | 8086 | 时序数据库 |
| **Redis** | omnimarket-redis | 6379 | 缓存服务 |

### 数据卷

- `postgres_data`: PostgreSQL 数据持久化
- `influxdb_data`: InfluxDB 数据持久化
- `influxdb_config`: InfluxDB 配置
- `redis_data`: Redis 数据持久化

---

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器+数据卷 (危险!)
docker-compose down -v
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 容器管理

```bash
# 进入后端容器
docker exec -it omnimarket-backend bash

# 进入 PostgreSQL 容器
docker exec -it omnimarket-postgres psql -U omnimarket

# 进入 Redis 容器
docker exec -it omnimarket-redis redis-cli -a your-redis-password
```

### 数据备份

```bash
# 备份 PostgreSQL 数据库
docker exec omnimarket-postgres pg_dump -U omnimarket omnimarket > backup_$(date +%Y%m%d).sql

# 恢复 PostgreSQL 数据库
docker exec -i omnimarket-postgres psql -U omnimarket omnimarket < backup_20250101.sql

# 备份 InfluxDB
docker exec omnimarket-influxdb influx backup /backup/influxdb_backup
docker cp omnimarket-influxdb:/backup/influxdb_backup ./influxdb_backup
```

---

## ⚙️ 配置说明

### 环境变量

#### 数据库配置

```env
# PostgreSQL
POSTGRES_PASSWORD=强密码 (建议16位以上)

# InfluxDB
INFLUXDB_PASSWORD=强密码 (建议16位以上)
INFLUXDB_TOKEN=随机token (建议32位以上)

# Redis
REDIS_PASSWORD=强密码 (建议16位以上)
```

#### 应用配置

```env
# JWT密钥 (必须32位以上)
SECRET_KEY=your-super-secret-key-min-32-characters-long
```

#### API密钥 (可选)

```env
# Alpha Vantage (外汇/美股数据)
ALPHA_VANTAGE_API_KEY=RWXKVB0M1GWJJYF5

# 币安 API (加密货币)
BINANCE_API_KEY=your-binance-key
BINANCE_SECRET_KEY=your-binance-secret

# Tushare (A股数据)
TUSHARE_TOKEN=your-tushare-token
```

#### 通知配置 (可选)

```env
# 邮件通知
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram 通知
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 端口映射修改

编辑 `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 修改前端端口为8080
  
  backend:
    ports:
      - "9000:8000"  # 修改后端端口为9000
```

### 资源限制

在 `docker-compose.yml` 中添加:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

---

## 🔒 安全建议

### 生产环境部署

1. **使用强密码**:
   - 所有数据库密码至少16位
   - SECRET_KEY 至少32位随机字符

2. **限制端口访问**:
   ```yaml
   services:
     postgres:
       ports:
         - "127.0.0.1:5432:5432"  # 仅本机访问
   ```

3. **启用 HTTPS**:
   - 使用 Let's Encrypt 证书
   - 配置 Nginx SSL

4. **定期备份**:
   - 每日自动备份数据库
   - 保留至少7天备份

5. **日志管理**:
   ```yaml
   services:
     backend:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

---

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查容器状态
docker-compose ps

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否健康
docker exec omnimarket-postgres pg_isready

# 检查 InfluxDB
docker exec omnimarket-influxdb influx ping

# 检查 Redis
docker exec omnimarket-redis redis-cli -a your-password ping
```

### 端口冲突

```bash
# 查看端口占用 (Windows)
netstat -ano | findstr :8000

# 查看端口占用 (Linux)
lsof -i :8000

# 修改 docker-compose.yml 中的端口映射
```

### 磁盘空间不足

```bash
# 清理未使用的镜像
docker system prune -a

# 清理未使用的数据卷
docker volume prune

# 查看磁盘使用
docker system df
```

---

## 🔄 更新部署

### 更新代码

```bash
# 拉取最新代码
git pull origin master

# 重新构建并启动
docker-compose build
docker-compose up -d

# 查看更新日志
docker-compose logs -f
```

### 数据库迁移

```bash
# 进入后端容器
docker exec -it omnimarket-backend bash

# 运行迁移脚本 (如果有)
python -m alembic upgrade head
```

---

## 📊 监控和维护

### 健康检查

所有服务都配置了健康检查:

```bash
# 查看健康状态
docker-compose ps

# 手动触发健康检查
docker inspect --format='{{json .State.Health}}' omnimarket-backend
```

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats omnimarket-backend
```

### 日志轮转

建议配置日志大小限制:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🌐 生产环境优化

### 1. 使用反向代理 (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name omnimarket.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 自动备份脚本

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# 备份 PostgreSQL
docker exec omnimarket-postgres pg_dump -U omnimarket omnimarket > $BACKUP_DIR/postgres_$DATE.sql

# 备份 InfluxDB
docker exec omnimarket-influxdb influx backup /backup/influx_$DATE

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

### 3. 监控告警

使用 Prometheus + Grafana 监控:

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

---

## 📞 支持

- **GitHub Issues**: https://github.com/czp1388/OmniMarket-Financial-Monitor/issues
- **文档**: 项目根目录下的 `*.md` 文件
- **API文档**: http://localhost:8000/docs

---

**最后更新**: 2025年12月7日  
**Docker版本**: 20.10+  
**Docker Compose版本**: 2.0+
