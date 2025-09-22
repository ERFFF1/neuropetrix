"""
Workflow Engine - İncele → Onayla → Finalize Akışı
Role-based access control ile raporlama workflow'u
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow Durumları"""
    DRAFT = "draft"           # Taslak
    IN_REVIEW = "in_review"   # İnceleme
    APPROVED = "approved"     # Onaylandı
    FINALIZED = "finalized"   # Finalize edildi
    REJECTED = "rejected"     # Reddedildi
    ARCHIVED = "archived"     # Arşivlendi

class UserRole(Enum):
    """Kullanıcı Rolleri"""
    RADIOLOGIST = "radiologist"     # Radyolog
    CLINICIAN = "clinician"         # Klinisyen
    ADMIN = "admin"                 # Yönetici
    TECHNICIAN = "technician"       # Teknisyen
    VIEWER = "viewer"              # Görüntüleyici

class WorkflowAction(Enum):
    """Workflow Aksiyonları"""
    CREATE = "create"           # Oluştur
    REVIEW = "review"           # İncele
    APPROVE = "approve"         # Onayla
    REJECT = "reject"           # Reddet
    FINALIZE = "finalize"       # Finalize et
    ARCHIVE = "archive"         # Arşivle
    COMMENT = "comment"         # Yorum ekle
    REQUEST_CONSULTATION = "request_consultation"  # Danışmanlık iste

@dataclass
class WorkflowStep:
    """Workflow Adımı"""
    step_id: str
    name: str
    description: str
    required_role: UserRole
    status: WorkflowStatus
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    comments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowInstance:
    """Workflow Örneği"""
    workflow_id: str
    report_id: str
    title: str
    current_status: WorkflowStatus
    steps: List[WorkflowStep] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class User:
    """Kullanıcı"""
    user_id: str
    username: str
    role: UserRole
    name: str
    email: str
    is_active: bool = True
    permissions: List[str] = field(default_factory=list)

