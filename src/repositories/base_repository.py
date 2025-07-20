"""
基础仓储类
提供通用的CRUD操作
"""

import uuid
import os
from typing import Generic, Type, TypeVar, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """基础仓储类"""
    
    def __init__(self, model: Type[T], session: Session):
        """
        初始化仓储
        
        Args:
            model: 模型类
            session: 数据库会话
        """
        self.model = model
        self.session = session
    
    def _convert_id_to_uuid(self, id: str) -> uuid.UUID:
        """
        将字符串ID转换为UUID对象
        
        Args:
            id: 字符串ID
            
        Returns:
            UUID对象
        """
        try:
            return uuid.UUID(id)
        except (ValueError, AttributeError):
            # 如果已经是UUID对象或无效格式，直接返回
            return id
    
    def _get_id_value(self, id: str):
        """
        根据环境获取ID值
        
        Args:
            id: 字符串ID
            
        Returns:
            ID值（UUID对象或字符串）
        """
        # 在测试环境中使用字符串ID
        if os.getenv('TESTING', 'false').lower() == 'true':
            return id
        else:
            return self._convert_id_to_uuid(id)
    
    def create(self, **kwargs) -> T:
        """
        创建新记录
        
        Args:
            **kwargs: 模型字段值
            
        Returns:
            创建的模型实例
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.flush()  # 获取ID但不提交
        return instance
    
    def get_by_id(self, id: str) -> Optional[T]:
        """
        根据ID获取记录
        
        Args:
            id: 记录ID
            
        Returns:
            模型实例或None
        """
        id_value = self._get_id_value(id)
        return self.session.query(self.model).filter(self.model.id == id_value).first()
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        获取所有记录
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            模型实例列表
        """
        query = self.session.query(self.model)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def update(self, id: str, **kwargs) -> Optional[T]:
        """
        更新记录
        
        Args:
            id: 记录ID
            **kwargs: 要更新的字段值
            
        Returns:
            更新后的模型实例或None
        """
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.session.flush()
        return instance
    
    def delete(self, id: str) -> bool:
        """
        删除记录
        
        Args:
            id: 记录ID
            
        Returns:
            是否删除成功
        """
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.flush()
            return True
        return False
    
    def count(self) -> int:
        """
        获取记录总数
        
        Returns:
            记录总数
        """
        return self.session.query(self.model).count()
    
    def exists(self, id: str) -> bool:
        """
        检查记录是否存在
        
        Args:
            id: 记录ID
            
        Returns:
            是否存在
        """
        id_value = self._get_id_value(id)
        return self.session.query(self.model).filter(self.model.id == id_value).first() is not None
    
    def find_by(self, **kwargs) -> List[T]:
        """
        根据条件查找记录
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            匹配的模型实例列表
        """
        filters = []
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                # 如果是ID字段，需要转换
                if key.endswith('_id') and isinstance(value, str):
                    value = self._get_id_value(value)
                filters.append(getattr(self.model, key) == value)
        
        if filters:
            return self.session.query(self.model).filter(and_(*filters)).all()
        return []
    
    def find_one_by(self, **kwargs) -> Optional[T]:
        """
        根据条件查找单条记录
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            匹配的模型实例或None
        """
        filters = []
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                # 如果是ID字段，需要转换
                if key.endswith('_id') and isinstance(value, str):
                    value = self._get_id_value(value)
                filters.append(getattr(self.model, key) == value)
        
        if filters:
            return self.session.query(self.model).filter(and_(*filters)).first()
        return None
    
    def bulk_create(self, instances: List[Dict[str, Any]]) -> List[T]:
        """
        批量创建记录
        
        Args:
            instances: 要创建的实例数据列表
            
        Returns:
            创建的模型实例列表
        """
        created_instances = []
        for instance_data in instances:
            instance = self.model(**instance_data)
            self.session.add(instance)
            created_instances.append(instance)
        
        self.session.flush()
        return created_instances
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> List[T]:
        """
        批量更新记录
        
        Args:
            updates: 更新数据列表，每个字典包含id和要更新的字段
            
        Returns:
            更新后的模型实例列表
        """
        updated_instances = []
        for update_data in updates:
            id = update_data.pop('id', None)
            if id:
                instance = self.update(id, **update_data)
                if instance:
                    updated_instances.append(instance)
        
        return updated_instances
    
    def bulk_delete(self, ids: List[str]) -> int:
        """
        批量删除记录
        
        Args:
            ids: 要删除的记录ID列表
            
        Returns:
            删除的记录数量
        """
        deleted_count = 0
        for id in ids:
            if self.delete(id):
                deleted_count += 1
        
        return deleted_count 