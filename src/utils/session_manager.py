"""
세션 상태 관리 유틸리티
"""
import shelve
import streamlit as st
import json
import os
from typing import Any, Dict, List

from src.config.settings import settings


class SessionManager:
    """Streamlit 세션 상태 관리"""
    
    @staticmethod
    def _ensure_logs_dir() -> None:
        """로그 디렉토리 생성 확인"""
        logs_dir = os.path.dirname(settings.CHAT_HISTORY_FILE)
        if logs_dir and not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
    
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
                st.session_state["ai_model"] = settings.OPENROUTER_DEFAULT_MODEL
            else:  # ollama
                st.session_state["ai_model"] = settings.OLLAMA_DEFAULT_MODEL
        
        # 메시지 기록 초기화
        if "messages" not in st.session_state:
            st.session_state.messages = SessionManager.load_chat_history()
        
        # 로컬 스토리지에서 생성된 컨텐츠 복원
        SessionManager.restore_content_from_storage()
    
    @staticmethod
    def load_chat_history() -> List[Dict[str, str]]:
        """채팅 기록 로드"""
        SessionManager._ensure_logs_dir()
        with shelve.open(settings.CHAT_HISTORY_FILE) as db:
            return db.get("messages", [])
    
    @staticmethod
    def save_chat_history(messages: List[Dict[str, str]]) -> None:
        """채팅 기록 저장"""
        SessionManager._ensure_logs_dir()
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
            'content_generated', 'generated_content', 'is_presentation'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        # 로컬 스토리지도 초기화
        SessionManager.clear_content_storage()
    
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
    
    @staticmethod
    def save_content_to_storage(content: str, is_presentation: bool = False) -> None:
        """생성된 컨텐츠를 로컬 스토리지에 저장"""
        content_data = {
            'generated_content': content,
            'is_presentation': is_presentation,
            'content_generated': True
        }
        
        # shelve를 사용해서 로컬에 저장
        SessionManager._ensure_logs_dir()
        with shelve.open(settings.CHAT_HISTORY_FILE) as db:
            db['saved_content'] = content_data
    
    @staticmethod
    def restore_content_from_storage() -> None:
        """로컬 스토리지에서 컨텐츠 복원"""
        try:
            SessionManager._ensure_logs_dir()
            with shelve.open(settings.CHAT_HISTORY_FILE) as db:
                if 'saved_content' in db:
                    content_data = db['saved_content']
                    
                    # 세션 상태에 복원 (새 생성 버튼이 눌리지 않았을 때만)
                    if not st.session_state.get('new_generation_requested', False):
                        st.session_state['generated_content'] = content_data.get('generated_content', '')
                        st.session_state['is_presentation'] = content_data.get('is_presentation', False)
                        st.session_state['content_generated'] = content_data.get('content_generated', False)
        except Exception as e:
            # 파일이 없거나 오류가 있는 경우 무시
            pass
    
    @staticmethod
    def clear_content_storage() -> None:
        """로컬 스토리지의 컨텐츠 삭제"""
        try:
            SessionManager._ensure_logs_dir()
            with shelve.open(settings.CHAT_HISTORY_FILE) as db:
                if 'saved_content' in db:
                    del db['saved_content']
        except Exception as e:
            # 파일이 없거나 오류가 있는 경우 무시
            pass
    
    @staticmethod
    def mark_new_generation() -> None:
        """새 생성 요청 표시"""
        st.session_state['new_generation_requested'] = True
    
    @staticmethod
    def clear_new_generation_flag() -> None:
        """새 생성 요청 플래그 초기화"""
        if 'new_generation_requested' in st.session_state:
            del st.session_state['new_generation_requested'] 
