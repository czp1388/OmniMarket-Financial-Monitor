"""
牛熊证风险分析服务
提供专业的牛熊证风险分析功能，包括触回收概率计算、时间价值衰减估算等
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    EXTREME = "极高风险"


class WarrantsRiskAnalysisService:
    """牛熊证风险分析服务"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.last_analysis_time = {}
        
    def calculate_knock_out_probability(self, 
                                      current_price: float,
                                      knock_out_price: float,
                                      volatility: float,
                                      time_to_expiry: int,
                                      warrant_type: str) -> float:
        """
        计算触回收概率
        使用Black-Scholes模型计算触回收概率
        
        Args:
            current_price: 当前正股价格
            knock_out_price: 回收价
            volatility: 年化波动率
            time_to_expiry: 剩余到期天数
            warrant_type: 牛熊证类型 ('BULL' or 'BEAR')
            
        Returns:
            float: 触回收概率 (0-1)
        """
        try:
            # 转换为年化时间
            time_years = time_to_expiry / 365.0
            
            # 计算距离回收价的距离
            if warrant_type == 'BULL':
                # 牛证：当正股价格下跌到回收价时触发
                distance = (current_price - knock_out_price) / current_price
                strike_price = knock_out_price
            else:  # BEAR
                # 熊证：当正股价格上涨到回收价时触发
                distance = (knock_out_price - current_price) / current_price
                strike_price = knock_out_price
                
            if distance <= 0:
                return 1.0  # 已经触发回收
                
            # 使用Black-Scholes模型计算触回收概率
            d2 = (math.log(current_price / strike_price) + 
                  (-0.5 * volatility**2) * time_years) / (volatility * math.sqrt(time_years))
            
            # 计算触回收概率 (1 - N(d2))
            from scipy.stats import norm
            knock_out_prob = 1 - norm.cdf(d2)
            
            # 确保概率在合理范围内
            knock_out_prob = max(0.0, min(1.0, knock_out_prob))
            
            logger.info(f"触回收概率计算: 当前价={current_price}, 回收价={knock_out_price}, "
                       f"波动率={volatility}, 剩余天数={time_to_expiry}, 类型={warrant_type}, "
                       f"概率={knock_out_prob:.4f}")
            
            return knock_out_prob
            
        except Exception as e:
            logger.error(f"计算触回收概率失败: {str(e)}")
            # 返回基于距离的简单估计
            if warrant_type == 'BULL':
                distance_ratio = (current_price - knock_out_price) / current_price
            else:
                distance_ratio = (knock_out_price - current_price) / current_price
                
            if distance_ratio <= 0.01:  # 1%以内
                return 0.8
            elif distance_ratio <= 0.03:  # 3%以内
                return 0.5
            elif distance_ratio <= 0.05:  # 5%以内
                return 0.3
            else:
                return 0.1
    
    def calculate_time_decay_estimate(self,
                                    current_price: float,
                                    strike_price: float,
                                    time_to_expiry: int,
                                    interest_rate: float = 0.03,
                                    volatility: float = 0.3) -> Dict[str, float]:
        """
        计算时间价值衰减估算
        
        Args:
            current_price: 当前正股价格
            strike_price: 行使价
            time_to_expiry: 剩余到期天数
            interest_rate: 无风险利率
            volatility: 年化波动率
            
        Returns:
            Dict: 包含不同时间点的价值估算
        """
        try:
            time_years = time_to_expiry / 365.0
            
            # 计算Theta（时间衰减）
            # 使用Black-Scholes模型的Theta近似
            d1 = (math.log(current_price / strike_price) + 
                  (interest_rate + 0.5 * volatility**2) * time_years) / (volatility * math.sqrt(time_years))
            d2 = d1 - volatility * math.sqrt(time_years)
            
            from scipy.stats import norm
            theta = (-current_price * norm.pdf(d1) * volatility / (2 * math.sqrt(time_years)) -
                     interest_rate * strike_price * math.exp(-interest_rate * time_years) * norm.cdf(d2))
            
            # 转换为每日衰减
            daily_decay = theta / 365.0
            
            # 计算不同时间点的价值衰减
            decay_estimates = {
                'daily_decay': abs(daily_decay),
                'weekly_decay': abs(daily_decay * 7),
                'monthly_decay': abs(daily_decay * 30),
                'current_time_value': current_price * 0.1,  # 简单估算
                'decay_percentage': min(1.0, abs(daily_decay) / (current_price * 0.1) * 100)
            }
            
            logger.info(f"时间价值衰减计算: 当前价={current_price}, 行使价={strike_price}, "
                       f"剩余天数={time_to_expiry}, 每日衰减={daily_decay:.6f}")
            
            return decay_estimates
            
        except Exception as e:
            logger.error(f"计算时间价值衰减失败: {str(e)}")
            # 返回基于时间的简单估计
            base_decay = current_price * 0.0005  # 每日0.05%的基础衰减
            return {
                'daily_decay': base_decay,
                'weekly_decay': base_decay * 7,
                'monthly_decay': base_decay * 30,
                'current_time_value': current_price * 0.1,
                'decay_percentage': 0.05
            }
    
    def analyze_leverage_effect(self,
                              warrant_price: float,
                              underlying_price: float,
                              conversion_ratio: float,
                              warrant_type: str) -> Dict[str, float]:
        """
        分析杠杆效应
        
        Args:
            warrant_price: 牛熊证价格
            underlying_price: 正股价格
            conversion_ratio: 兑换比率
            warrant_type: 牛熊证类型
            
        Returns:
            Dict: 杠杆效应分析结果
        """
        try:
            # 计算有效杠杆
            effective_leverage = abs((underlying_price / warrant_price) * conversion_ratio)
            
            # 计算理论杠杆
            theoretical_leverage = abs(underlying_price / (warrant_price * conversion_ratio))
            
            # 计算对冲比率
            hedge_ratio = 1.0 / conversion_ratio if conversion_ratio > 0 else 0
            
            # 评估杠杆风险
            if effective_leverage > 20:
                leverage_risk = "极高"
            elif effective_leverage > 15:
                leverage_risk = "高"
            elif effective_leverage > 10:
                leverage_risk = "中"
            else:
                leverage_risk = "低"
                
            leverage_analysis = {
                'effective_leverage': effective_leverage,
                'theoretical_leverage': theoretical_leverage,
                'hedge_ratio': hedge_ratio,
                'leverage_risk': leverage_risk,
                'price_sensitivity': effective_leverage * 0.01  # 价格敏感度
            }
            
            logger.info(f"杠杆效应分析: 牛熊证价={warrant_price}, 正股价={underlying_price}, "
                       f"兑换比率={conversion_ratio}, 有效杠杆={effective_leverage:.2f}")
            
            return leverage_analysis
            
        except Exception as e:
            logger.error(f"分析杠杆效应失败: {str(e)}")
            return {
                'effective_leverage': 0,
                'theoretical_leverage': 0,
                'hedge_ratio': 0,
                'leverage_risk': "未知",
                'price_sensitivity': 0
            }
    
    def calculate_safety_margin(self,
                              current_price: float,
                              knock_out_price: float,
                              warrant_type: str,
                              volatility: float) -> Dict[str, float]:
        """
        计算安全边际
        
        Args:
            current_price: 当前正股价格
            knock_out_price: 回收价
            warrant_type: 牛熊证类型
            volatility: 波动率
            
        Returns:
            Dict: 安全边际分析结果
        """
        try:
            # 计算距离回收价的百分比距离
            if warrant_type == 'BULL':
                distance = (current_price - knock_out_price) / current_price * 100
                safe_distance = volatility * 2  # 2倍波动率作为安全距离
            else:  # BEAR
                distance = (knock_out_price - current_price) / current_price * 100
                safe_distance = volatility * 2
                
            # 计算安全边际比率
            safety_margin_ratio = distance / safe_distance if safe_distance > 0 else 0
            
            # 评估安全等级
            if safety_margin_ratio >= 2.0:
                safety_level = "很高"
            elif safety_margin_ratio >= 1.5:
                safety_level = "高"
            elif safety_margin_ratio >= 1.0:
                safety_level = "中等"
            elif safety_margin_ratio >= 0.5:
                safety_level = "低"
            else:
                safety_level = "极低"
                
            margin_analysis = {
                'distance_to_knock_out': distance,
                'safe_distance_required': safe_distance,
                'safety_margin_ratio': safety_margin_ratio,
                'safety_level': safety_level,
                'is_safe': safety_margin_ratio >= 1.0
            }
            
            logger.info(f"安全边际计算: 当前价={current_price}, 回收价={knock_out_price}, "
                       f"类型={warrant_type}, 安全边际比率={safety_margin_ratio:.2f}")
            
            return margin_analysis
            
        except Exception as e:
            logger.error(f"计算安全边际失败: {str(e)}")
            return {
                'distance_to_knock_out': 0,
                'safe_distance_required': 0,
                'safety_margin_ratio': 0,
                'safety_level': "未知",
                'is_safe': False
            }
    
    def comprehensive_risk_analysis(self,
                                  warrant_data: Dict) -> Dict:
        """
        综合风险分析
        
        Args:
            warrant_data: 牛熊证数据
            
        Returns:
            Dict: 综合风险分析结果
        """
        try:
            # 提取必要数据
            current_price = warrant_data.get('current_price', 0)
            knock_out_price = warrant_data.get('knock_out_price', 0)
            strike_price = warrant_data.get('strike_price', 0)
            warrant_price = warrant_data.get('warrant_price', 0)
            conversion_ratio = warrant_data.get('conversion_ratio', 1)
            time_to_expiry = warrant_data.get('time_to_expiry', 30)
            warrant_type = warrant_data.get('warrant_type', 'BULL')
            volatility = warrant_data.get('volatility', 0.3)
            
            # 执行各项分析
            knock_out_prob = self.calculate_knock_out_probability(
                current_price, knock_out_price, volatility, time_to_expiry, warrant_type
            )
            
            time_decay = self.calculate_time_decay_estimate(
                current_price, strike_price, time_to_expiry
            )
            
            leverage_analysis = self.analyze_leverage_effect(
                warrant_price, current_price, conversion_ratio, warrant_type
            )
            
            safety_margin = self.calculate_safety_margin(
                current_price, knock_out_price, warrant_type, volatility
            )
            
            # 综合风险评估
            overall_risk_score = self._calculate_overall_risk_score(
                knock_out_prob, 
                leverage_analysis['effective_leverage'],
                safety_margin['safety_margin_ratio'],
                time_decay['decay_percentage']
            )
            
            # 生成风险等级
            risk_level = self._determine_risk_level(overall_risk_score)
            
            # 生成投资建议
            investment_advice = self._generate_investment_advice(risk_level, warrant_type)
            
            comprehensive_analysis = {
                'knock_out_probability': knock_out_prob,
                'time_decay_analysis': time_decay,
                'leverage_analysis': leverage_analysis,
                'safety_margin_analysis': safety_margin,
                'overall_risk_score': overall_risk_score,
                'risk_level': risk_level,
                'investment_advice': investment_advice,
                'analysis_timestamp': datetime.now().isoformat(),
                'warrant_symbol': warrant_data.get('symbol', ''),
                'underlying_symbol': warrant_data.get('underlying_symbol', '')
            }
            
            logger.info(f"综合风险分析完成: {warrant_data.get('symbol', '')}, "
                       f"风险等级={risk_level.value}, 风险评分={overall_risk_score}")
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"综合风险分析失败: {str(e)}")
            return {
                'error': f"风险分析失败: {str(e)}",
                'risk_level': RiskLevel.HIGH,
                'investment_advice': "分析失败，建议谨慎操作"
            }
    
    def _calculate_overall_risk_score(self,
                                    knock_out_prob: float,
                                    effective_leverage: float,
                                    safety_margin_ratio: float,
                                    decay_percentage: float) -> float:
        """计算综合风险评分"""
        # 权重分配
        weights = {
            'knock_out_prob': 0.4,      # 触回收概率权重最高
            'leverage': 0.3,            # 杠杆效应权重次之
            'safety_margin': 0.2,       # 安全边际权重
            'time_decay': 0.1           # 时间衰减权重最低
        }
        
        # 标准化各项指标 (0-1范围，1表示风险最高)
        knock_out_risk = knock_out_prob  # 已经是0-1范围
        
        leverage_risk = min(1.0, effective_leverage / 20.0)  # 杠杆超过20视为最高风险
        
        safety_risk = max(0.0, 1.0 - safety_margin_ratio)  # 安全边际越低风险越高
        
        decay_risk = min(1.0, decay_percentage / 10.0)  # 每日衰减超过10%视为最高风险
        
        # 计算加权风险评分
        overall_score = (
            knock_out_risk * weights['knock_out_prob'] +
            leverage_risk * weights['leverage'] +
            safety_risk * weights['safety_margin'] +
            decay_risk * weights['time_decay']
        )
        
        return min(1.0, overall_score)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """根据风险评分确定风险等级"""
        if risk_score >= 0.8:
            return RiskLevel.EXTREME
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_investment_advice(self, risk_level: RiskLevel, warrant_type: str) -> str:
        """生成投资建议"""
        base_advice = {
            RiskLevel.LOW: "风险较低，适合稳健投资者",
            RiskLevel.MEDIUM: "风险适中，需要关注市场变化",
            RiskLevel.HIGH: "风险较高，建议谨慎操作",
            RiskLevel.EXTREME: "风险极高，不建议投资"
        }
        
        type_advice = {
            'BULL': "牛证：看涨正股，注意下跌风险",
            'BEAR': "熊证：看跌正股，注意上涨风险"
        }
        
        return f"{base_advice[risk_level]} | {type_advice.get(warrant_type, '')}"
    
    async def analyze_warrants_batch(self, warrants_list: List[Dict]) -> List[Dict]:
        """
        批量分析牛熊证
        
        Args:
            warrants_list: 牛熊证数据列表
            
        Returns:
            List[Dict]: 分析结果列表
        """
        results = []
        
        for warrant_data in warrants_list:
            try:
                analysis_result = self.comprehensive_risk_analysis(warrant_data)
                results.append(analysis_result)
            except Exception as e:
                logger.error(f"分析牛熊证失败 {warrant_data.get('symbol', '')}: {str(e)}")
                results.append({
                    'warrant_symbol': warrant_data.get('symbol', ''),
                    'error': str(e),
                    'risk_level': RiskLevel.HIGH,
                    'investment_advice': "分析失败"
                })
        
        return results
    
    def get_risk_summary(self, analysis_results: List[Dict]) -> Dict:
        """
        获取风险汇总统计
        
        Args:
            analysis_results: 风险分析结果列表
            
        Returns:
            Dict: 风险汇总统计
        """
        try:
            total_count = len(analysis_results)
            risk_counts = {
                'EXTREME': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            }
            
            total_risk_score = 0
            valid_results = 0
            
            for result in analysis_results:
                if 'risk_level' in result and 'overall_risk_score' in result:
                    risk_level = result['risk_level']
                    if isinstance(risk_level, RiskLevel):
                        risk_counts[risk_level.name] += 1
                    else:
                        # 如果是字符串，尝试转换
                        try:
                            risk_level_enum = RiskLevel[risk_level]
                            risk_counts[risk_level_enum.name] += 1
                        except:
                            risk_counts['HIGH'] += 1
                    
                    total_risk_score += result['overall_risk_score']
                    valid_results += 1
            
            avg_risk_score = total_risk_score / valid_results if valid_results > 0 else 0
            
            summary = {
                'total_warrants': total_count,
                'risk_distribution': risk_counts,
                'average_risk_score': avg_risk_score,
                'high_risk_count': risk_counts['HIGH'] + risk_counts['EXTREME'],
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"生成风险汇总失败: {str(e)}")
            return {
                'total_warrants': len(analysis_results),
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }


# 全局风险分析服务实例
warrants_risk_analysis_service = WarrantsRiskAnalysisService()
