"""
项目仓储类
提供项目相关的数据访问操作
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .base_repository import BaseRepository
from src.models.project import Project

class ProjectRepository(BaseRepository[Project]):
    """项目仓储类"""
    
    def __init__(self, session: Session):
        super().__init__(Project, session)
    
    def find_by_name(self, project_name: str) -> Optional[Project]:
        """
        根据项目名称查找项目
        
        Args:
            project_name: 项目名称
            
        Returns:
            项目实例或None
        """
        return self.find_one_by(project_name=project_name)
    
    def find_by_code(self, project_code: str) -> Optional[Project]:
        """
        根据项目代码查找项目
        
        Args:
            project_code: 项目代码
            
        Returns:
            项目实例或None
        """
        return self.find_one_by(project_code=project_code)
    
    def find_by_name_or_code(self, name_or_code: str) -> Optional[Project]:
        """
        根据项目名称或代码查找项目
        
        Args:
            name_or_code: 项目名称或代码
            
        Returns:
            项目实例或None
        """
        return self.session.query(self.model).filter(
            or_(
                self.model.project_name == name_or_code,
                self.model.project_code == name_or_code
            )
        ).first()
    
    def search_projects(self, search_term: str, limit: Optional[int] = None) -> List[Project]:
        """
        搜索项目
        
        Args:
            search_term: 搜索关键词
            limit: 限制数量
            
        Returns:
            匹配的项目列表
        """
        query = self.session.query(self.model).filter(
            or_(
                self.model.project_name.ilike(f"%{search_term}%"),
                self.model.project_code.ilike(f"%{search_term}%")
            )
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_active_projects(self) -> List[Project]:
        """
        获取所有活跃项目
        
        Returns:
            活跃项目列表
        """
        return self.session.query(self.model).filter(
            self.model.is_active == True
        ).all()
    
    def get_projects_by_status(self, is_active: bool) -> List[Project]:
        """
        根据状态获取项目
        
        Args:
            is_active: 是否活跃
            
        Returns:
            项目列表
        """
        return self.find_by(is_active=is_active)
    
    def update_project_status(self, project_id: str, is_active: bool) -> Optional[Project]:
        """
        更新项目状态
        
        Args:
            project_id: 项目ID
            is_active: 是否活跃
            
        Returns:
            更新后的项目实例或None
        """
        return self.update(project_id, is_active=is_active)
    
    def get_projects_with_use_cases(self) -> List[Project]:
        """
        获取包含用例的项目
        
        Returns:
            包含用例的项目列表
        """
        return self.session.query(self.model).join(
            self.model.use_cases
        ).distinct().all()
    
    def get_project_stats(self) -> dict:
        """
        获取项目统计信息
        
        Returns:
            统计信息字典
        """
        total_projects = self.count()
        active_projects = self.session.query(self.model).filter(
            self.model.is_active == True
        ).count()
        
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'inactive_projects': total_projects - active_projects
        } 