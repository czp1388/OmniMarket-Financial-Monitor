import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
from backend.models.warrants import WarrantData, WarrantType, WarrantStatus
from backend.services.futu_data_service import futu_data_service

logger = logging.getLogger(__name__)


class WarrantsDataService:
    """牛熊证数据服务 - 集成多个数据源获取港股牛熊证数据"""
    
    def __init__(self):
        self.logger = logger
        self.tencent_base_url = "https://stock.finance.sina.com.cn/hkstock/api/jsonp.php"
        self.sina_base_url = "https://hq.sinajs.cn"
        self.session = None
        
    async def initialize(self):
        """初始化数据服务"""
        self.session = aiohttp.ClientSession()
        await futu_data_service.connect()
        
    async def get_warrants_list(self, underlying_symbol: str = None) -> List[WarrantData]:
        """获取牛熊证列表"""
        try:
            # 尝试从富途API获取
            if futu_data_service.connected:
                warrants = await self._get_warrants_from_futu(underlying_symbol)
                if warrants:
                    return warrants
            
            # 回退到模拟数据
            return await self._get_mock_warrants_data(underlying_symbol)
            
        except Exception as e:
            self.logger.error(f"获取牛熊证列表失败: {str(e)}")
            return await self._get_mock_warrants_data(underlying_symbol)
    
    async def _get_warrants_from_futu(self, underlying_symbol: str = None) -> List[WarrantData]:
        """从富途API获取牛熊证数据"""
        try:
            # 富途API获取窝轮（牛熊证）列表
            # 注意：这里需要实际的富途API调用，目前使用模拟实现
            # 在实际部署中，这里应该调用富途的get_warrant_list API
            
            # 模拟富途API返回的数据
            futu_warrants = [
                {
                    'code': '12345.HK',
                    'name': '腾讯法兴九乙购A',
                    'stock_code': '00700.HK',
                    'warrant_type': 'BULL',
                    'strike_price': 180.0,
                    'knock_out_price': 200.0,
                    'last_price': 0.25,
                    'leverage': 15.2,
                    'maturity_date': '2025-06-30',
                    'volume': 1500000,
                    'avg_volume': 800000,
                    'conversion_ratio': 100
                },
                {
                    'code': '67890.HK',
                    'name': '腾讯瑞通九乙沽A',
                    'stock_code': '00700.HK',
                    'warrant_type': 'BEAR',
                    'strike_price': 220.0,
                    'knock_out_price': 200.0,
                    'last_price': 0.18,
                    'leverage': 12.8,
                    'maturity_date': '2025-05-15',
                    'volume': 800000,
                    'avg_volume': 500000,
                    'conversion_ratio': 100
                }
            ]
            
            warrants = []
            for w_data in futu_warrants:
                if underlying_symbol and w_data['stock_code'] != underlying_symbol:
                    continue
                    
                # 计算剩余到期时间
                maturity_date = datetime.strptime(w_data['maturity_date'], '%Y-%m-%d')
                time_to_maturity = (maturity_date - datetime.now()).days
                
                warrant = WarrantData(
                    symbol=w_data['code'],
                    name=w_data['name'],
                    underlying_symbol=w_data['stock_code'],
                    warrant_type=WarrantType.BULL if w_data['warrant_type'] == 'BULL' else WarrantType.BEAR,
                    strike_price=w_data['strike_price'],
                    knock_out_price=w_data['knock_out_price'],
                    current_price=w_data['last_price'],
                    leverage=w_data['leverage'],
                    time_to_maturity=max(time_to_maturity, 0),
                    conversion_ratio=w_data['conversion_ratio'],
                    status=WarrantStatus.ACTIVE if time_to_maturity > 0 else WarrantStatus.EXPIRED,
                    volume=w_data['volume'],
                    average_volume=w_data['avg_volume'],
                    last_updated=datetime.now()
                )
                warrants.append(warrant)
                
            return warrants
            
        except Exception as e:
            self.logger.error(f"从富途获取牛熊证数据失败: {str(e)}")
            return []
    
    async def get_warrant_realtime_data(self, warrant_symbol: str) -> Optional[WarrantData]:
        """获取牛熊证实时数据"""
        try:
            # 尝试从富途API获取实时数据
            if futu_data_service.connected:
                data = await self._get_warrant_realtime_from_futu(warrant_symbol)
                if data:
                    return data
            
            # 回退到模拟数据
            return await self._get_mock_warrant_realtime(warrant_symbol)
            
        except Exception as e:
            self.logger.error(f"获取牛熊证实时数据失败 {warrant_symbol}: {str(e)}")
            return await self._get_mock_warrant_realtime(warrant_symbol)
    
    async def _get_warrant_realtime_from_futu(self, warrant_symbol: str) -> Optional[WarrantData]:
        """从富途API获取牛熊证实时数据"""
        try:
            # 模拟富途API调用
            # 在实际部署中，这里应该调用富途的get_stock_quote API
            
            # 模拟数据映射
            warrant_data_map = {
                '12345.HK': {
                    'last_price': 0.25 + (datetime.now().second % 10 - 5) * 0.001,
                    'volume': 1500000 + (datetime.now().minute % 10) * 10000,
                    'high': 0.26,
                    'low': 0.24,
                    'open': 0.25,
                    'change': 0.0
                },
                '67890.HK': {
                    'last_price': 0.18 + (datetime.now().second % 10 - 5) * 0.001,
                    'volume': 800000 + (datetime.now().minute % 10) * 5000,
                    'high': 0.19,
                    'low': 0.17,
                    'open': 0.18,
                    'change': 0.0
                }
            }
            
            if warrant_symbol not in warrant_data_map:
                return None
                
            data = warrant_data_map[warrant_symbol]
            
            # 获取基础信息
            base_info = await self._get_warrant_base_info(warrant_symbol)
            if not base_info:
                return None
                
            # 更新实时数据
            base_info.current_price = data['last_price']
            base_info.volume = data['volume']
            base_info.high = data['high']
            base_info.low = data['low']
            base_info.open = data['open']
            base_info.change = data['change']
            base_info.last_updated = datetime.now()
            
            return base_info
            
        except Exception as e:
            self.logger.error(f"从富途获取牛熊证实时数据失败 {warrant_symbol}: {str(e)}")
            return None
    
    async def _get_warrant_base_info(self, warrant_symbol: str) -> Optional[WarrantData]:
        """获取牛熊证基础信息"""
        # 模拟基础信息
        base_info_map = {
            '12345.HK': WarrantData(
                symbol='12345.HK',
                name='腾讯法兴九乙购A',
                underlying_symbol='00700.HK',
                warrant_type=WarrantType.BULL,
                strike_price=180.0,
                knock_out_price=200.0,
                current_price=0.25,
                leverage=15.2,
                time_to_maturity=180,
                conversion_ratio=100,
                status=WarrantStatus.ACTIVE,
                volume=1500000,
                average_volume=800000,
                last_updated=datetime.now()
            ),
            '67890.HK': WarrantData(
                symbol='67890.HK',
                name='腾讯瑞通九乙沽A',
                underlying_symbol='00700.HK',
                warrant_type=WarrantType.BEAR,
                strike_price=220.0,
                knock_out_price=200.0,
                current_price=0.18,
                leverage=12.8,
                time_to_maturity=150,
                conversion_ratio=100,
                status=WarrantStatus.ACTIVE,
                volume=800000,
                average_volume=500000,
                last_updated=datetime.now()
            )
        }
        
        return base_info_map.get(warrant_symbol)
    
    async def get_underlying_realtime_data(self, symbol: str) -> Dict:
        """获取正股实时数据"""
        try:
            # 使用富途数据服务获取正股数据
            quote = await futu_data_service.get_stock_quote(symbol)
            return quote
        except Exception as e:
            self.logger.error(f"获取正股实时数据失败 {symbol}: {str(e)}")
            return await self._get_mock_underlying_data(symbol)
    
    async def _get_mock_underlying_data(self, symbol: str) -> Dict:
        """生成正股模拟数据"""
        import random
        base_prices = {
            '00700.HK': 185.5,
            '00005.HK': 45.2,
            '01299.HK': 120.8,
            '00941.HK': 62.3
        }
        
        base_price = base_prices.get(symbol, 50.0)
        change = random.uniform(-2.0, 2.0)
        
        return {
            'symbol': symbol,
            'last_price': base_price + change,
            'open': base_price,
            'high': base_price + random.uniform(0, 3.0),
            'low': base_price - random.uniform(0, 3.0),
            'volume': random.uniform(1000000, 5000000),
            'turnover': random.uniform(50000000, 200000000),
            'change': change,
            'change_rate': (change / base_price) * 100,
            'timestamp': datetime.now()
        }
    
    async def _get_mock_warrants_data(self, underlying_symbol: str = None) -> List[WarrantData]:
        """生成牛熊证模拟数据"""
        mock_warrants = [
            WarrantData(
                symbol="12345.HK",
                name="腾讯法兴九乙购A",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BULL,
                strike_price=180.0,
                knock_out_price=200.0,
                current_price=0.25,
                leverage=15.2,
                time_to_maturity=180,
                conversion_ratio=100,
                status=WarrantStatus.ACTIVE,
                volume=1500000,
                average_volume=800000,
                last_updated=datetime.now()
            ),
            WarrantData(
                symbol="67890.HK",
                name="腾讯瑞通九乙沽A",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BEAR,
                strike_price=220.0,
                knock_out_price=200.0,
                current_price=0.18,
                leverage=12.8,
                time_to_maturity=150,
                conversion_ratio=100,
                status=WarrantStatus.ACTIVE,
                volume=800000,
                average_volume=500000,
                last_updated=datetime.now()
            ),
            WarrantData(
                symbol="23456.HK",
                name="腾讯摩通九乙购B",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BULL,
                strike_price=190.0,
                knock_out_price=210.0,
                current_price=0.22,
                leverage=14.5,
                time_to_maturity=120,
                conversion_ratio=100,
                status=WarrantStatus.ACTIVE,
                volume=1200000,
                average_volume=600000,
                last_updated=datetime.now()
            ),
            WarrantData(
                symbol="78901.HK",
                name="腾讯高盛九乙沽B",
                underlying_symbol="00700.HK",
                warrant_type=WarrantType.BEAR,
                strike_price=230.0,
                knock_out_price=210.0,
                current_price=0.15,
                leverage=13.2,
                time_to_maturity=90,
                conversion_ratio=100,
                status=WarrantStatus.ACTIVE,
                volume=900000,
                average_volume=450000,
                last_updated=datetime.now()
            )
        ]
        
        if underlying_symbol:
            return [w for w in mock_warrants if w.underlying_symbol == underlying_symbol]
        else:
            return mock_warrants
    
    async def _get_mock_warrant_realtime(self, warrant_symbol: str) -> Optional[WarrantData]:
        """生成牛熊证实时模拟数据"""
        base_info = await self._get_warrant_base_info(warrant_symbol)
        if not base_info:
            return None
            
        # 添加随机波动
        import random
        change = random.uniform(-0.01, 0.01)
        base_info.current_price = max(base_info.current_price + change, 0.01)
        base_info.volume = base_info.average_volume + random.randint(-100000, 100000)
        base_info.last_updated = datetime.now()
        
        return base_info
    
    async def get_warrants_by_risk_level(self, max_risk_score: float = 0.7) -> List[WarrantData]:
        """根据风险等级筛选牛熊证"""
        all_warrants = await self.get_warrants_list()
        
        # 简化的风险评估
        low_risk_warrants = []
        for warrant in all_warrants:
            # 计算风险评分
            risk_score = self._calculate_risk_score(warrant)
            if risk_score <= max_risk_score:
                warrant.risk_score = risk_score
                low_risk_warrants.append(warrant)
        
        # 按风险评分排序
        low_risk_warrants.sort(key=lambda x: x.risk_score)
        return low_risk_warrants
    
    def _calculate_risk_score(self, warrant: WarrantData) -> float:
        """计算风险评分"""
        # 距离回收价风险（越近风险越高）
        underlying_price = 185.5  # 模拟正股价格
        if warrant.warrant_type == WarrantType.BULL:
            distance_risk = max(0, 1 - (warrant.knock_out_price - underlying_price) / underlying_price)
        else:
            distance_risk = max(0, 1 - (underlying_price - warrant.knock_out_price) / underlying_price)
        
        # 时间价值衰减风险（剩余时间越短风险越高）
        time_risk = 1 - (warrant.time_to_maturity / 365.0)
        
        # 杠杆风险（杠杆越高风险越高）
        leverage_risk = min(warrant.leverage / 30.0, 1.0)
        
        # 综合风险评分
        risk_score = (distance_risk * 0.4 + time_risk * 0.3 + leverage_risk * 0.3)
        return risk_score
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
        await futu_data_service.disconnect()


# 全局牛熊证数据服务实例
warrants_data_service = WarrantsDataService()
