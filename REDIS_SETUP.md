# Redis 安装和配置指南（Windows）

## 方法一：使用 Memurai（推荐，Windows 原生）

Memurai 是 Redis 的 Windows 原生实现，完全兼容 Redis 协议。

### 安装步骤

1. **下载 Memurai**
   - 访问：https://www.memurai.com/get-memurai
   - 下载免费版（Developer Edition）
   - 或使用 Chocolatey 安装：
     ```powershell
     choco install memurai-developer
     ```

2. **安装**
   - 运行下载的安装程序
   - 按默认配置安装即可

3. **启动服务**
   - 安装后会自动注册为 Windows 服务并启动
   - 默认端口：6379
   - 查看服务状态：
     ```powershell
     Get-Service Memurai
     ```

4. **测试连接**
   ```powershell
   # 使用 Redis CLI（包含在 Memurai 安装中）
   memurai-cli ping
   # 应返回：PONG
   ```

---

## 方法二：使用 WSL2 + Redis（Linux 方式）

如果已启用 WSL2，可以在 Linux 环境中运行标准 Redis。

### 安装步骤

1. **启用 WSL2**（如果未启用）
   ```powershell
   # 管理员权限运行
   wsl --install
   # 重启计算机
   ```

2. **安装 Ubuntu**
   ```powershell
   wsl --install -d Ubuntu
   ```

3. **在 WSL2 中安装 Redis**
   ```bash
   # 进入 WSL
   wsl

   # 更新包列表
   sudo apt update

   # 安装 Redis
   sudo apt install redis-server -y

   # 启动 Redis
   sudo service redis-server start

   # 测试连接
   redis-cli ping
   # 应返回：PONG
   ```

4. **配置开机自启（可选）**
   在 Windows 启动时自动启动 WSL 中的 Redis：
   - 创建 `start-redis.bat` 文件：
     ```batch
     @echo off
     wsl -u root service redis-server start
     ```
   - 将该文件添加到 Windows 启动项

---

## 方法三：使用 Docker（最简单）

如果已安装 Docker Desktop，可以直接运行 Redis 容器。

### 安装步骤

1. **安装 Docker Desktop**
   - 下载：https://www.docker.com/products/docker-desktop
   - 安装并启动

2. **运行 Redis 容器**
   ```powershell
   # 运行 Redis（持久化数据）
   docker run -d --name redis-omnimarket -p 6379:6379 -v redis-data:/data redis:latest redis-server --appendonly yes

   # 查看运行状态
   docker ps | Select-String redis

   # 测试连接
   docker exec -it redis-omnimarket redis-cli ping
   # 应返回：PONG
   ```

3. **管理 Redis 容器**
   ```powershell
   # 停止 Redis
   docker stop redis-omnimarket

   # 启动 Redis
   docker start redis-omnimarket

   # 重启 Redis
   docker restart redis-omnimarket

   # 删除容器（数据会保留在 redis-data 卷中）
   docker rm redis-omnimarket
   ```

---

## 方法四：使用 Redis for Windows（微软移植版）

**注意**：此版本较旧（基于 Redis 3.x），不推荐用于生产环境。

### 安装步骤

1. **下载**
   - GitHub：https://github.com/tporadowski/redis/releases
   - 下载最新的 `.zip` 或 `.msi` 安装包

2. **安装**
   - 解压或运行安装程序
   - 将 Redis 目录添加到系统 PATH

3. **启动 Redis**
   ```powershell
   # 前台运行
   redis-server.exe

   # 后台运行（注册为 Windows 服务）
   redis-server.exe --service-install
   redis-server.exe --service-start

   # 查看服务状态
   Get-Service redis
   ```

4. **测试连接**
   ```powershell
   redis-cli.exe ping
   # 应返回：PONG
   ```

---

## 验证 OmniMarket 连接 Redis

配置完成后，重启 OmniMarket 后端服务，检查日志：

```powershell
# 停止当前服务（按 Ctrl+C）
# 重新启动
cd E:\OmniMarket-Financial-Monitor\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**成功日志示例**：
```
INFO:backend.database:Redis连接成功
```

**失败日志示例**（无 Redis）：
```
WARNING:backend.database:Redis连接失败: Error 10061 connecting to localhost:6379
```

---

## Redis 配置优化（可选）

### 设置密码保护

1. **编辑 Redis 配置文件**
   - Memurai: `C:\Program Files\Memurai\memurai.conf`
   - WSL Redis: `/etc/redis/redis.conf`
   - Docker: 创建配置文件并挂载

2. **添加密码**
   ```conf
   requirepass your-strong-password-here
   ```

3. **重启 Redis**

4. **更新 OmniMarket 配置**
   在 `backend/.env` 中修改：
   ```env
   REDIS_URL=redis://:your-strong-password-here@localhost:6379
   ```

### 持久化配置

默认 Redis 会定期保存数据到磁盘。如需调整：

```conf
# RDB 快照（默认）
save 900 1      # 900秒内至少1个键变化
save 300 10     # 300秒内至少10个键变化
save 60 10000   # 60秒内至少10000个键变化

# AOF 持久化（推荐）
appendonly yes
appendfsync everysec
```

---

## 故障排除

### 问题 1: 端口 6379 被占用

**解决方案**：
```powershell
# 查看占用端口的进程
netstat -ano | findstr :6379

# 结束占用的进程（使用上面查到的 PID）
taskkill /PID <PID> /F
```

### 问题 2: WSL 中 Redis 无法从 Windows 访问

**解决方案**：
```bash
# 编辑 Redis 配置
sudo nano /etc/redis/redis.conf

# 修改绑定地址
bind 0.0.0.0

# 重启 Redis
sudo service redis-server restart
```

### 问题 3: Docker Redis 容器启动失败

**解决方案**：
```powershell
# 查看日志
docker logs redis-omnimarket

# 删除并重新创建
docker rm -f redis-omnimarket
docker run -d --name redis-omnimarket -p 6379:6379 redis:latest
```

---

## 性能监控

### 使用 redis-cli 监控

```bash
# 实时监控命令
redis-cli monitor

# 查看统计信息
redis-cli info

# 查看内存使用
redis-cli info memory

# 查看连接数
redis-cli info clients
```

### 使用 Redis GUI 工具

推荐工具：
- **RedisInsight**（官方，免费）：https://redis.com/redis-enterprise/redis-insight/
- **Another Redis Desktop Manager**（开源）：https://github.com/qishibo/AnotherRedisDesktopManager
- **Medis**（macOS，免费）：https://getmedis.com/

---

## 总结

**推荐方案**：

| 场景 | 推荐方法 | 优点 |
|------|---------|------|
| **开发环境** | Docker | 最简单，一条命令即可 |
| **Windows 原生** | Memurai | 性能最好，原生 Windows 服务 |
| **已有 WSL2** | WSL2 + Redis | 标准 Redis，功能完整 |
| **快速测试** | Redis for Windows | 轻量级，无需额外依赖 |

**OmniMarket 使用说明**：
- Redis 是**可选组件**，不影响核心功能
- 启用 Redis 后可提升：
  - ✅ 数据查询速度（缓存热数据）
  - ✅ WebSocket 消息性能
  - ✅ API 响应时间
- 未启用时系统自动降级到内存缓存