class WorkflowEngine:
    """Workflow Motoru"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowInstance] = {}
        self.users: Dict[str, User] = {}
        self.workflow_templates = self._load_workflow_templates()
        
        # Varsayılan kullanıcıları oluştur
        self._create_default_users()
        
        logger.info("Workflow Engine başlatıldı")

    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Workflow şablonlarını yükle"""
        return {
            "standard_report": {
                "name": "Standart Rapor Workflow",
                "description": "Standart PET/CT raporu için workflow",
                "steps": [
                    {
                        "step_id": "create",
                        "name": "Rapor Oluştur",
                        "description": "Rapor taslağını oluştur",
                        "required_role": "radiologist",
                        "status": "draft"
                    },
                    {
                        "step_id": "review",
                        "name": "İncele",
                        "description": "Raporu incele ve yorum ekle",
                        "required_role": "radiologist",
                        "status": "in_review"
                    },
                    {
                        "step_id": "approve",
                        "name": "Onayla",
                        "description": "Raporu onayla",
                        "required_role": "clinician",
                        "status": "approved"
                    },
                    {
                        "step_id": "finalize",
                        "name": "Finalize Et",
                        "description": "Raporu finalize et",
                        "required_role": "admin",
                        "status": "finalized"
                    }
                ]
            },
            "urgent_report": {
                "name": "Acil Rapor Workflow",
                "description": "Acil PET/CT raporu için hızlı workflow",
                "steps": [
                    {
                        "step_id": "create",
                        "name": "Rapor Oluştur",
                        "description": "Acil rapor taslağını oluştur",
                        "required_role": "radiologist",
                        "status": "draft"
                    },
                    {
                        "step_id": "approve",
                        "name": "Hızlı Onay",
                        "description": "Acil raporu hızlı onayla",
                        "required_role": "radiologist",
                        "status": "approved"
                    },
                    {
                        "step_id": "finalize",
                        "name": "Finalize Et",
                        "description": "Acil raporu finalize et",
                        "required_role": "radiologist",
                        "status": "finalized"
                    }
                ]
            }
        }

    def _create_default_users(self):
        """Varsayılan kullanıcıları oluştur"""
        default_users = [
            User("admin_001", "admin", UserRole.ADMIN, "Sistem Yöneticisi", "admin@neuropetrix.com"),
            User("rad_001", "dr_smith", UserRole.RADIOLOGIST, "Dr. John Smith", "dr.smith@neuropetrix.com"),
            User("clin_001", "dr_jones", UserRole.CLINICIAN, "Dr. Sarah Jones", "dr.jones@neuropetrix.com"),
            User("tech_001", "tech_mike", UserRole.TECHNICIAN, "Mike Wilson", "mike.wilson@neuropetrix.com"),
            User("view_001", "viewer_anna", UserRole.VIEWER, "Anna Brown", "anna.brown@neuropetrix.com")
        ]
        
        for user in default_users:
            self.users[user.user_id] = user

    def create_workflow(self, report_id: str, title: str, template: str, created_by: str) -> WorkflowInstance:
        """Yeni workflow oluştur"""
        workflow_id = f"wf_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Template'i al
        template_data = self.workflow_templates.get(template, self.workflow_templates["standard_report"])
        
        # Workflow adımlarını oluştur
        steps = []
        for step_data in template_data["steps"]:
            step = WorkflowStep(
                step_id=step_data["step_id"],
                name=step_data["name"],
                description=step_data["description"],
                required_role=UserRole(step_data["required_role"]),
                status=WorkflowStatus(step_data["status"])
            )
            steps.append(step)
        
        # Workflow instance oluştur
        workflow = WorkflowInstance(
            workflow_id=workflow_id,
            report_id=report_id,
            title=title,
            current_status=WorkflowStatus.DRAFT,
            steps=steps,
            created_by=created_by,
            metadata={"template": template}
        )
        
        self.workflows[workflow_id] = workflow
        
        logger.info(f"Workflow oluşturuldu: {workflow_id}")
        return workflow

    def execute_action(self, workflow_id: str, action: WorkflowAction, user_id: str, 
                      comment: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Workflow aksiyonu çalıştır"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow bulunamadı: {workflow_id}")
            return False
        
        workflow = self.workflows[workflow_id]
        user = self.users.get(user_id)
        
        if not user:
            logger.error(f"Kullanıcı bulunamadı: {user_id}")
            return False
        
        # Kullanıcının bu aksiyonu yapma yetkisi var mı?
        if not self._can_execute_action(workflow, action, user):
            logger.error(f"Kullanıcı {user_id} aksiyon {action.value} yapamaz")
            return False
        
        # Aksiyonu çalıştır
        success = self._execute_workflow_action(workflow, action, user, comment, metadata)
        
        if success:
            workflow.updated_at = datetime.now()
            logger.info(f"Aksiyon {action.value} başarıyla çalıştırıldı: {workflow_id}")
        
        return success

    def _can_execute_action(self, workflow: WorkflowInstance, action: WorkflowAction, user: User) -> bool:
        """Kullanıcının aksiyonu yapma yetkisi var mı?"""
        # Admin her şeyi yapabilir
        if user.role == UserRole.ADMIN:
            return True
        
        # Mevcut duruma göre yetki kontrolü
        current_status = workflow.current_status
        
        if action == WorkflowAction.CREATE:
            return user.role in [UserRole.RADIOLOGIST, UserRole.CLINICIAN]
        
        elif action == WorkflowAction.REVIEW:
            return (current_status == WorkflowStatus.DRAFT and 
                   user.role == UserRole.RADIOLOGIST)
        
        elif action == WorkflowAction.APPROVE:
            return (current_status == WorkflowStatus.IN_REVIEW and 
                   user.role in [UserRole.CLINICIAN, UserRole.RADIOLOGIST])
        
        elif action == WorkflowAction.FINALIZE:
            return (current_status == WorkflowStatus.APPROVED and 
                   user.role in [UserRole.ADMIN, UserRole.RADIOLOGIST])
        
        elif action == WorkflowAction.REJECT:
            return user.role in [UserRole.CLINICIAN, UserRole.RADIOLOGIST, UserRole.ADMIN]
        
        elif action == WorkflowAction.COMMENT:
            return user.role in [UserRole.RADIOLOGIST, UserRole.CLINICIAN, UserRole.ADMIN]
        
        elif action == WorkflowAction.REQUEST_CONSULTATION:
            return user.role in [UserRole.RADIOLOGIST, UserRole.CLINICIAN]
        
        return False

    def _execute_workflow_action(self, workflow: WorkflowInstance, action: WorkflowAction, 
                               user: User, comment: Optional[str], metadata: Optional[Dict[str, Any]]) -> bool:
        """Workflow aksiyonunu çalıştır"""
        try:
            if action == WorkflowAction.CREATE:
                workflow.current_status = WorkflowStatus.DRAFT
                self._complete_step(workflow, "create", user.user_id, comment)
            
            elif action == WorkflowAction.REVIEW:
                workflow.current_status = WorkflowStatus.IN_REVIEW
                self._complete_step(workflow, "review", user.user_id, comment)
            
            elif action == WorkflowAction.APPROVE:
                workflow.current_status = WorkflowStatus.APPROVED
                self._complete_step(workflow, "approve", user.user_id, comment)
            
            elif action == WorkflowAction.FINALIZE:
                workflow.current_status = WorkflowStatus.FINALIZED
                self._complete_step(workflow, "finalize", user.user_id, comment)
            
            elif action == WorkflowAction.REJECT:
                workflow.current_status = WorkflowStatus.REJECTED
                self._add_comment(workflow, user.user_id, f"Reddedildi: {comment or 'Sebep belirtilmedi'}")
            
            elif action == WorkflowAction.COMMENT:
                self._add_comment(workflow, user.user_id, comment or "")
            
            elif action == WorkflowAction.REQUEST_CONSULTATION:
                self._add_comment(workflow, user.user_id, f"Danışmanlık istendi: {comment or ''}")
                if metadata:
                    workflow.metadata["consultation_request"] = metadata
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow aksiyonu hatası: {e}")
            return False

    def _complete_step(self, workflow: WorkflowInstance, step_id: str, user_id: str, comment: Optional[str]):
        """Workflow adımını tamamla"""
        for step in workflow.steps:
            if step.step_id == step_id:
                step.status = WorkflowStatus.APPROVED
                step.completed_by = user_id
                step.completed_at = datetime.now()
                if comment:
                    step.comments.append(f"{user_id}: {comment}")
                break

    def _add_comment(self, workflow: WorkflowInstance, user_id: str, comment: str):
        """Workflow'a yorum ekle"""
        if comment:
            # Son adıma yorum ekle
            if workflow.steps:
                last_step = workflow.steps[-1]
                last_step.comments.append(f"{user_id}: {comment}")

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Workflow durumunu getir"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            "workflow_id": workflow.workflow_id,
            "report_id": workflow.report_id,
            "title": workflow.title,
            "current_status": workflow.current_status.value,
            "created_by": workflow.created_by,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "description": step.description,
                    "required_role": step.required_role.value,
                    "status": step.status.value,
                    "completed_by": step.completed_by,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "comments": step.comments
                }
                for step in workflow.steps
            ],
            "metadata": workflow.metadata
        }

    def get_user_workflows(self, user_id: str) -> List[Dict[str, Any]]:
        """Kullanıcının workflow'larını getir"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        user_workflows = []
        
        for workflow in self.workflows.values():
            # Kullanıcının bu workflow'da işlem yapma yetkisi var mı?
            if self._can_view_workflow(workflow, user):
                workflow_status = self.get_workflow_status(workflow.workflow_id)
                if workflow_status:
                    user_workflows.append(workflow_status)
        
        return user_workflows

    def _can_view_workflow(self, workflow: WorkflowInstance, user: User) -> bool:
        """Kullanıcı workflow'u görüntüleyebilir mi?"""
        # Admin her şeyi görebilir
        if user.role == UserRole.ADMIN:
            return True
        
        # Oluşturan kişi görebilir
        if workflow.created_by == user.user_id:
            return True
        
        # Kullanıcının rolüne göre yetki
        if user.role in [UserRole.RADIOLOGIST, UserRole.CLINICIAN]:
            return True
        
        return False

    def get_available_actions(self, workflow_id: str, user_id: str) -> List[str]:
        """Kullanıcının yapabileceği aksiyonları getir"""
        if workflow_id not in self.workflows:
            return []
        
        workflow = self.workflows[workflow_id]
        user = self.users.get(user_id)
        
        if not user:
            return []
        
        available_actions = []
        
        for action in WorkflowAction:
            if self._can_execute_action(workflow, action, user):
                available_actions.append(action.value)
        
        return available_actions

    def get_workflow_templates(self) -> Dict[str, Any]:
        """Workflow şablonlarını getir"""
        return self.workflow_templates

    def get_users(self) -> List[Dict[str, Any]]:
        """Kullanıcıları getir"""
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active
            }
            for user in self.users.values()
        ]

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# Kullanım örneği
if __name__ == "__main__":
    # Test workflow oluştur
    workflow = workflow_engine.create_workflow(
        report_id="RPT_001",
        title="PET/CT Raporu - Hasta 12345",
        template="standard_report",
        created_by="rad_001"
    )
    
    print(f"Workflow oluşturuldu: {workflow.workflow_id}")
    
    # Aksiyonları test et
    workflow_engine.execute_action(workflow.workflow_id, WorkflowAction.REVIEW, "rad_001", "İnceleme tamamlandı")
    workflow_engine.execute_action(workflow.workflow_id, WorkflowAction.APPROVE, "clin_001", "Onaylandı")
    workflow_engine.execute_action(workflow.workflow_id, WorkflowAction.FINALIZE, "admin_001", "Finalize edildi")
    
    # Durumu kontrol et
    status = workflow_engine.get_workflow_status(workflow.workflow_id)
    print(f"Final durum: {status['current_status']}")
