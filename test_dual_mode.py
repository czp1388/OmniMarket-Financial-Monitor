"""
双模架构验证脚本
验证意图理解服务和助手API模块的正确性
"""
import sys
from pathlib import Path

# 添加backend到路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_intent_service():
    """测试意图理解服务"""
    print("\n[测试1] 意图理解服务")
    print("-" * 50)
    
    try:
        from services.intent_service import intent_service, UserGoal, RiskTolerance
        
        # 测试获取所有策略包
        packages = intent_service.get_all_packages()
        print(f"✅ 策略包数量: {len(packages)}")
        
        for pkg in packages[:3]:  # 显示前3个
            print(f"\n  📦 {pkg['friendly_name']} {pkg['icon']}")
            print(f"     标语: {pkg['tagline']}")
            print(f"     风险评分: {pkg['risk_score']}/5")
            print(f"     预期收益: {pkg['expected_return']}")
        
        # 测试意图翻译
        print("\n\n[测试2] 意图翻译")
        print("-" * 50)
        
        translation = intent_service.translate_user_intent(
            user_goal=UserGoal.STABLE_GROWTH,
            risk_tolerance=RiskTolerance.LOW,
            investment_amount=5000
        )
        
        package = translation['package']
        print(f"✅ 用户目标: 稳健增长 + 低风险")
        print(f"   匹配策略包: {package['friendly_name']}")
        print(f"   底层策略ID: {package['strategy_id']}")
        print(f"   策略参数: {package['parameters']}")
        
        explanation = translation['user_explanation']
        print(f"\n   白话解读:")
        print(f"   - {explanation['what_it_does']}")
        print(f"   - {explanation['analogy']}")
        print(f"   - {explanation['risk_level']}")
        
        print("\n✅ 意图理解服务测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 意图理解服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_assistant_api_structure():
    """测试助手API结构"""
    print("\n\n[测试3] 助手API模块结构")
    print("-" * 50)
    
    try:
        from api.endpoints import assistant_api
        
        # 检查路由对象
        print(f"✅ 助手API模块导入成功")
        print(f"   路由前缀: {assistant_api.router.prefix}")
        print(f"   标签: {assistant_api.router.tags}")
        
        # 检查端点
        routes = assistant_api.router.routes
        print(f"\n   注册的端点数量: {len(routes)}")
        
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods)
                print(f"   - {methods:6} {route.path}")
        
        print("\n✅ 助手API结构测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 助手API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models():
    """测试数据模型"""
    print("\n\n[测试4] 数据模型验证")
    print("-" * 50)
    
    try:
        from api.endpoints.assistant_api import (
            ActivateStrategyRequest,
            StrategyPackageResponse,
            MarketOpportunity
        )
        
        # 测试请求模型
        request = ActivateStrategyRequest(
            user_goal="stable_growth",
            risk_tolerance="low",
            investment_amount=5000.0,
            auto_execute=False
        )
        
        print(f"✅ 请求模型验证通过")
        print(f"   用户目标: {request.user_goal}")
        print(f"   风险偏好: {request.risk_tolerance}")
        print(f"   投资金额: ¥{request.investment_amount}")
        
        print("\n✅ 数据模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("   双模架构验证测试")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    results.append(("意图理解服务", test_intent_service()))
    results.append(("助手API结构", test_assistant_api_structure()))
    results.append(("数据模型", test_models()))
    
    # 汇总结果
    print("\n\n" + "=" * 50)
    print("   测试汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！双模架构已就绪！")
        print("\n下一步:")
        print("  1. 启动后端: uvicorn backend.main:app --reload")
        print("  2. 启动前端: cd frontend && npm run dev")
        print("  3. 访问助手模式: http://localhost:3001/assistant")
        print("  4. 访问专家模式: http://localhost:3001/expert")
        print("  5. API文档: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
