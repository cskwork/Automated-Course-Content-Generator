"""
사이드바 UI 컴포넌트
"""
import streamlit as st
from typing import Dict, Any

from src.config.settings import settings
from src.utils.session_manager import SessionManager
from src.services.ai_service import ai_service


class SidebarUI:
    """사이드바 UI 클래스"""
    
    @staticmethod
    def render() -> Dict[str, Any]:
        """사이드바 렌더링 및 설정값 반환"""
        with st.sidebar:
            # 대화 기록 삭제 버튼
            if st.button("대화 기록 삭제"):
                SessionManager.clear_chat_history()
            
            st.header("교과서 설정 📋")
            
            # AI 설정
            ai_config = SidebarUI._render_ai_settings()
            
            st.divider()
            
            # 교과서 설정
            course_config = SidebarUI._render_course_settings()
            
            # 버튼 렌더링
            buttons = SidebarUI._render_buttons()
            
            # 모든 설정 통합
            config = {
                **ai_config,
                **course_config,
                **buttons
            }
            
            # 세션에 저장
            SessionManager.save_course_config(config)
            
            return config
    
    @staticmethod
    def _render_ai_settings() -> Dict[str, str]:
        """AI 제공자 및 모델 설정"""
        st.subheader("AI 설정")
        
        # AI 제공자 선택
        provider_options = ["openai", "openrouter", "ollama"]
        current_provider = SessionManager.get_session_value("ai_provider", settings.DEFAULT_PROVIDER)
        
        selected_provider = st.selectbox(
            "AI 제공자 선택",
            provider_options,
            index=provider_options.index(current_provider),
            help="사용할 AI 제공자를 선택하세요"
        )
        
        # 제공자 변경시 처리
        if selected_provider != current_provider:
            SessionManager.update_ai_settings(selected_provider, "")
            ai_service.initialize_client(selected_provider)
        
        # 모델 선택
        model_options = settings.MODEL_OPTIONS.get(selected_provider, [])
        if selected_provider == "ollama":
            # Ollama의 경우 동적으로 모델 목록 가져오기
            available_models = ai_service.get_available_models()
            if available_models:
                model_options = available_models
        
        current_model = SessionManager.get_session_value("ai_model", model_options[0] if model_options else "")
        
        selected_model = st.selectbox(
            "AI 모델 선택",
            model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            help="컨텐츠 생성에 사용할 AI 모델을 선택하세요"
        )
        
        SessionManager.update_ai_settings(selected_provider, selected_model)
        
        return {
            "provider": selected_provider,
            "model": selected_model
        }
    
    @staticmethod
    def _render_course_settings() -> Dict[str, Any]:
        """교과서 관련 설정"""
        # 과목 선택
        subject = st.selectbox("과목 선택", settings.SUBJECTS)
        
        # 학년 선택
        grade = st.selectbox("학년", settings.GRADES)
        
        # 학기 선택
        semester = st.selectbox("학기", settings.SEMESTERS)
        
        # 단원명 입력
        unit_name = st.text_input("단원명")
        
        # 학습 목표 입력
        learning_objectives = st.text_area("학습 목표", height=100)
        
        # 컨텐츠 유형 선택
        content_types = st.multiselect(
            "포함할 컨텐츠 유형",
            settings.CONTENT_TYPES,
            default=settings.DEFAULT_CONTENT_TYPES
        )
        
        # 내보내기 형식 선택
        export_format = st.radio(
            "내보내기 형식",
            settings.EXPORT_FORMATS
        )
        
        return {
            "subject": subject,
            "grade": grade,
            "semester": semester,
            "unit_name": unit_name,
            "learning_objectives": learning_objectives,
            "content_types": content_types,
            "export_format": export_format
        }
    
    @staticmethod
    def _render_buttons() -> Dict[str, bool]:
        """버튼 렌더링"""
        button1, button2 = st.columns([1, 0.8])
        
        with button1:
            generate_button = st.button(
                "컨텐츠 생성", 
                help="클릭하여 디지털 교과서 컨텐츠를 생성하세요! 🎯"
            )
        
        with button2:
            new_content_button = False
            if SessionManager.get_session_value("content_generated"):
                new_content_button = st.button(
                    "새 컨텐츠", 
                    help="새로운 컨텐츠를 만들어보세요! 💡"
                )
                
                if new_content_button:
                    SessionManager.reset_content_generation()
                    st.experimental_rerun()
        
        return {
            "generate_button": generate_button,
            "new_content_button": new_content_button
        } 