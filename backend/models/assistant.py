"""
助手模式数据模型 - 策略实例、执行历史、报告
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class StrategyInstance(Base):
    """策略实例表 - 记录用户激活的策略"""
    __tablename__ = "strategy_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String, unique=True, index=True, nullable=False)  # 实例唯一ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 用户ID
    
    # 策略包信息
    package_id = Column(String, nullable=False)  # 策略包ID（如 "stable_growth_low_risk"）
    friendly_name = Column(String, nullable=False)  # 友好名称（如 "稳健增长定投宝"）
    strategy_id = Column(String, nullable=False)  # 底层策略ID（如 "rsi_dca"）
    
    # 用户输入
    user_goal = Column(String, nullable=False)  # 用户目标
    risk_tolerance = Column(String, nullable=False)  # 风险承受度
    investment_amount = Column(Float, nullable=False)  # 投资金额
    investment_horizon = Column(String)  # 投资期限
    
    # 策略参数（JSON存储）
    strategy_parameters = Column(JSON, nullable=False)  # 策略参数
    
    # 运行状态
    status = Column(String, default="active")  # active, paused, stopped, completed
    auto_execute = Column(Boolean, default=False)  # 是否自动执行
    
    # 账户数据
    initial_capital = Column(Float, nullable=False)  # 初始资金
    current_value = Column(Float, default=0)  # 当前账户价值
    total_invested = Column(Float, default=0)  # 累计投入
    total_profit = Column(Float, default=0)  # 累计收益
    profit_rate = Column(Float, default=0)  # 收益率
    
    # 执行统计
    total_executions = Column(Integer, default=0)  # 总执行次数
    successful_executions = Column(Integer, default=0)  # 成功执行次数
    last_execution_time = Column(DateTime)  # 最后执行时间
    next_execution_time = Column(DateTime)  # 下次执行时间
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime)
    
    # 关系
    user = relationship("User", back_populates="strategy_instances")
    executions = relationship("ExecutionHistory", back_populates="instance", cascade="all, delete-orphan")
    reports = relationship("SimpleReport", back_populates="instance", cascade="all, delete-orphan")


class ExecutionHistory(Base):
    """执行历史表 - 记录每次策略执行"""
    __tablename__ = "execution_history"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, unique=True, index=True, nullable=False)
    instance_id = Column(String, ForeignKey("strategy_instances.instance_id"), nullable=False)
    
    # 执行信息
    execution_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_type = Column(String, nullable=False)  # buy, sell, hold, rebalance
    
    # 交易详情
    symbol = Column(String)  # 交易品种
    action = Column(String)  # 具体动作（如 "市价买入"）
    quantity = Column(Float)  # 数量
    price = Column(Float)  # 成交价格
    amount = Column(Float)  # 金额
    
    # 执行结果
    status = Column(String, nullable=False)  # success, failed, skipped
    result_message = Column(Text)  # 执行结果消息
    
    # 账户快照
    account_value_before = Column(Float)  # 执行前账户价值
    account_value_after = Column(Float)  # 执行后账户价值
    cash_balance = Column(Float)  # 现金余额
    position_value = Column(Float)  # 持仓价值
    
    # 白话解释（给用户看的）
    plain_explanation = Column(Text)  # 通俗解释（如 "今天市场便宜，加仓500元"）
    reason = Column(Text)  # 执行原因（如 "RSI显示超卖"）
    
    # 关系
    instance = relationship("StrategyInstance", back_populates="executions")


class SimpleReport(Base):
    """简化报告表 - 周报/月报"""
    __tablename__ = "simple_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True, nullable=False)
    instance_id = Column(String, ForeignKey("strategy_instances.instance_id"), nullable=False)
    
    # 报告元数据
    report_type = Column(String, nullable=False)  # weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # 核心数据
    total_invested = Column(Float, nullable=False)  # 本期投入
    total_return = Column(Float, nullable=False)  # 本期收益
    return_rate = Column(Float, nullable=False)  # 收益率
    account_value = Column(Float, nullable=False)  # 账户价值
    
    # 目标进度
    target_amount = Column(Float)  # 目标金额
    current_progress = Column(Float)  # 当前进度百分比
    
    # 本周亮点（JSON数组）
    highlights = Column(JSON)  # [{title: "...", value: "...", icon: "..."}]
    
    # 下周建议
    next_week_suggestion = Column(Text)  # 白话建议
    next_action_date = Column(DateTime)  # 下次行动日期
    next_action_amount = Column(Float)  # 建议金额
    
    # 数据快照（JSON）
    weekly_data = Column(JSON)  # 周度数据点
    monthly_data = Column(JSON)  # 月度数据点
    
    # 关系
    instance = relationship("StrategyInstance", back_populates="reports")


# 更新 User 模型的关系（需要在 users.py 中添加）
# user = relationship("StrategyInstance", back_populates="user")
