from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from backend.services.semi_auto_trading_service import SemiAutoTradingService, TradingSignal

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化服务
trading_service = SemiAutoTradingService()

@router.post("/generate-signals")
async def generate_trading_signals(
    warrant_data_list: List[Dict],
    underlying_data: Dict,
    market_conditions: Dict
):
    """
    生成交易信号
    """
    try:
        signals = trading_service.generate_trading_signals(
            warrant_data_list, underlying_data, market_conditions
        )
        
        # 转换信号为可序列化的字典
        serialized_signals = []
        for signal in signals:
            signal_dict = {
                'warrant_code': signal.warrant_code,
                'signal_type': signal.signal_type.value,
                'strength': signal.strength,
                'confidence': signal.confidence,
                'price': signal.price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'reason': signal.reason,
                'timestamp': signal.timestamp.isoformat()
            }
            serialized_signals.append(signal_dict)
        
        return {
            'success': True,
            'signals': serialized_signals,
            'count': len(serialized_signals)
        }
        
    except Exception as e:
        logger.error(f"生成交易信号失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成交易信号失败: {str(e)}")

@router.post("/validate-trade")
async def validate_trade(signal: Dict, position_size: float):
    """
    验证交易是否符合风控规则
    """
    try:
        # 创建交易信号对象
        trading_signal = TradingSignal(
            warrant_code=signal.get('warrant_code'),
            signal_type=signal.get('signal_type'),
            strength=signal.get('strength', 0.0),
            confidence=signal.get('confidence', 0.0),
            price=signal.get('price', 0.0),
            stop_loss=signal.get('stop_loss'),
            take_profit=signal.get('take_profit'),
            reason=signal.get('reason', '')
        )
        
        validation_result = trading_service.validate_trade(trading_signal, position_size)
        
        return {
            'success': True,
            'validation': validation_result
        }
        
    except Exception as e:
        logger.error(f"交易验证失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"交易验证失败: {str(e)}")

@router.post("/execute-trade")
async def execute_trade(signal: Dict, position_size: float, user_confirmation: bool = False):
    """
    执行交易（需要人工确认）
    """
    try:
        # 创建交易信号对象
        trading_signal = TradingSignal(
            warrant_code=signal.get('warrant_code'),
            signal_type=signal.get('signal_type'),
            strength=signal.get('strength', 0.0),
            confidence=signal.get('confidence', 0.0),
            price=signal.get('price', 0.0),
            stop_loss=signal.get('stop_loss'),
            take_profit=signal.get('take_profit'),
            reason=signal.get('reason', '')
        )
        
        execution_result = trading_service.execute_trade(
            trading_signal, position_size, user_confirmation
        )
        
        return {
            'success': True,
            'execution': execution_result
        }
        
    except Exception as e:
        logger.error(f"交易执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"交易执行失败: {str(e)}")

@router.get("/dashboard")
async def get_trading_dashboard():
    """
    获取交易仪表板数据
    """
    try:
        dashboard_data = trading_service.get_trading_dashboard()
        
        return {
            'success': True,
            'dashboard': dashboard_data
        }
        
    except Exception as e:
        logger.error(f"获取交易仪表板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取交易仪表板失败: {str(e)}")

@router.get("/risk-rules")
async def get_risk_rules():
    """
    获取风险控制规则
    """
    try:
        dashboard_data = trading_service.get_trading_dashboard()
        
        return {
            'success': True,
            'risk_rules': dashboard_data['risk_rules']
        }
        
    except Exception as e:
        logger.error(f"获取风险规则失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取风险规则失败: {str(e)}")
