"""
컨텐츠 관련 데이터 모델
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Provider(Enum):
    """AI 제공자 열거형"""
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class ExportFormat(Enum):
    """내보내기 형식 열거형"""
    HTML = "HTML"
    PDF = "PDF"
    BOTH = "둘 다"


@dataclass
class CourseConfig:
    """교과서 설정 데이터 클래스"""
    subject: str
    grade: str
    semester: str
    unit_name: str
    learning_objectives: str
    content_types: List[str]
    export_format: str
    provider: str = "openai"
    model: str = "gpt-4"
    
    def to_prompt_string(self) -> str:
        """프롬프트용 문자열로 변환"""
        return f"""
        과목: {self.subject}
        학년: {self.grade}
        학기: {self.semester}
        단원명: {self.unit_name}
        학습 목표: {self.learning_objectives}
        컨텐츠 유형: {', '.join(self.content_types)}
        """


@dataclass
class ImageInfo:
    """이미지 정보 데이터 클래스"""
    id: str
    url: str
    thumb_url: str
    description: str
    author: str
    author_url: str
    
    def to_html(self, placeholder: str) -> str:
        """HTML 태그로 변환"""
        return f'''
        <div class="image-container">
            <img src="{self.url}" alt="{placeholder}" style="width: 100%; max-width: 600px; border-radius: 8px;">
            <p class="image-caption">
                <small>{placeholder} - Photo by <a href="{self.author_url}?utm_source=course_generator&utm_medium=referral" target="_blank">{self.author}</a> on <a href="https://unsplash.com/?utm_source=course_generator&utm_medium=referral" target="_blank">Unsplash</a></small>
            </p>
        </div>
        '''


@dataclass
class GeneratedContent:
    """생성된 컨텐츠 데이터 클래스"""
    main_content: str
    interactive_content: Optional[str] = None
    quiz_content: Optional[str] = None
    full_html: Optional[str] = None
    
    def has_content(self) -> bool:
        """컨텐츠 존재 여부 확인"""
        return bool(self.main_content) 