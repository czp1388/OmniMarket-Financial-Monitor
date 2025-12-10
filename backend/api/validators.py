"""
API请求验证器和中间件
提供统一的参数验证、错误响应、分页支持
"""
from typing import Optional, Any, Dict, List, Type
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException, Query
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================
# 通用响应模型
# ============================================

class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class APIResponse(BaseModel):
    """统一API响应格式"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="响应状态")
    message: str = Field(default="操作成功", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="错误详情")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "数据获取成功",
                "data": {"items": [], "total": 0},
                "meta": {"version": "1.0", "timestamp": "2024-01-01T00:00:00Z"}
            }
        }


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(description="数据列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }


# ============================================
# 分页参数
# ============================================

class PaginationParams:
    """分页参数（依赖注入）"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码（从1开始）"),
        page_size: int = Query(20, ge=1, le=100, description="每页大小（1-100）"),
        sort_by: Optional[str] = Query(None, description="排序字段"),
        sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="排序方向（asc/desc）")
    ):
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.offset = (page - 1) * page_size
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }


def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int
) -> PaginatedResponse:
    """创建分页响应"""
    total_pages = (total + page_size - 1) // page_size  # 向上取整
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


# ============================================
# 参数验证器
# ============================================

class SymbolValidator(BaseModel):
    """交易对验证器"""
    symbol: str = Field(..., min_length=3, max_length=20, description="交易对符号")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """验证交易对格式"""
        # 允许的格式: BTC/USDT, BTCUSDT, AAPL, 600519.SH
        if not v:
            raise ValueError("交易对不能为空")
        
        # 移除空格
        v = v.strip().upper()
        
        # 基本格式检查（字母、数字、斜杠、点）
        if not all(c.isalnum() or c in ['/', '.'] for c in v):
            raise ValueError("交易对包含非法字符")
        
        return v


class DateRangeValidator(BaseModel):
    """日期范围验证器"""
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="结束日期（YYYY-MM-DD）")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError("结束日期不能早于开始日期")
        return v


class LimitOffsetValidator(BaseModel):
    """Limit/Offset验证器"""
    limit: int = Field(default=100, ge=1, le=1000, description="返回记录数（1-1000）")
    offset: int = Field(default=0, ge=0, description="偏移量")


# ============================================
# 错误处理
# ============================================

class APIError(Exception):
    """自定义API异常"""
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


def create_error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[List[Dict[str, Any]]] = None
) -> APIResponse:
    """创建错误响应"""
    return APIResponse(
        status=ResponseStatus.ERROR,
        message=message,
        data=None,
        errors=errors
    )


def create_success_response(
    data: Any,
    message: str = "操作成功",
    meta: Optional[Dict[str, Any]] = None
) -> APIResponse:
    """创建成功响应"""
    return APIResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        meta=meta
    )


# ============================================
# 请求验证装饰器
# ============================================

def validate_request(validator_class: Type[BaseModel]):
    """请求验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                # 验证参数
                validator_class(**kwargs)
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.warning(f"参数验证失败: {e}")
                raise HTTPException(
                    status_code=400,
                    detail=create_error_response(
                        message="参数验证失败",
                        errors=[{"field": "unknown", "message": str(e)}]
                    ).dict()
                )
        return wrapper
    return decorator


# ============================================
# 速率限制（简化版）
# ============================================

class RateLimiter:
    """简单的内存速率限制器"""
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    def check_rate_limit(
        self,
        client_id: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """检查速率限制"""
        import time
        
        now = time.time()
        
        # 获取客户端请求历史
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # 清理过期请求
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window_seconds
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= max_requests:
            return False
        
        # 记录当前请求
        self.requests[client_id].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter()


# ============================================
# 数据转换工具
# ============================================

def to_camel_case(snake_str: str) -> str:
    """蛇形命名转驼峰命名"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """驼峰命名转蛇形命名"""
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


class CamelCaseModel(BaseModel):
    """自动转换为驼峰命名的模型"""
    class Config:
        alias_generator = to_camel_case
        populate_by_name = True


# ============================================
# 通用查询参数
# ============================================

class CommonQueryParams:
    """通用查询参数"""
    def __init__(
        self,
        search: Optional[str] = Query(None, description="搜索关键词"),
        filter_by: Optional[str] = Query(None, description="过滤字段"),
        filter_value: Optional[str] = Query(None, description="过滤值"),
        include_deleted: bool = Query(False, description="包含已删除记录")
    ):
        self.search = search
        self.filter_by = filter_by
        self.filter_value = filter_value
        self.include_deleted = include_deleted
