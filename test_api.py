import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health_endpoint():
    """测试健康检查端点"""
    try:
        # 健康检查端点在根路径，不在API版本路径下
        response = requests.get("http://localhost:8000/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_market_data_endpoints():
    """测试市场数据相关端点"""
    endpoints = [
        "/market/exchanges",
        "/market/symbols?exchange=binance",
        "/market/tickers?exchange=binance&symbol=BTC/USDT"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  响应: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"  错误: {response.text}")
        except Exception as e:
            print(f"{endpoint}: 失败 - {e}")

def test_user_endpoints():
    """测试用户相关端点"""
    endpoints = [
        "/users/register",
        "/users/login"
    ]
    
    for endpoint in endpoints:
        try:
            # 测试端点是否存在
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint} (GET): {response.status_code}")
            
            # 尝试POST请求
            if endpoint == "/users/register":
                test_data = {
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
                response = requests.post(f"{BASE_URL}{endpoint}", json=test_data)
                print(f"{endpoint} (POST): {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: 失败 - {e}")

if __name__ == "__main__":
    print("开始测试API端点...")
    print("=" * 50)
    
    if test_health_endpoint():
        print("\n测试市场数据端点:")
        print("-" * 30)
        test_market_data_endpoints()
        
        print("\n测试用户端点:")
        print("-" * 30)
        test_user_endpoints()
    else:
        print("后端服务未运行，请先启动后端服务")
