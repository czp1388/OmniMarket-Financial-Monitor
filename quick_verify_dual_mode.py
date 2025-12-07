"""
快速验证 - 直接测试关键功能
"""
import sys
from pathlib import Path

# 添加backend到路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("\n" + "=" * 60)
print("   双模架构快速验证")
print("=" * 60)

# 测试1：意图理解服务
print("\n✅ [1/3] 意图理解服务")
from services.intent_service import intent_service, UserGoal, RiskTolerance

packages = intent_service.get_all_packages()
print(f"   策略包总数: {len(packages)}")

for i, pkg in enumerate(packages, 1):
    print(f"   {i}. {pkg['icon']} {pkg['friendly_name']}")
    print(f"      风险: {pkg['risk_score']}/5 | 收益: {pkg['expected_return']}")

# 测试2：意图翻译
print("\n✅ [2/3] 意图翻译")
translation = intent_service.translate_user_intent(
    user_goal=UserGoal.STABLE_GROWTH,
    risk_tolerance=RiskTolerance.LOW,
    investment_amount=5000
)

print(f"   用户说: '我想稳健增长，不想冒太大风险'")
print(f"   系统翻译为: {translation['package']['friendly_name']}")
print(f"   底层策略: {translation['backtest_request']['strategy_id']}")
print(f"   参数配置: {translation['backtest_request']['parameters']}")

# 测试3：白话解读
print("\n✅ [3/3] 白话解读生成")
explanation = translation['user_explanation']
print(f"   {explanation['what_it_does']}")
print(f"   类比: {explanation['analogy']}")
print(f"   风险: {explanation['risk_level']}")

print("\n" + "=" * 60)
print("   核心功能验证通过！")
print("=" * 60)

print("\n📋 双模对比:")
print("\n专家模式请求:")
print("""
{
  "strategy_id": "rsi_strategy",
  "parameters": {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "stop_loss": 0.05
  }
}
""")

print("\n助手模式请求:")
print("""
{
  "user_goal": "stable_growth",
  "risk_tolerance": "low",
  "investment_amount": 5000
}
""")

print("\n系统自动将助手请求翻译为专家参数！")
print("同一个引擎，两种交互方式 ✅")

print("\n" + "=" * 60)
print("下一步：启动服务测试完整流程")
print("=" * 60)
print("\n1. 后端: cd backend && uvicorn main:app --reload")
print("2. 前端: cd frontend && npm run dev")
print("3. 助手模式: http://localhost:3001/assistant")
print("4. 专家模式: http://localhost:3001/expert")
print("5. API文档: http://localhost:8000/docs (查看 '智能助手' 标签)\n")
