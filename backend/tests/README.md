# Backend Tests

本目录包含 OmniMarket 后端的所有单元测试和集成测试。

## 目录结构

```
tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                 # Pytest 配置和 fixtures
├── test_services/              # 服务层测试
│   ├── test_data_service.py
│   ├── test_alert_service.py
│   └── test_websocket_manager.py
├── test_api/                   # API 端点测试
│   ├── test_market_data.py
│   ├── test_alerts.py
│   └── test_virtual_trading.py
└── test_models/                # 数据模型测试
    └── test_market_data_models.py
```

## 运行测试

### 安装测试依赖
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_services/test_data_service.py
```

### 生成覆盖率报告
```bash
pytest --cov=backend --cov-report=html
```

### 运行标记的测试
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

## 测试标记

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.slow`: 慢速测试
- `@pytest.mark.asyncio`: 异步测试

## 编写测试的最佳实践

1. **命名规范**: 测试文件以 `test_` 开头，测试函数以 `test_` 开头
2. **使用 fixtures**: 复用测试数据和设置
3. **模拟外部依赖**: 使用 `pytest-mock` 模拟 API 调用和数据库操作
4. **测试覆盖率**: 目标覆盖率 > 80%
5. **异步测试**: 使用 `@pytest.mark.asyncio` 装饰器

## 示例

### 单元测试示例
```python
import pytest
from backend.services.data_service import DataService

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_klines_success(mock_coingecko):
    """测试成功获取 K 线数据"""
    service = DataService()
    result = await service.get_klines(
        symbol="BTC/USDT",
        market_type="CRYPTO",
        exchange="binance",
        timeframe="1h"
    )
    assert len(result) > 0
    assert result[0].symbol == "BTC/USDT"
```

### 集成测试示例
```python
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.integration
@pytest.mark.asyncio
async def test_market_data_endpoint():
    """测试市场数据 API 端点"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/market/klines", params={
            "symbol": "BTC/USDT",
            "market_type": "CRYPTO",
            "timeframe": "1h"
        })
    assert response.status_code == 200
    assert len(response.json()) > 0
```
