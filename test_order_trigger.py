import requests
import time
import json

# 基础URL
BASE_URL = "http://localhost:8000/api/v1/virtual"

def test_order_trigger():
    """测试订单触发功能"""
    print("=== 订单触发测试 ===\n")
    
    # 1. 创建虚拟账户
    print("1. 创建虚拟账户...")
    create_data = {
        "name": "订单触发测试账户",
        "initial_balance": 100000
    }
    create_response = requests.post(f"{BASE_URL}/accounts", json=create_data)
    print(f"   状态码: {create_response.status_code}")
    create_result = create_response.json()
    print(f"   响应: {create_result}\n")
    
    if 'account_id' not in create_result:
        print("创建账户失败，无法继续测试")
        return
    
    account_id = create_result['account_id']
    
    # 2. 设置初始市场价格
    print("2. 设置初始市场价格...")
    initial_price_data = {
        "symbol": "00700.HK",
        "price": 320.0
    }
    price_response = requests.post(f"{BASE_URL}/market/price", json=initial_price_data)
    print(f"   状态码: {price_response.status_code}")
    print(f"   响应: {price_response.json()}\n")
    
    # 3. 下市价单买入建立持仓
    print("3. 下市价单买入建立持仓...")
    market_order_data = {
        "account_id": account_id,
        "symbol": "00700.HK",
        "quantity": 100,
        "order_type": "market",
        "side": "buy",
        "price": 320.0
    }
    market_response = requests.post(f"{BASE_URL}/orders", json=market_order_data)
    print(f"   状态码: {market_response.status_code}")
    market_result = market_response.json()
    print(f"   响应: {market_result}\n")
    
    # 等待订单执行
    time.sleep(1)
    
    # 4. 获取账户信息查看持仓
    print("4. 获取账户信息查看持仓...")
    account_response = requests.get(f"{BASE_URL}/accounts/{account_id}")
    account_info = account_response.json()
    print(f"   当前持仓: {account_info['positions']}\n")
    
    # 5. 下止损单（卖出止损）
    print("5. 下止损单（卖出止损）...")
    stop_order_data = {
        "account_id": account_id,
        "symbol": "00700.HK",
        "quantity": 50,
        "order_type": "stop",
        "side": "sell",
        "price": 320.0,
        "stop_price": 310.0  # 当价格跌到310时触发
    }
    stop_response = requests.post(f"{BASE_URL}/orders", json=stop_order_data)
    print(f"   状态码: {stop_response.status_code}")
    stop_result = stop_response.json()
    print(f"   响应: {stop_result}\n")
    
    # 6. 下限价单（买入限价）
    print("6. 下买入限价单...")
    limit_buy_data = {
        "account_id": account_id,
        "symbol": "00700.HK",
        "quantity": 50,
        "order_type": "limit",
        "side": "buy",
        "price": 300.0,  # 限价300
        "limit_price": 300.0
    }
    limit_buy_response = requests.post(f"{BASE_URL}/orders", json=limit_buy_data)
    print(f"   状态码: {limit_buy_response.status_code}")
    limit_buy_result = limit_buy_response.json()
    print(f"   响应: {limit_buy_result}\n")
    
    # 7. 检查当前订单状态
    print("7. 检查当前订单状态...")
    orders_response = requests.get(f"{BASE_URL}/orders/{account_id}")
    orders = orders_response.json()
    print("   当前订单:")
    for order in orders:
        print(f"     - {order['order_type']} {order['side']} {order['symbol']} "
              f"{order['quantity']} @ {order.get('price', 'N/A')} "
              f"(状态: {order['status']})")
    print()
    
    # 8. 模拟价格下跌触发止损单
    print("8. 模拟价格下跌触发止损单...")
    # 先设置价格到止损触发点
    trigger_price_data = {
        "symbol": "00700.HK",
        "price": 309.0  # 低于止损价310
    }
    trigger_response = requests.post(f"{BASE_URL}/market/price", json=trigger_price_data)
    print(f"   设置价格到309.0: {trigger_response.json()}\n")
    
    # 等待订单处理
    time.sleep(2)
    
    # 9. 检查止损单是否触发
    print("9. 检查止损单是否触发...")
    orders_after_trigger = requests.get(f"{BASE_URL}/orders/{account_id}").json()
    print("   触发后订单状态:")
    for order in orders_after_trigger:
        print(f"     - {order['order_type']} {order['side']} {order['symbol']} "
              f"{order['quantity']} @ {order.get('price', 'N/A')} "
              f"(状态: {order['status']})")
    print()
    
    # 10. 检查账户持仓变化
    print("10. 检查账户持仓变化...")
    account_after_trigger = requests.get(f"{BASE_URL}/accounts/{account_id}").json()
    print(f"   持仓: {account_after_trigger['positions']}")
    print(f"   可用资金: {account_after_trigger['available_balance']}\n")
    
    # 11. 模拟价格上涨触发限价单
    print("11. 模拟价格上涨触发限价单...")
    # 设置价格到限价单触发点
    limit_trigger_data = {
        "symbol": "00700.HK",
        "price": 299.0  # 低于限价300
    }
    limit_trigger_response = requests.post(f"{BASE_URL}/market/price", json=limit_trigger_data)
    print(f"   设置价格到299.0: {limit_trigger_response.json()}\n")
    
    # 等待订单处理
    time.sleep(2)
    
    # 12. 检查限价单是否触发
    print("12. 检查限价单是否触发...")
    orders_after_limit = requests.get(f"{BASE_URL}/orders/{account_id}").json()
    print("   限价单触发后订单状态:")
    for order in orders_after_limit:
        print(f"     - {order['order_type']} {order['side']} {order['symbol']} "
              f"{order['quantity']} @ {order.get('price', 'N/A')} "
              f"(状态: {order['status']})")
    print()
    
    # 13. 最终账户状态
    print("13. 最终账户状态...")
    final_account = requests.get(f"{BASE_URL}/accounts/{account_id}").json()
    print(f"   总资产: {final_account['total_assets']}")
    print(f"   持仓: {final_account['positions']}")
    print(f"   可用资金: {final_account['available_balance']}\n")
    
    print("=== 订单触发测试完成 ===")

if __name__ == "__main__":
    test_order_trigger()
