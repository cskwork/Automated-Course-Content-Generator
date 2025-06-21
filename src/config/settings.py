"""
애플리케이션 설정 관리
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(override=True)


class Settings:
    """애플리케이션 설정 클래스"""
    
    # 앱 기본 설정
    APP_TITLE = "🇰🇷 초등 디지털 교과서 컨텐츠 생성기 📚"
    PAGE_ICON = "📚"
    LAYOUT = "wide"
    
    # AI 제공자 설정 (동적 속성)
    @property
    def OPENAI_API_KEY(self):
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def OPENROUTER_API_KEY(self):
        return os.getenv("OPENROUTER_API_KEY")
    
    @property
    def OPENROUTER_BASE_URL(self):
        return os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    @property
    def OPENROUTER_DEFAULT_MODEL(self):
        return os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4")
    
    @property
    def OLLAMA_HOST(self):
        return os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    @property
    def OLLAMA_DEFAULT_MODEL(self):
        return os.getenv("OLLAMA_DEFAULT_MODEL", "gemma3:latest")
    
    @property
    def DEFAULT_PROVIDER(self):
        return os.getenv("MODEL_SELECTION", "openai")
    
    # Unsplash API 설정
    @property
    def UNSPLASH_API_KEY(self):
        return os.getenv("UNSPLASH_API_KEY")
    
    # 모델 옵션
    MODEL_OPTIONS: Dict[str, list] = {
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "openrouter": [
            "openai/gpt-3.5-turbo",
            "openai/gpt-4",
            "openai/gpt-4-turbo",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro",
            "google/gemini-2.5-flash-lite-preview-06-17"
        ],
        "ollama": ["gemma3:latest", "llama3.2", "llama3.1", "codellama", "mistral", "qwen2.5"]
    }
    
    # UI 설정
    GRADES = ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"]
    SUBJECTS = ["영어", "수학"]
    SEMESTERS = ["1학기", "2학기"]
    CONTENT_TYPES = ["개념 설명", "예시 문제", "상호작용 활동", "시각 자료", "퀴즈", "게임형 학습"]
    DEFAULT_CONTENT_TYPES = ["개념 설명", "예시 문제", "상호작용 활동", "퀴즈"]
    EXPORT_FORMATS = ["HTML", "PDF", "PPT", "둘 다"]
    
    # 파일 설정
    CHAT_HISTORY_FILE = "chat_history"
    OUTPUT_DIR = "output"
    
    # 이미지 검색 설정
    EDUCATIONAL_KEYWORDS = {
        "영어": "english learning kids education",
        "수학": "mathematics education kids learning"
    }
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """모든 설정값을 딕셔너리로 반환"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and not callable(getattr(cls, key))
        }
    
    @classmethod
    def validate_settings(cls) -> bool:
        """필수 설정값 검증"""
        required = {
            "openai": ["OPENAI_API_KEY"],
            "openrouter": ["OPENROUTER_API_KEY"],
            "ollama": []  # Ollama는 API 키 불필요
        }
        
        provider = cls.DEFAULT_PROVIDER
        if provider in required:
            for key in required[provider]:
                if not getattr(cls, key):
                    return False
        return True


# 싱글톤 인스턴스
settings = Settings() 