from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from decimal import Decimal
import logging
from pydantic import BaseModel

from backend.services.virtual_trading_engine import (
    virtual_trading_engine, 
    OrderType, 
    OrderSide,
    OrderStatus
)
from backend.services.data_service import data_service
from backend.models.market_data import MarketType

# Pydantic模型用于请求体
class CreateAccountRequest(BaseModel):
    name: str
    initial_balance: float = 100000.0

class PlaceOrderRequest(BaseModel):
    account_id: str
    symbol: str
    order_type: str
    side: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None

logger = logging.getLogger(__name__)

router = APIRouter(tags=["虚拟交易"])

@router.post("/accounts")
async def create_virtual_account(request: CreateAccountRequest):
    """创建虚拟账户"""
    try:
        account_id = await virtual_trading_engine.create_account(
            name=request.name,
            initial_balance=Decimal(str(request.initial_balance))
        )
        return {
            "success": True,
            "account_id": account_id,
            "message": f"虚拟账户 '{request.name}' 创建成功"
        }
    except Exception as e:
        logger.error(f"创建虚拟账户失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建虚拟账户失败: {str(e)}")

@router.get("/accounts/{account_id}")
async def get_virtual_account(account_id: str):
    """获取虚拟账户信息"""
    try:
        account_info = await virtual_trading_engine.get_account_info(account_id)
        if not account_info:
            raise HTTPException(status_code=404, detail="虚拟账户不存在")
        
        return {
            "success": True,
            "account": account_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取虚拟账户信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取虚拟账户信息失败: {str(e)}")

@router.get("/accounts")
async def list_virtual_accounts():
    """列出所有虚拟账户"""
    try:
        # 这里简化处理，实际应该存储账户列表
        accounts = []
        for account_id, account in virtual_trading_engine.accounts.items():
            account_info = await virtual_trading_engine.get_account_info(account_id)
            if account_info:
                accounts.append(account_info)
        
        return {
            "success": True,
            "accounts": accounts
        }
    except Exception as e:
        logger.error(f"列出虚拟账户失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出虚拟账户失败: {str(e)}")

@router.post("/orders")
async def place_virtual_order(request: PlaceOrderRequest):
    """下虚拟订单"""
    try:
        # 验证订单类型
        try:
            order_type_enum = OrderType(order_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的订单类型: {order_type}")
        
        # 验证买卖方向
        try:
            side_enum = OrderSide(side.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的买卖方向: {side}")
        
        # 获取当前市场价格（用于验证）
        if order_type_enum == OrderType.MARKET:
            # 对于市价单，需要获取当前价格
            current_price = await data_service.get_current_price(symbol, MarketType.CRYPTO)
            await virtual_trading_engine.update_market_price(symbol, Decimal(str(current_price)))
        
        # 下订单
        order_id = await virtual_trading_engine.place_order(
            account_id=account_id,
            symbol=symbol,
            order_type=order_type_enum,
            side=side_enum,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(price)) if price else None,
            stop_price=Decimal(str(stop_price)) if stop_price else None
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "message": "虚拟订单提交成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"下虚拟订单失败: {e}")
        raise HTTPException(status_code=500, detail=f"下虚拟订单失败: {str(e)}")

@router.delete("/orders/{order_id}")
async def cancel_virtual_order(order_id: str):
    """取消虚拟订单"""
    try:
        success = await virtual_trading_engine.cancel_order(order_id)
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在或无法取消")
        
        return {
            "success": True,
            "message": "虚拟订单取消成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消虚拟订单失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消虚拟订单失败: {str(e)}")

@router.get("/orders/{account_id}")
async def get_virtual_order_history(account_id: str, limit: int = 100):
    """获取虚拟订单历史"""
    try:
        orders = await virtual_trading_engine.get_order_history(account_id, limit)
        return {
            "success": True,
            "orders": orders
        }
    except Exception as e:
        logger.error(f"获取虚拟订单历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取虚拟订单历史失败: {str(e)}")

@router.get("/performance/{account_id}")
async def get_virtual_performance(account_id: str):
    """获取虚拟交易绩效指标"""
    try:
        metrics = await virtual_trading_engine.get_performance_metrics(account_id)
        return {
            "success": True,
            "performance": metrics
        }
    except Exception as e:
        logger.error(f"获取虚拟交易绩效失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取虚拟交易绩效失败: {str(e)}")

@router.post("/market/update")
async def update_market_prices():
    """更新所有持仓的市场价格"""
    try:
        # 获取所有账户的所有持仓符号
        all_symbols = set()
        for account in virtual_trading_engine.accounts.values():
            for symbol in account.positions.keys():
                all_symbols.add(symbol)
        
        # 更新每个符号的市场价格
        for symbol in all_symbols:
            try:
                current_price = await data_service.get_current_price(symbol, MarketType.CRYPTO)
                await virtual_trading_engine.update_market_price(
                    symbol, 
                    Decimal(str(current_price))
                )
            except Exception as e:
                logger.warning(f"更新 {symbol} 价格失败: {e}")
                continue
        
        return {
            "success": True,
            "message": f"已更新 {len(all_symbols)} 个交易对的市场价格"
        }
        
    except Exception as e:
        logger.error(f"更新市场价格失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新市场价格失败: {str(e)}")

@router.get("/health")
async def health_check():
    """虚拟交易健康检查"""
    return {
        "status": "healthy",
        "service": "virtual_trading",
        "active_accounts": len(virtual_trading_engine.accounts),
        "active_orders": len(virtual_trading_engine.orders),
        "timestamp": "2025-11-07T00:44:45Z"
    }
