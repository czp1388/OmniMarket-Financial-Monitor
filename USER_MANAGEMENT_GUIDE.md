# 👥 用户管理系统使用指南

## 功能概述
用户管理系统为金融监控系统提供了完整的用户认证和授权功能：

- 🔐 用户注册和登录
- 🎫 JWT令牌认证
- 👤 用户信息管理
- 🛡️ 密码安全加密

## API端点

### 用户认证
- POST /api/v1/users/register - 用户注册
- POST /api/v1/users/login - 用户登录
- GET /api/v1/users/me - 获取当前用户信息

### 用户管理
- GET /api/v1/users - 获取用户列表（需要认证）

## 使用示例

### 用户注册
\\\ash
POST /api/v1/users/register
{
  \"username\": \"testuser\",
  \"email\": \"test@example.com\", 
  \"password\": \"password123\"
}
\\\

### 用户登录
\\\ash
POST /api/v1/users/login
{
  \"username\": \"testuser\",
  \"password\": \"password123\"
}
\\\

### 使用令牌访问受保护接口
\\\ash
GET /api/v1/users/me
Authorization: Bearer <your_token>
\\\

## 安全特性
- 密码使用bcrypt加密存储
- JWT令牌过期时间可配置
- 支持Bearer Token认证

## 配置
在环境变量中设置：
- JWT_SECRET_KEY - JWT签名密钥
- ACCESS_TOKEN_EXPIRE_MINUTES - 令牌过期时间

## 下一步开发
- 用户角色和权限管理
- 用户个人预警规则
- 用户数据隔离
- 管理员功能
