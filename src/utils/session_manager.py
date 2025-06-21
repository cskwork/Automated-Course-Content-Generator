"""
세션 상태 관리 유틸리티
"""
import shelve
import streamlit as st
from typing import Any, Dict, List

from src.config.settings import settings


class SessionManager:
    """Streamlit 세션 상태 관리"""
    
    @staticmethod
    def init_session_state() -> None:
        """세션 상태 초기화"""
        # AI 설정 초기화
        if "ai_provider" not in st.session_state:
            st.session_state["ai_provider"] = settings.DEFAULT_PROVIDER
        
        if "ai_model" not in st.session_state:
            provider = st.session_state["ai_provider"]
            if provider == "openai":
                st.session_state["ai_model"] = "gpt-4"
            elif provider == "openrouter":
                st.session_state["ai_model"] = "openai/gpt-4"
            else:  # ollama
                st.session_state["ai_model"] = settings.OLLAMA_DEFAULT_MODEL
        
        # 메시지 기록 초기화
        if "messages" not in st.session_state:
            st.session_state.messages = SessionManager.load_chat_history()
    
    @staticmethod
    def load_chat_history() -> List[Dict[str, str]]:
        """채팅 기록 로드"""
        with shelve.open(settings.CHAT_HISTORY_FILE) as db:
            return db.get("messages", [])
    
    @staticmethod
    def save_chat_history(messages: List[Dict[str, str]]) -> None:
        """채팅 기록 저장"""
        with shelve.open(settings.CHAT_HISTORY_FILE) as db:
            db["messages"] = messages
    
    @staticmethod
    def clear_chat_history() -> None:
        """채팅 기록 삭제"""
        st.session_state.messages = []
        SessionManager.save_chat_history([])
    
    @staticmethod
    def get_session_value(key: str, default: Any = None) -> Any:
        """세션 값 가져오기"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set_session_value(key: str, value: Any) -> None:
        """세션 값 설정"""
        st.session_state[key] = value
    
    @staticmethod
    def update_ai_settings(provider: str, model: str) -> None:
        """AI 설정 업데이트"""
        st.session_state["ai_provider"] = provider
        st.session_state["ai_model"] = model
    
    @staticmethod
    def reset_content_generation() -> None:
        """컨텐츠 생성 상태 초기화"""
        keys_to_remove = [
            'subject', 'grade', 'semester', 'unit_name', 
            'learning_objectives', 'content_types', 
            'content_generated', 'generated_content'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def save_course_config(config: Dict[str, Any]) -> None:
        """교과서 설정 저장"""
        for key, value in config.items():
            st.session_state[key] = value
    
    @staticmethod
    def get_course_config() -> Dict[str, Any]:
        """교과서 설정 가져오기"""
        return {
            'subject': st.session_state.get('subject'),
            'grade': st.session_state.get('grade'),
            'semester': st.session_state.get('semester'),
            'unit_name': st.session_state.get('unit_name'),
            'learning_objectives': st.session_state.get('learning_objectives'),
            'content_types': st.session_state.get('content_types', []),
            'export_format': st.session_state.get('export_format'),
            'provider': st.session_state.get('ai_provider'),
            'model': st.session_state.get('ai_model')
        } 