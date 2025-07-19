"""
用例仓储类
提供用例相关的数据访问操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .base_repository import BaseRepository
from src.models.use_case import UseCase

class UseCaseRepository(BaseRepository[UseCase]):
    """用例仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(UseCase, session)
    
    def find_by_project_id(self, project_id: str) -> List[UseCase]:
        """
        根据项目ID查找用例
        
        Args:
            project_id: 项目ID
            
        Returns:
            用例列表
        """
        return self.find_by(project_id=project_id)
    
    def find_by_name(self, use_case_name: str) -> Optional[UseCase]:
        """
        根据用例名称查找用例
        
        Args:
            use_case_name: 用例名称
            
        Returns:
            用例实例或None
        """
        return self.find_one_by(use_case_name=use_case_name)
    
    def find_by_project_and_name(self, project_id: str, use_case_name: str) -> Optional[UseCase]:
        """
        根据项目ID和用例名称查找用例
        
        Args:
            project_id: 项目ID
            use_case_name: 用例名称
            
        Returns:
            用例实例或None
        """
        return self.session.query(self.model).filter(
            and_(
                self.model.project_id == project_id,
                self.model.use_case_name == use_case_name
            )
        ).first()
    
    def get_active_use_cases(self) -> List[UseCase]:
        """
        获取所有活跃用例
        
        Returns:
            活跃用例列表
        """
        return self.find_by(is_active=True)
    
    def get_use_cases_by_project_and_status(self, project_id: str, is_active: bool) -> List[UseCase]:
        """
        根据项目ID和状态获取用例
        
        Args:
            project_id: 项目ID
            is_active: 是否活跃
            
        Returns:
            用例列表
        """
        return self.session.query(self.model).filter(
            and_(
                self.model.project_id == project_id,
                self.model.is_active == is_active
            )
        ).all()
    
    def find_by_ad_group(self, ad_group: str) -> List[UseCase]:
        """
        根据广告组查找用例
        
        Args:
            ad_group: 广告组
            
        Returns:
            用例列表
        """
        return self.find_by(ad_group=ad_group)
    
    def search_use_cases(self, search_term: str, project_id: Optional[str] = None, limit: Optional[int] = None) -> List[UseCase]:
        """
        搜索用例
        
        Args:
            search_term: 搜索关键词
            project_id: 项目ID（可选）
            limit: 限制数量
            
        Returns:
            匹配的用例列表
        """
        query = self.session.query(self.model).filter(
            or_(
                self.model.use_case_name.ilike(f"%{search_term}%"),
                self.model.ad_group.ilike(f"%{search_term}%")
            )
        )
        
        if project_id:
            query = query.filter(self.model.project_id == project_id)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_use_case_status(self, use_case_id: str, is_active: bool) -> Optional[UseCase]:
        """
        更新用例状态
        
        Args:
            use_case_id: 用例ID
            is_active: 是否活跃
            
        Returns:
            更新后的用例实例或None
        """
        return self.update(use_case_id, is_active=is_active)
    
    def get_use_cases_with_budgets(self) -> List[UseCase]:
        """
        获取包含预算的用例
        
        Returns:
            包含预算的用例列表
        """
        return self.session.query(self.model).join(
            self.model.budgets
        ).distinct().all()
    
    def get_use_case_stats(self, project_id: Optional[str] = None) -> dict:
        """
        获取用例统计信息
        
        Args:
            project_id: 项目ID（可选）
            
        Returns:
            统计信息字典
        """
        query = self.session.query(self.model)
        if project_id:
            query = query.filter(self.model.project_id == project_id)
        
        total_use_cases = query.count()
        active_use_cases = query.filter(self.model.is_active == True).count()
        
        return {
            'total_use_cases': total_use_cases,
            'active_use_cases': active_use_cases,
            'inactive_use_cases': total_use_cases - active_use_cases
        } 