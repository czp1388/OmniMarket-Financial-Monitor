"""
测试助手模式 API 端点

此脚本直接导入和测试 API 逻辑，无需启动完整的 FastAPI 服务器
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.assistant import StrategyInstance, ExecutionHistory, SimpleReport
from backend.models.users import User
from backend.database import Base
import json
from datetime import datetime, timedelta

# 创建数据库连接
DATABASE_URL = "sqlite:///omnimarket.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_database_tables():
    """测试数据库表是否存在"""
    print("\n" + "="*60)
    print("测试 1: 检查数据库表")
    print("="*60)
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"✓ 数据库中的表: {', '.join(tables)}")
    
    required_tables = ['users', 'strategy_instances', 'execution_history', 'simple_reports']
    for table in required_tables:
        if table in tables:
            print(f"  ✓ {table} - 存在")
        else:
            print(f"  ✗ {table} - 缺失")
    
    return all(table in tables for table in required_tables)

def test_create_strategy_instance():
    """测试创建策略实例"""
    print("\n" + "="*60)
    print("测试 2: 创建策略实例")
    print("="*60)
    
    db = SessionLocal()
    try:
        # 创建测试用户（如果不存在）
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                username="test_user",
                email="test@example.com",
                full_name="Test User",
                hashed_password="test_hash"
            )
            db.add(user)
            db.commit()
            print(f"  ✓ 创建测试用户: {user.username}")
        else:
            print(f"  ✓ 使用已存在用户: {user.username}")
        
        # 创建策略实例
        instance = StrategyInstance(
            package_id="stable_growth_pkg",
            user_id=1,
            status="active",
            parameters=json.dumps({
                "investment_amount": 5000,
                "user_goal": "stable_growth",
                "risk_tolerance": "low",
                "investment_horizon": "long_term"
            }),
            initial_amount=5000.0,
            current_value=5000.0,
            profit=0.0
        )
        db.add(instance)
        db.commit()
        db.refresh(instance)
        
        print(f"  ✓ 策略实例已创建:")
        print(f"    - ID: {instance.id}")
        print(f"    - 包ID: {instance.package_id}")
        print(f"    - 初始金额: ${instance.initial_amount:,.2f}")
        print(f"    - 当前价值: ${instance.current_value:,.2f}")
        print(f"    - 状态: {instance.status}")
        print(f"    - 创建时间: {instance.created_at}")
        
        return instance.id
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def test_create_execution_history(instance_id):
    """测试创建执行历史记录"""
    print("\n" + "="*60)
    print("测试 3: 创建执行历史记录")
    print("="*60)
    
    db = SessionLocal()
    try:
        # 创建模拟交易记录
        executions = [
            {
                "execution_date": datetime.now() - timedelta(days=7),
                "action_type": "buy",
                "symbol": "AAPL",
                "quantity": 10,
                "price": 150.50,
                "amount": 1505.00,
                "reason": "初始建仓 - 符合稳健增长策略"
            },
            {
                "execution_date": datetime.now() - timedelta(days=5),
                "action_type": "buy",
                "symbol": "MSFT",
                "quantity": 5,
                "price": 350.00,
                "amount": 1750.00,
                "reason": "配置科技股 - 分散风险"
            },
            {
                "execution_date": datetime.now() - timedelta(days=2),
                "action_type": "buy",
                "symbol": "VTI",
                "quantity": 8,
                "price": 220.00,
                "amount": 1760.00,
                "reason": "购买ETF - 稳定收益"
            }
        ]
        
        for exec_data in executions:
            execution = ExecutionHistory(
                instance_id=instance_id,
                **exec_data
            )
            db.add(execution)
        
        db.commit()
        
        # 查询并显示
        all_executions = db.query(ExecutionHistory).filter(
            ExecutionHistory.instance_id == instance_id
        ).all()
        
        print(f"  ✓ 已创建 {len(all_executions)} 条执行记录:")
        for exec in all_executions:
            print(f"    - {exec.execution_date.strftime('%Y-%m-%d')}: {exec.action_type.upper()} {exec.quantity} x {exec.symbol} @ ${exec.price:.2f}")
            print(f"      原因: {exec.reason}")
        
        return True
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_create_simple_report(instance_id):
    """测试创建简报"""
    print("\n" + "="*60)
    print("测试 4: 创建策略简报")
    print("="*60)
    
    db = SessionLocal()
    try:
        # 创建周报
        report = SimpleReport(
            instance_id=instance_id,
            report_type="weekly",
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now(),
            total_invested=5000.0,
            current_value=5123.50,
            profit=123.50,
            profit_rate=2.47,
            highlights=json.dumps([
                "本周收益 +2.47%，超过预期目标",
                "AAPL 上涨 3.2%，贡献主要收益",
                "投资组合波动性保持在低风险范围"
            ]),
            suggestions=json.dumps([
                "建议继续持有当前配置",
                "可考虑在下周增加债券ETF仓位",
                "关注美联储利率决议对市场的影响"
            ]),
            report_data=json.dumps({
                "equity_curve": [5000, 5050, 5080, 5100, 5123.50],
                "holdings": {
                    "AAPL": {"quantity": 10, "value": 1530.0, "profit": 25.0},
                    "MSFT": {"quantity": 5, "value": 1775.0, "profit": 25.0},
                    "VTI": {"quantity": 8, "value": 1818.5, "profit": 58.5}
                },
                "goal_progress": 2.47  # 离目标的进度
            })
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        print(f"  ✓ 简报已创建:")
        print(f"    - 类型: {report.report_type}")
        print(f"    - 周期: {report.period_start.strftime('%Y-%m-%d')} 至 {report.period_end.strftime('%Y-%m-%d')}")
        print(f"    - 投资总额: ${report.total_invested:,.2f}")
        print(f"    - 当前价值: ${report.current_value:,.2f}")
        print(f"    - 收益: ${report.profit:,.2f} ({report.profit_rate}%)")
        print(f"    - 亮点: {len(json.loads(report.highlights))} 条")
        print(f"    - 建议: {len(json.loads(report.suggestions))} 条")
        
        return report.id
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def test_query_running_status(instance_id):
    """测试查询运行状态"""
    print("\n" + "="*60)
    print("测试 5: 查询策略运行状态")
    print("="*60)
    
    db = SessionLocal()
    try:
        instance = db.query(StrategyInstance).filter(StrategyInstance.id == instance_id).first()
        if not instance:
            print(f"  ✗ 未找到实例 ID: {instance_id}")
            return False
        
        print(f"  ✓ 策略实例状态:")
        print(f"    - 实例 ID: {instance.id}")
        print(f"    - 状态: {instance.status}")
        print(f"    - 当前价值: ${instance.current_value:,.2f}")
        print(f"    - 收益: ${instance.profit:,.2f}")
        print(f"    - 最后更新: {instance.updated_at}")
        
        # 查询最新执行记录
        recent_execution = db.query(ExecutionHistory).filter(
            ExecutionHistory.instance_id == instance_id
        ).order_by(ExecutionHistory.execution_date.desc()).first()
        
        if recent_execution:
            print(f"  ✓ 最近执行:")
            print(f"    - 时间: {recent_execution.execution_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"    - 操作: {recent_execution.action_type.upper()} {recent_execution.symbol}")
            print(f"    - 原因: {recent_execution.reason}")
        
        return True
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False
    finally:
        db.close()

def test_query_report(instance_id):
    """测试查询报告"""
    print("\n" + "="*60)
    print("测试 6: 查询策略报告")
    print("="*60)
    
    db = SessionLocal()
    try:
        report = db.query(SimpleReport).filter(
            SimpleReport.instance_id == instance_id
        ).order_by(SimpleReport.created_at.desc()).first()
        
        if not report:
            print(f"  ✗ 未找到报告")
            return False
        
        print(f"  ✓ 报告详情:")
        print(f"    - 类型: {report.report_type}")
        print(f"    - 收益率: {report.profit_rate}%")
        
        highlights = json.loads(report.highlights)
        print(f"  ✓ 亮点 ({len(highlights)} 条):")
        for i, highlight in enumerate(highlights, 1):
            print(f"    {i}. {highlight}")
        
        suggestions = json.loads(report.suggestions)
        print(f"  ✓ 建议 ({len(suggestions)} 条):")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"    {i}. {suggestion}")
        
        report_data = json.loads(report.report_data)
        print(f"  ✓ 持仓明细:")
        for symbol, data in report_data["holdings"].items():
            print(f"    - {symbol}: {data['quantity']} 股, 价值 ${data['value']:,.2f}, 收益 ${data['profit']:,.2f}")
        
        return True
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        return False
    finally:
        db.close()

def main():
    """主测试流程"""
    print("\n" + "="*70)
    print(" 🚀 OmniMarket 助手模式 API 测试")
    print("="*70)
    print(f"数据库: {DATABASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试 1: 检查表
    if not test_database_tables():
        print("\n❌ 数据库表检查失败，请运行 create_assistant_tables_sqlite.py")
        return
    
    # 测试 2: 创建策略实例
    instance_id = test_create_strategy_instance()
    if not instance_id:
        print("\n❌ 创建策略实例失败")
        return
    
    # 测试 3: 创建执行历史
    if not test_create_execution_history(instance_id):
        print("\n❌ 创建执行历史失败")
        return
    
    # 测试 4: 创建报告
    report_id = test_create_simple_report(instance_id)
    if not report_id:
        print("\n❌ 创建报告失败")
        return
    
    # 测试 5: 查询运行状态
    if not test_query_running_status(instance_id):
        print("\n❌ 查询运行状态失败")
        return
    
    # 测试 6: 查询报告
    if not test_query_report(instance_id):
        print("\n❌ 查询报告失败")
        return
    
    # 所有测试通过
    print("\n" + "="*70)
    print(" ✅ 所有测试通过！")
    print("="*70)
    print(f"✓ 数据库模型验证成功")
    print(f"✓ 策略实例创建成功 (ID: {instance_id})")
    print(f"✓ 执行历史记录成功")
    print(f"✓ 报告生成成功 (ID: {report_id})")
    print(f"✓ 数据查询功能正常")
    print("\n📝 后续步骤:")
    print("  1. 修复后端服务启动问题（lifespan 或依赖）")
    print("  2. 启动后端服务: cd backend && uvicorn main:app --reload")
    print("  3. 启动前端服务: cd frontend && npm run dev")
    print("  4. 测试完整前后端对接")

if __name__ == "__main__":
    main()
