"""
基础模型
定义所有模型的通用字段和方法
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, String as StringType
import uuid

Base = declarative_base()


class UniversalUUID(TypeDecorator):
    """
    通用UUID类型，兼容SQLite和PostgreSQL
    在PostgreSQL中使用原生UUID，在SQLite中使用String
    """
    impl = StringType
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(StringType(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        else:
            return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        else:
            return uuid.UUID(value) if isinstance(value, str) else value


class BaseModel(Base):
    """基础模型类"""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """自动生成表名"""
        return cls.__name__.lower()
    
    # 使用通用UUID类型，自动适配不同数据库
    id = Column(UniversalUUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    created_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """从字典创建实例"""
        # 过滤掉None值
        filtered_data = {k: v for k, v in data.items() if v is not None}
        return cls(**filtered_data)
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """从字典更新实例"""
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_time = datetime.now(timezone.utc)
    
    @property
    def created_at(self) -> datetime:
        """创建时间别名"""
        return self.created_time
    
    @property
    def updated_at(self) -> datetime:
        """更新时间别名"""
        return self.updated_time 