import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import uuid
import json
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from backend.models.market_data import KlineData, MarketType
from .futu_data_service import futu_data_service

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class VirtualOrder:
    """虚拟订单"""
    id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal('0')
    avg_fill_price: Decimal = Decimal('0')
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: Decimal
    avg_cost: Decimal
    market_value: Decimal = Decimal('0')
    unrealized_pnl: Decimal = Decimal('0')
    unrealized_pnl_rate: Decimal = Decimal('0')
    last_price: Decimal = Decimal('0')

@dataclass
class Account:
    """虚拟账户"""
    id: str
    name: str
    initial_balance: Decimal
    current_balance: Decimal
    available_balance: Decimal
    total_market_value: Decimal
    total_unrealized_pnl: Decimal
    total_unrealized_pnl_rate: Decimal
    positions: Dict[str, Position]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class VirtualTradingEngine:
    """虚拟交易引擎"""
    
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.orders: Dict[str, VirtualOrder] = {}
        self.pending_orders: Dict[str, List[VirtualOrder]] = {}  # 按symbol分组的待处理订单（限价单）
        self.market_prices: Dict[str, Decimal] = {}
        self.transaction_fee_rate = Decimal('0.001')  # 0.1% 交易手续费
        
        # 初始化默认市场价格
        self._initialize_default_prices()
    
    def _initialize_default_prices(self):
        """初始化默认市场价格"""
        default_prices = {
            'AAPL': Decimal('182.45'),
            'TSLA': Decimal('245.67'),
            'BTC/USDT': Decimal('42567.39'),
            'ETH/USDT': Decimal('2345.67'),
            'USD/CNY': Decimal('7.1987'),
            'EUR/USD': Decimal('1.0856'),
            'XAU/USD': Decimal('1987.45'),
            'SPY': Decimal('456.78')
        }
        self.market_prices.update(default_prices)
        
    async def create_account(self, name: str, initial_balance: Decimal = Decimal('100000')) -> str:
        """创建虚拟账户"""
        account_id = str(uuid.uuid4())
        
        account = Account(
            id=account_id,
            name=name,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            available_balance=initial_balance,
            total_market_value=Decimal('0'),
            total_unrealized_pnl=Decimal('0'),
            total_unrealized_pnl_rate=Decimal('0'),
            positions={}
        )
        
        self.accounts[account_id] = account
        logger.info(f"创建虚拟账户: {name}, 初始资金: {initial_balance}")
        
        return account_id
    
    async def place_order(
        self,
        account_id: str,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
    ) -> str:
        """下单"""
        if account_id not in self.accounts:
            raise ValueError(f"账户不存在: {account_id}")
        
        account = self.accounts[account_id]
        order_id = str(uuid.uuid4())
        
        # 验证订单
        if not await self._validate_order(account, symbol, order_type, side, quantity, price):
            raise ValueError("订单验证失败")
        
        # 创建订单
        order = VirtualOrder(
            id=order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        self.orders[order_id] = order
        
        # 根据订单类型处理
        if order_type == OrderType.MARKET:
            # 市价单立即执行
            await self._execute_market_order(order, account)
        else:
            # 限价单和止损单添加到待处理列表
            if symbol not in self.pending_orders:
                self.pending_orders[symbol] = []
            self.pending_orders[symbol].append(order)
            
            # 对于非市价单，冻结资金
            await self._reserve_funds_for_order(order, account)
        
        logger.info(f"下单成功: {order_id}, {symbol}, {order_type.value}, {side.value}, {quantity}")
        return order_id
    
    async def _reserve_funds_for_order(self, order: VirtualOrder, account: Account):
        """为订单冻结资金"""
        if order.side == OrderSide.BUY:
            # 计算需要的资金（包括手续费）
            required_funds = order.quantity * order.price * (1 + self.transaction_fee_rate)
            account.available_balance -= required_funds
            logger.info(f"冻结资金: {required_funds} for order {order.id}")
    
    async def _validate_order(
        self,
        account: Account,
        symbol: str,
        order_type: OrderType,
        side: OrderSide,
        quantity: Decimal,
        price: Optional[Decimal]
    ) -> bool:
        """验证订单"""
        if quantity <= Decimal('0'):
            return False
        
        # 检查资金是否足够
        if side == OrderSide.BUY:
            if order_type == OrderType.MARKET:
                current_price = self.market_prices.get(symbol, Decimal('0'))
                if current_price <= Decimal('0'):
                    return False
                total_cost = quantity * current_price * (1 + self.transaction_fee_rate)
            else:
                if price is None or price <= Decimal('0'):
                    return False
                total_cost = quantity * price * (1 + self.transaction_fee_rate)
            
            if total_cost > account.available_balance:
                return False
        
        return True
    
    async def _execute_market_order(self, order: VirtualOrder, account: Account):
        """执行市价单"""
        current_price = self.market_prices.get(order.symbol)
        if not current_price or current_price <= Decimal('0'):
            order.status = OrderStatus.REJECTED
            return
        
        # 计算交易费用
        transaction_fee = order.quantity * current_price * self.transaction_fee_rate
        
        if order.side == OrderSide.BUY:
            # 买入逻辑
            total_cost = order.quantity * current_price + transaction_fee
            
            if total_cost > account.available_balance:
                order.status = OrderStatus.REJECTED
                return
            
            # 更新账户余额
            account.current_balance -= total_cost
            account.available_balance -= total_cost
            
            # 更新持仓
            if order.symbol in account.positions:
                position = account.positions[order.symbol]
                total_quantity = position.quantity + order.quantity
                total_cost_value = (position.avg_cost * position.quantity + 
                                  order.quantity * current_price)
                position.avg_cost = total_cost_value / total_quantity
                position.quantity = total_quantity
            else:
                account.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_cost=current_price
                )
            
        else:  # SELL
            # 卖出逻辑
            if order.symbol not in account.positions:
                order.status = OrderStatus.REJECTED
                return
            
            position = account.positions[order.symbol]
            if order.quantity > position.quantity:
                order.status = OrderStatus.REJECTED
                return
            
            # 计算收益
            sell_amount = order.quantity * current_price - transaction_fee
            cost_basis = position.avg_cost * order.quantity
            
            # 更新账户余额
            account.current_balance += sell_amount
            account.available_balance += sell_amount
            
            # 更新持仓
            position.quantity -= order.quantity
            if position.quantity == Decimal('0'):
                del account.positions[order.symbol]
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = current_price
        order.updated_at = datetime.now()
        
        # 更新账户市值
        await self._update_account_market_value(account)
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status not in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        logger.info(f"取消订单: {order_id}")
        return True
    
    async def update_market_price(self, symbol: str, price: Decimal):
        """更新市场价格"""
        self.market_prices[symbol] = price
        
        # 更新所有账户的持仓市值
        for account in self.accounts.values():
            await self._update_account_market_value(account)
        
        # 检查待处理订单的触发条件
        await self._check_pending_orders(symbol, price)
    
    async def _check_pending_orders(self, symbol: str, current_price: Decimal):
        """检查待处理订单的触发条件"""
        if symbol not in self.pending_orders:
            return
        
        orders_to_remove = []
        
        for order in self.pending_orders[symbol]:
            if order.status != OrderStatus.PENDING:
                orders_to_remove.append(order)
                continue
            
            # 检查限价单触发条件
            if order.order_type == OrderType.LIMIT:
                if await self._check_limit_order_trigger(order, current_price):
                    # 执行限价单
                    account = self._find_account_by_order(order)
                    if account:
                        await self._execute_limit_order(order, account)
                        orders_to_remove.append(order)
            
            # 检查止损单触发条件
            elif order.order_type == OrderType.STOP:
                if await self._check_stop_order_trigger(order, current_price):
                    # 执行止损单
                    account = self._find_account_by_order(order)
                    if account:
                        await self._execute_stop_order(order, account)
                        orders_to_remove.append(order)
        
        # 移除已执行或无效的订单
        for order in orders_to_remove:
            if order in self.pending_orders[symbol]:
                self.pending_orders[symbol].remove(order)
    
    async def _check_limit_order_trigger(self, order: VirtualOrder, current_price: Decimal) -> bool:
        """检查限价单触发条件"""
        if order.side == OrderSide.BUY:
            # 买入限价单：当前价格 <= 限价
            return current_price <= order.price
        else:
            # 卖出限价单：当前价格 >= 限价
            return current_price >= order.price
    
    async def _check_stop_order_trigger(self, order: VirtualOrder, current_price: Decimal) -> bool:
        """检查止损单触发条件"""
        if order.side == OrderSide.BUY:
            # 买入止损单：当前价格 >= 止损价
            return current_price >= order.stop_price
        else:
            # 卖出止损单：当前价格 <= 止损价
            return current_price <= order.stop_price
    
    def _find_account_by_order(self, order: VirtualOrder) -> Optional[Account]:
        """根据订单找到对应的账户"""
        # 简化实现：假设所有订单都关联到第一个账户
        # 在实际系统中，应该有订单与账户的关联关系
        if self.accounts:
            return next(iter(self.accounts.values()))
        return None
    
    async def _execute_limit_order(self, order: VirtualOrder, account: Account):
        """执行限价单"""
        current_price = self.market_prices.get(order.symbol, Decimal('0'))
        if current_price <= Decimal('0'):
            order.status = OrderStatus.REJECTED
            return
        
        # 计算交易费用
        transaction_fee = order.quantity * current_price * self.transaction_fee_rate
        
        if order.side == OrderSide.BUY:
            # 买入限价单执行逻辑
            total_cost = order.quantity * current_price + transaction_fee
            
            # 更新账户余额（已冻结资金，这里只需要调整余额）
            account.current_balance -= total_cost
            
            # 更新持仓
            if order.symbol in account.positions:
                position = account.positions[order.symbol]
                total_quantity = position.quantity + order.quantity
                total_cost_value = (position.avg_cost * position.quantity + 
                                  order.quantity * current_price)
                position.avg_cost = total_cost_value / total_quantity
                position.quantity = total_quantity
            else:
                account.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_cost=current_price
                )
            
        else:  # SELL
            # 卖出限价单执行逻辑
            if order.symbol not in account.positions:
                order.status = OrderStatus.REJECTED
                return
            
            position = account.positions[order.symbol]
            if order.quantity > position.quantity:
                order.status = OrderStatus.REJECTED
                return
            
            # 计算收益
            sell_amount = order.quantity * current_price - transaction_fee
            cost_basis = position.avg_cost * order.quantity
            
            # 更新账户余额
            account.current_balance += sell_amount
            account.available_balance += sell_amount
            
            # 更新持仓
            position.quantity -= order.quantity
            if position.quantity == Decimal('0'):
                del account.positions[order.symbol]
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = current_price
        order.updated_at = datetime.now()
        
        # 更新账户市值
        await self._update_account_market_value(account)
        
        logger.info(f"限价单执行成功: {order.id}, {order.symbol}, {order.side.value}, {order.quantity}")
    
    async def _execute_stop_order(self, order: VirtualOrder, account: Account):
        """执行止损单"""
        current_price = self.market_prices.get(order.symbol, Decimal('0'))
        if current_price <= Decimal('0'):
            order.status = OrderStatus.REJECTED
            return
        
        # 止损单执行时转为市价单
        await self._execute_market_order(order, account)
        logger.info(f"止损单执行成功: {order.id}, {order.symbol}, {order.side.value}, {order.quantity}")
    
    async def sync_market_prices(self, symbols: List[str]):
        """同步市场价格从富途数据服务"""
        for symbol in symbols:
            try:
                quote = await futu_data_service.get_stock_quote(symbol)
                if quote and 'last_price' in quote:
                    price = Decimal(str(quote['last_price']))
                    await self.update_market_price(symbol, price)
                    logger.info(f"同步市场价格: {symbol} = {price}")
            except Exception as e:
                logger.error(f"同步市场价格失败 {symbol}: {e}")
    
    async def _update_account_market_value(self, account: Account):
        """更新账户市值"""
        total_market_value = Decimal('0')
        total_cost_basis = Decimal('0')
        
        for symbol, position in account.positions.items():
            current_price = self.market_prices.get(symbol, Decimal('0'))
            position.last_price = current_price
            position.market_value = position.quantity * current_price
            position.unrealized_pnl = position.market_value - (position.avg_cost * position.quantity)
            
            if position.avg_cost * position.quantity > Decimal('0'):
                position.unrealized_pnl_rate = (
                    position.unrealized_pnl / (position.avg_cost * position.quantity) * Decimal('100')
                )
            
            total_market_value += position.market_value
            total_cost_basis += position.avg_cost * position.quantity
        
        account.total_market_value = total_market_value
        account.total_unrealized_pnl = total_market_value - total_cost_basis
        
        if total_cost_basis > Decimal('0'):
            account.total_unrealized_pnl_rate = (
                account.total_unrealized_pnl / total_cost_basis * Decimal('100')
            )
    
    async def get_account_info(self, account_id: str) -> Optional[Dict]:
        """获取账户信息"""
        if account_id not in self.accounts:
            return None
        
        account = self.accounts[account_id]
        await self._update_account_market_value(account)
        
        return {
            'id': account.id,
            'name': account.name,
            'initial_balance': float(account.initial_balance),
            'current_balance': float(account.current_balance),
            'available_balance': float(account.available_balance),
            'total_market_value': float(account.total_market_value),
            'total_unrealized_pnl': float(account.total_unrealized_pnl),
            'total_unrealized_pnl_rate': float(account.total_unrealized_pnl_rate),
            'total_assets': float(account.current_balance + account.total_market_value),
            'positions': [
                {
                    'symbol': pos.symbol,
                    'quantity': float(pos.quantity),
                    'avg_cost': float(pos.avg_cost),
                    'market_value': float(pos.market_value),
                    'unrealized_pnl': float(pos.unrealized_pnl),
                    'unrealized_pnl_rate': float(pos.unrealized_pnl_rate),
                    'last_price': float(pos.last_price)
                }
                for pos in account.positions.values()
            ],
            'created_at': account.created_at.isoformat()
        }
    
    async def get_order_history(self, account_id: str, limit: int = 100) -> List[Dict]:
        """获取订单历史"""
        account_orders = [
            order for order in self.orders.values()
            # 这里应该根据账户关联订单，简化处理返回所有订单
        ]
        
        sorted_orders = sorted(
            account_orders[:limit],
            key=lambda x: x.created_at,
            reverse=True
        )
        
        return [
            {
                'id': order.id,
                'symbol': order.symbol,
                'order_type': order.order_type.value,
                'side': order.side.value,
                'quantity': float(order.quantity),
                'price': float(order.price) if order.price else None,
                'stop_price': float(order.stop_price) if order.stop_price else None,
                'status': order.status.value,
                'filled_quantity': float(order.filled_quantity),
                'avg_fill_price': float(order.avg_fill_price),
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }
            for order in sorted_orders
        ]
    
    async def get_performance_metrics(self, account_id: str) -> Dict:
        """获取绩效指标"""
        account_info = await self.get_account_info(account_id)
        if not account_info:
            return {}
        
        total_assets = account_info['total_assets']
        initial_balance = account_info['initial_balance']
        
        # 计算收益率
        total_return = ((total_assets - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0
        
        # 计算日收益率（简化版）
        daily_return = self._calculate_daily_return(account_id)
        
        # 计算夏普比率（简化版）
        sharpe_ratio = self._calculate_sharpe_ratio(account_id)
        
        # 计算最大回撤（简化版）
        max_drawdown = self._calculate_max_drawdown(account_id)
        
        # 计算胜率
        win_rate = self._calculate_win_rate(account_id)
        
        # 计算盈利交易数
        profitable_trades = self._count_profitable_trades(account_id)
        
        # 总交易数
        total_trades = len([o for o in self.orders.values() if o.status == OrderStatus.FILLED])
        
        return {
            'total_return': total_return,
            'daily_return': daily_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': 0.0,  # 需要更复杂的交易历史数据
            'total_trades': total_trades,
            'profitable_trades': profitable_trades
        }
    
    def _calculate_daily_return(self, account_id: str) -> float:
        """计算日收益率（简化实现）"""
        # 这里应该基于每日收益率计算，简化返回固定值
        return 0.25
    
    def _calculate_win_rate(self, account_id: str) -> float:
        """计算胜率"""
        filled_orders = [o for o in self.orders.values() if o.status == OrderStatus.FILLED]
        if not filled_orders:
            return 0.0
        
        profitable_orders = 0
        for order in filled_orders:
            if order.side == OrderSide.BUY:
                # 对于买入订单，如果当前价格高于成本价则视为盈利
                current_price = self.market_prices.get(order.symbol, Decimal('0'))
                if current_price > order.avg_fill_price:
                    profitable_orders += 1
            else:
                # 对于卖出订单，如果卖出价格高于成本价则视为盈利
                if order.avg_fill_price > Decimal('0'):  # 简化处理
                    profitable_orders += 1
        
        return (profitable_orders / len(filled_orders)) * 100
    
    def _count_profitable_trades(self, account_id: str) -> int:
        """计算盈利交易数"""
        filled_orders = [o for o in self.orders.values() if o.status == OrderStatus.FILLED]
        profitable_orders = 0
        
        for order in filled_orders:
            if order.side == OrderSide.BUY:
                current_price = self.market_prices.get(order.symbol, Decimal('0'))
                if current_price > order.avg_fill_price:
                    profitable_orders += 1
            else:
                if order.avg_fill_price > Decimal('0'):  # 简化处理
                    profitable_orders += 1
        
        return profitable_orders
    
    def _calculate_sharpe_ratio(self, account_id: str) -> float:
        """计算夏普比率（简化实现）"""
        # 这里应该基于历史收益率计算，简化返回固定值
        return 1.5
    
    def _calculate_max_drawdown(self, account_id: str) -> float:
        """计算最大回撤（简化实现）"""
        # 这里应该基于历史净值计算，简化返回固定值
        return 5.0


# 全局虚拟交易引擎实例
virtual_trading_engine = VirtualTradingEngine()
