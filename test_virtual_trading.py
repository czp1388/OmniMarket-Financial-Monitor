import requests

# 基础URL
BASE_URL = "http://localhost:8000/api/v1/virtual"

def test_virtual_trading():
    print("=== 虚拟交易系统测试 ===\n")
    
    # 1. 测试健康检查
    print("1. 测试健康检查...")
    health_response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码: {health_response.status_code}")
    print(f"   响应: {health_response.json()}\n")
    
    # 2. 创建虚拟账户
    print("2. 创建虚拟账户...")
    create_data = {
        "name": "测试交易账户",
        "initial_balance": 100000
    }
    create_response = requests.post(f"{BASE_URL}/accounts", json=create_data)
    print(f"   状态码: {create_response.status_code}")
    create_result = create_response.json()
    print(f"   响应: {create_result}\n")
    
    if create_result.get('success'):
        account_id = create_result['account_id']
        
        # 3. 获取账户列表
        print("3. 获取账户列表...")
        accounts_response = requests.get(f"{BASE_URL}/accounts")
        print(f"   状态码: {accounts_response.status_code}")
        accounts_result = accounts_response.json()
        print(f"   响应: {accounts_result}\n")
        
        # 4. 获取特定账户信息
        print("4. 获取特定账户信息...")
        account_response = requests.get(f"{BASE_URL}/accounts/{account_id}")
        print(f"   状态码: {account_response.status_code}")
        account_result = account_response.json()
        print(f"   响应: {account_result}\n")
        
        # 5. 测试下单功能
        print("5. 测试下单功能...")
        order_data = {
            "account_id": account_id,
            "symbol": "00700.HK",  # 腾讯控股
            "quantity": 100,
            "order_type": "market",
            "side": "buy",
            "price": 320.0
        }
        order_response = requests.post(f"{BASE_URL}/orders", json=order_data)
        print(f"   状态码: {order_response.status_code}")
        order_result = order_response.json()
        print(f"   响应: {order_result}\n")
        
        # 6. 获取订单列表
        print("6. 获取订单列表...")
        orders_response = requests.get(f"{BASE_URL}/orders/{account_id}")
        print(f"   状态码: {orders_response.status_code}")
        orders_result = orders_response.json()
        print(f"   响应: {orders_result}\n")
        
        # 7. 获取持仓列表
        print("7. 获取持仓列表...")
        # 注意：目前虚拟交易API中没有单独的持仓列表端点，持仓信息包含在账户信息中
        # 所以我们重新获取账户信息来查看持仓
        account_response_after = requests.get(f"{BASE_URL}/accounts/{account_id}")
        print(f"   状态码: {account_response_after.status_code}")
        account_result_after = account_response_after.json()
        print(f"   响应: {account_result_after}\n")
        
        # 8. 获取绩效指标
        print("8. 获取绩效指标...")
        performance_response = requests.get(f"{BASE_URL}/performance/{account_id}")
        print(f"   状态码: {performance_response.status_code}")
        performance_result = performance_response.json()
        print(f"   响应: {performance_result}\n")
        
        print("=== 测试完成 ===")
    else:
        print("创建账户失败，无法继续测试")

if __name__ == "__main__":
    test_virtual_trading()
