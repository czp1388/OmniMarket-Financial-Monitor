# 测试快速参考指南

## 🚀 快速开始

### 运行测试
```bash
cd backend

# 运行所有测试
pytest

# 带详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=backend --cov-report=html

# 查看报告
start htmlcov/index.html
```

## 📁 测试文件结构

```
backend/tests/
├── conftest.py                     # 全局fixtures
├── test_api/
│   ├── __init__.py
│   └── test_market_data.py        # API集成测试
└── test_services/
    ├── test_data_service.py        # 数据服务测试
    ├── test_alert_service.py       # 预警服务测试
    ├── test_websocket_manager.py   # WebSocket测试
    ├── test_technical_analysis.py  # 技术分析测试
    ├── test_auto_trading.py        # 自动交易测试 ⭐
    └── test_virtual_trading.py     # 虚拟交易测试 ⭐
```

## 🎯 常用测试命令

```bash
# 运行特定文件
pytest tests/test_services/test_data_service.py

# 运行特定测试类
pytest tests/test_services/test_data_service.py::TestDataService

# 运行特定测试方法
pytest tests/test_services/test_data_service.py::TestDataService::test_get_klines_from_cache

# 使用标记
pytest -m unit        # 只运行单元测试
pytest -m integration # 只运行集成测试
pytest -m "not slow"  # 跳过慢速测试

# 调试
pytest --pdb          # 失败时进入调试器
pytest -s             # 显示print输出
pytest -vv            # 超详细输出
pytest -x             # 第一个失败后停止

# 覆盖率
pytest --cov=backend                    # 基本覆盖率
pytest --cov=backend --cov-report=term  # 终端报告
pytest --cov=backend --cov-report=html  # HTML报告
pytest --cov=backend --cov-report=xml   # XML报告(CI用)

# 性能
pytest --durations=10  # 显示最慢10个测试
pytest --durations=0   # 显示所有测试耗时
```

## 🧪 测试模式

### 1. 单元测试模式
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_service_method(service_fixture):
    """测试单个服务方法"""
    result = await service_fixture.method()
    assert result == expected_value
```

### 2. 集成测试模式
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    """测试API端点"""
    response = await async_client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

### 3. 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    ("BTC/USDT", "crypto"),
    ("AAPL", "stock"),
    ("EUR/USD", "forex"),
])
def test_market_type(input, expected):
    result = get_market_type(input)
    assert result == expected
```

## 🔧 Fixtures 使用

### 常用Fixtures
```python
# 测试配置
def test_with_settings(test_settings):
    assert test_settings.DEBUG == True

# 数据库会话
async def test_with_db(test_db_session):
    # 使用测试数据库
    pass

# 模拟数据
def test_with_sample_data(sample_kline_data):
    assert len(sample_kline_data) > 0
```

### 自定义Fixture
```python
@pytest.fixture
def custom_data():
    """创建自定义测试数据"""
    data = {"key": "value"}
    yield data
    # 清理代码（如果需要）
```

## ⚡ 性能测试

```python
import pytest
import time

@pytest.mark.slow
def test_performance():
    """性能测试"""
    start = time.time()
    # 执行操作
    result = expensive_operation()
    duration = time.time() - start
    assert duration < 1.0  # 应该在1秒内完成
```

## 🐛 调试技巧

### 1. 使用 --pdb
```bash
pytest --pdb tests/test_file.py
# 失败时自动进入调试器
```

### 2. 使用 print
```bash
pytest -s tests/test_file.py
# 显示所有print输出
```

### 3. 使用 breakpoint()
```python
def test_something():
    result = function_to_test()
    breakpoint()  # 在这里暂停
    assert result == expected
```

### 4. 查看详细错误
```bash
pytest --tb=long tests/test_file.py
# --tb=short: 简短回溯
# --tb=line: 单行回溯
# --tb=native: Python标准回溯
```

## 📊 覆盖率目标

```
配置文件覆盖率目标:
- config.py: 100% ✅
- models/*: 95%+ ✅
- services/*: 70%+ 🎯
- api/*: 80%+ 🎯
- 整体: 80%+ 🎯

当前状态:
- 基础模块: 50% ✅
- 服务层: 15-38% 🔄
- 总体: 32-50% 🔄
```

## 🔍 故障排查

### 问题1: 导入错误
```bash
# 检查模块是否存在
python -c "from backend.services.data_service import DataService"

# 如果失败，检查PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 问题2: 异步测试失败
```bash
# 确保安装了pytest-asyncio
pip install pytest-asyncio

# 检查pytest.ini配置
# 应该有: asyncio_mode = auto
```

### 问题3: 覆盖率不准确
```bash
# 清理缓存
rm -rf .pytest_cache htmlcov .coverage

# 重新运行
pytest --cov=backend --cov-report=html
```

## 📝 编写测试检查清单

- [ ] 测试名称清晰描述功能
- [ ] 使用AAA模式（Arrange-Act-Assert）
- [ ] 测试独立，不依赖其他测试
- [ ] 包含正常和异常情况
- [ ] 边界条件已测试
- [ ] 使用合适的断言
- [ ] Mock外部依赖
- [ ] 添加文档字符串
- [ ] 测试通过
- [ ] 覆盖率提升

## 🎓 最佳实践

1. **一个测试一个断言**: 保持测试简单
2. **有意义的命名**: `test_should_return_error_when_invalid_input`
3. **使用fixtures**: 复用测试数据
4. **Mock外部服务**: 不依赖真实API
5. **快速执行**: 单元测试应该快速
6. **定期运行**: 每次提交前运行
7. **保持同步**: 代码变更时更新测试

## 🚨 常见错误

### ❌ 不好的测试
```python
def test_everything():
    # 测试太多东西
    assert service.method1() == 1
    assert service.method2() == 2
    assert service.method3() == 3
```

### ✅ 好的测试
```python
def test_method1_returns_correct_value():
    """测试method1在正常情况下返回正确值"""
    result = service.method1()
    assert result == 1

def test_method1_raises_error_when_invalid():
    """测试method1在无效输入时抛出异常"""
    with pytest.raises(ValueError):
        service.method1(invalid_input)
```

## 📚 相关文档

- [TESTING_REPORT.md](./TESTING_REPORT.md) - 详细测试报告
- [TESTING_SUMMARY.md](./TESTING_SUMMARY.md) - 实施总结
- [pytest.ini](./pytest.ini) - Pytest配置
- [conftest.py](./tests/conftest.py) - 全局fixtures

## 🆘 获取帮助

```bash
# Pytest帮助
pytest --help

# 查看可用fixtures
pytest --fixtures

# 查看可用标记
pytest --markers

# 查看测试收集（不运行）
pytest --collect-only
```

---

**快速联系**: 查看 TESTING_SUMMARY.md 获取完整指南  
**HTML报告**: `htmlcov/index.html`  
**配置文件**: `pytest.ini`
