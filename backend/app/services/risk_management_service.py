# 风险管理服务
import logging
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class RiskMetric(Enum):
    DRAWDOWN = "drawdown"           # 回撤
    VOLATILITY = "volatility"       # 波动率
    VAR = "var"                     # 风险价值
    SHARPE_RATIO = "sharpe_ratio"  # 夏普比率
    MAX_LOSS = "max_loss"           # 最大亏损

class RiskManagementService:
    """风险管理服务"""
    
    def __init__(self):
        self.portfolio_data = {}
        self.risk_rules = {}
        self.risk_history = []
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """初始化风险管理服务"""
        try:
            logger.info("🔄 初始化风险管理服务...")
            
            # 加载默认风险规则
            await self._load_default_rules()
            
            self.is_initialized = True
            logger.info("✅ 风险管理服务初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"风险管理服务初始化失败: {e}")
            return False
    
    async def _load_default_rules(self):
        """加载默认风险规则"""
        self.risk_rules = {
            "max_drawdown": {
                "metric": RiskMetric.DRAWDOWN,
                "threshold": 0.10,  # 10%最大回撤
                "level": RiskLevel.HIGH,
                "enabled": True
            },
            "daily_loss_limit": {
                "metric": RiskMetric.MAX_LOSS, 
                "threshold": 0.05,  # 5%单日最大亏损
                "level": RiskLevel.CRITICAL,
                "enabled": True
            },
            "position_concentration": {
                "metric": "concentration",
                "threshold": 0.20,  # 单个仓位不超过20%
                "level": RiskLevel.MEDIUM,
                "enabled": True
            }
        }
    
    async def calculate_portfolio_risk(self, portfolio: Dict) -> Dict:
        """计算投资组合风险"""
        try:
            positions = portfolio.get("positions", [])
            total_value = portfolio.get("total_value", 0)
            
            if total_value <= 0:
                return {"error": "投资组合价值无效"}
            
            risk_metrics = {}
            
            # 计算回撤
            drawdown = await self._calculate_drawdown(portfolio)
            risk_metrics["drawdown"] = drawdown
            
            # 计算波动率
            volatility = await self._calculate_volatility(portfolio)
            risk_metrics["volatility"] = volatility
            
            # 计算风险价值(VaR)
            var = await self._calculate_var(portfolio)
            risk_metrics["var"] = var
            
            # 计算夏普比率
            sharpe_ratio = await self._calculate_sharpe_ratio(portfolio)
            risk_metrics["sharpe_ratio"] = sharpe_ratio
            
            # 计算仓位集中度
            concentration = await self._calculate_concentration(positions, total_value)
            risk_metrics["concentration"] = concentration
            
            # 评估风险等级
            risk_level = await self._assess_risk_level(risk_metrics)
            risk_metrics["risk_level"] = risk_level
            
            # 检查风险规则
            risk_alerts = await self._check_risk_rules(risk_metrics)
            risk_metrics["alerts"] = risk_alerts
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"计算投资组合风险失败: {e}")
            return {"error": str(e)}
    
    async def _calculate_drawdown(self, portfolio: Dict) -> float:
        """计算最大回撤"""
        try:
            historical_values = portfolio.get("historical_values", [])
            if len(historical_values) < 2:
                return 0.0
            
            peak = max(historical_values)
            current = historical_values[-1] if historical_values else 0
            drawdown = (peak - current) / peak if peak > 0 else 0.0
            
            return round(drawdown, 4)
            
        except Exception as e:
            logger.error(f"计算回撤失败: {e}")
            return 0.0
    
    async def _calculate_volatility(self, portfolio: Dict) -> float:
        """计算波动率"""
        try:
            returns = portfolio.get("returns", [])
            if len(returns) < 2:
                return 0.0
            
            volatility = pd.Series(returns).std()
            return round(volatility, 4)
            
        except Exception as e:
            logger.error(f"计算波动率失败: {e}")
            return 0.0
    
    async def _calculate_var(self, portfolio: Dict, confidence: float = 0.95) -> float:
        """计算风险价值(VaR)"""
        try:
            returns = portfolio.get("returns", [])
            if len(returns) < 10:
                return 0.0
            
            series = pd.Series(returns)
            var = series.quantile(1 - confidence)
            return round(var, 4)
            
        except Exception as e:
            logger.error(f"计算VaR失败: {e}")
            return 0.0
    
    async def _calculate_sharpe_ratio(self, portfolio: Dict, risk_free_rate: float = 0.02) -> float:
        """计算夏普比率"""
        try:
            returns = portfolio.get("returns", [])
            if len(returns) < 2:
                return 0.0
            
            series = pd.Series(returns)
            excess_returns = series.mean() - risk_free_rate / 252  # 年化无风险利率
            volatility = series.std()
            
            sharpe = excess_returns / volatility * (252 ** 0.5) if volatility > 0 else 0.0
            return round(sharpe, 4)
            
        except Exception as e:
            logger.error(f"计算夏普比率失败: {e}")
            return 0.0
    
    async def _calculate_concentration(self, positions: List[Dict], total_value: float) -> Dict:
        """计算仓位集中度"""
        try:
            if total_value <= 0:
                return {"max_concentration": 0.0, "top_positions": []}
            
            # 计算每个仓位的权重
            position_weights = []
            for position in positions:
                market_value = position.get("market_value", 0)
                weight = market_value / total_value
                position_weights.append({
                    "symbol": position.get("symbol", ""),
                    "weight": round(weight, 4)
                })
            
            # 按权重排序
            position_weights.sort(key=lambda x: x["weight"], reverse=True)
            
            max_concentration = position_weights[0]["weight"] if position_weights else 0.0
            
            return {
                "max_concentration": max_concentration,
                "top_positions": position_weights[:5]  # 前5大仓位
            }
            
        except Exception as e:
            logger.error(f"计算仓位集中度失败: {e}")
            return {"max_concentration": 0.0, "top_positions": []}
    
    async def _assess_risk_level(self, risk_metrics: Dict) -> RiskLevel:
        """评估风险等级"""
        try:
            drawdown = risk_metrics.get("drawdown", 0)
            volatility = risk_metrics.get("volatility", 0)
            var = risk_metrics.get("var", 0)
            
            risk_score = 0
            
            # 回撤评分
            if drawdown > 0.15:
                risk_score += 3
            elif drawdown > 0.10:
                risk_score += 2
            elif drawdown > 0.05:
                risk_score += 1
            
            # 波动率评分
            if volatility > 0.03:
                risk_score += 2
            elif volatility > 0.02:
                risk_score += 1
            
            # VaR评分
            if var < -0.05:
                risk_score += 3
            elif var < -0.03:
                risk_score += 2
            elif var < -0.01:
                risk_score += 1
            
            # 确定风险等级
            if risk_score >= 5:
                return RiskLevel.CRITICAL
            elif risk_score >= 3:
                return RiskLevel.HIGH
            elif risk_score >= 1:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
                
        except Exception as e:
            logger.error(f"评估风险等级失败: {e}")
            return RiskLevel.MEDIUM
    
    async def _check_risk_rules(self, risk_metrics: Dict) -> List[Dict]:
        """检查风险规则"""
        alerts = []
        
        try:
            for rule_name, rule in self.risk_rules.items():
                if not rule.get("enabled", False):
                    continue
                
                metric = rule["metric"]
                threshold = rule["threshold"]
                level = rule["level"]
                
                current_value = risk_metrics.get(metric.value if hasattr(metric, 'value') else metric, 0)
                
                # 检查是否触发规则
                if self._is_rule_triggered(metric, current_value, threshold):
                    alert = {
                        "rule_name": rule_name,
                        "metric": metric.value if hasattr(metric, 'value') else metric,
                        "current_value": current_value,
                        "threshold": threshold,
                        "level": level.value,
                        "message": self._generate_risk_alert_message(rule_name, current_value, threshold),
                        "triggered_at": datetime.now()
                    }
                    alerts.append(alert)
                    logger.warning(f"🚨 风险预警: {alert['message']}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"检查风险规则失败: {e}")
            return []
    
    def _is_rule_triggered(self, metric: RiskMetric, current_value: float, threshold: float) -> bool:
        """判断规则是否触发"""
        if metric == RiskMetric.DRAWDOWN:
            return current_value > threshold
        elif metric == RiskMetric.MAX_LOSS:
            return current_value < -threshold
        elif metric == "concentration":
            return current_value > threshold
        else:
            return abs(current_value) > threshold
    
    def _generate_risk_alert_message(self, rule_name: str, current_value: float, threshold: float) -> str:
        """生成风险预警消息"""
        messages = {
            "max_drawdown": f"投资组合回撤 {current_value:.2%} 超过阈值 {threshold:.2%}",
            "daily_loss_limit": f"单日亏损 {current_value:.2%} 超过阈值 {threshold:.2%}",
            "position_concentration": f"仓位集中度 {current_value:.2%} 超过阈值 {threshold:.2%}"
        }
        return messages.get(rule_name, f"风险规则 {rule_name} 触发")
    
    async def add_risk_rule(self, rule: Dict) -> bool:
        """添加风险规则"""
        try:
            rule_name = rule.get("name")
            if rule_name:
                self.risk_rules[rule_name] = rule
                logger.info(f"✅ 添加风险规则: {rule_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"添加风险规则失败: {e}")
            return False
    
    async def get_risk_report(self, portfolio: Dict) -> Dict:
        """生成风险报告"""
        risk_metrics = await self.calculate_portfolio_risk(portfolio)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "portfolio_value": portfolio.get("total_value", 0),
            "risk_metrics": risk_metrics,
            "recommendations": await self._generate_recommendations(risk_metrics)
        }
    
    async def _generate_recommendations(self, risk_metrics: Dict) -> List[str]:
        """生成风险建议"""
        recommendations = []
        risk_level = risk_metrics.get("risk_level")
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "立即减少高风险仓位",
                "增加对冲头寸",
                "考虑部分获利了结"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "降低仓位集中度", 
                "设置止损订单",
                "监控市场波动"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "保持现有仓位但密切监控",
                "准备应对市场波动"
            ])
        else:
            recommendations.append("当前风险可控，继续保持")
        
        return recommendations

# 创建全局风险管理服务实例
risk_management_service = RiskManagementService()
