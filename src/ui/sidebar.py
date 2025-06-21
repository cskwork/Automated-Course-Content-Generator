"""
사이드바 UI 컴포넌트
"""
import streamlit as st
from typing import Dict, Any
import torch

from src.config.settings import settings
from src.utils.session_manager import SessionManager
from src.services.ai_service import ai_service


class SidebarUI:
    """사이드바 UI 클래스"""
    
    @staticmethod
    def render() -> Dict[str, Any]:
        """사이드바 렌더링 및 설정값 반환"""
        # 대화 기록 삭제 버튼
        if st.button("대화 기록 삭제"):
            SessionManager.clear_chat_history()
        
        # 환경 변수 다시 로드 버튼
        if st.button("환경 변수 다시 로드"):
            # 세션 상태 AI 설정 초기화
            if "ai_provider" in st.session_state:
                del st.session_state["ai_provider"]
            if "ai_model" in st.session_state:
                del st.session_state["ai_model"]
            # 환경 변수 다시 로드
            from dotenv import load_dotenv
            load_dotenv(override=True)
            st.rerun()
        
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
            help="사용할 AI 제공자를 선택하세요",
            key="provider_select"
        )
        
        # 제공자 변경시 처리
        if selected_provider != current_provider:
            # 제공자별 기본 모델 설정
            if selected_provider == "openai":
                default_model_for_provider = "gpt-4"
            elif selected_provider == "openrouter":
                default_model_for_provider = settings.OPENROUTER_DEFAULT_MODEL
            else:  # ollama
                default_model_for_provider = settings.OLLAMA_DEFAULT_MODEL
            
            SessionManager.update_ai_settings(selected_provider, default_model_for_provider)
            ai_service.initialize_client(selected_provider)
            st.rerun()  # UI 즉시 업데이트를 위한 rerun
        
        # 모델 선택
        model_options = settings.MODEL_OPTIONS.get(selected_provider, [])
        if selected_provider == "ollama":
            # Ollama의 경우 동적으로 모델 목록 가져오기
            available_models = ai_service.get_available_models()
            if available_models:
                model_options = available_models
        
        
        # 기본 모델 설정
        default_model = ""
        if selected_provider == "openai":
            default_model = "gpt-4"
        elif selected_provider == "openrouter":
            default_model = settings.OPENROUTER_DEFAULT_MODEL
        elif selected_provider == "ollama":
            default_model = settings.OLLAMA_DEFAULT_MODEL
        
        current_model = SessionManager.get_session_value("ai_model", default_model)
        
        # 현재 모델이 모델 옵션에 없으면 추가
        if current_model and current_model not in model_options:
            model_options = [current_model] + model_options
        
        # 모델 입력 방식 선택
        model_input_type = st.radio("모델 선택 방식", ["목록에서 선택", "직접 입력"], horizontal=True)
        
        if model_input_type == "목록에서 선택":
            selected_model = st.selectbox(
                "AI 모델 선택",
                model_options,
                index=model_options.index(current_model) if current_model in model_options else 0,
                help="컨텐츠 생성에 사용할 AI 모델을 선택하세요",
                key=f"model_select_{selected_provider}"
            )
        else:
            selected_model = st.text_input(
                "AI 모델명 직접 입력",
                value=current_model,
                help="사용할 모델명을 직접 입력하세요 (예: google/gemini-2.5-flash-lite-preview-06-17)",
                key=f"model_input_{selected_provider}"
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
        
        # 이미지 생성 설정
        use_stable_diffusion_toggle = st.toggle(
            "Stable Diffusion 이미지 사용",
            value=settings.USE_STABLE_DIFFUSION,
            help="활성화하면 Stable Diffusion을 사용하여 이미지를 생성합니다. .env 파일의 기본값을 따릅니다.",
            key="sd_toggle"
        )
        
        use_stable_diffusion = use_stable_diffusion_toggle
        
        # GPU가 없고 Stable Diffusion이 활성화된 경우 CPU 사용 여부 확인
        if use_stable_diffusion_toggle and not torch.cuda.is_available():
            st.warning("GPU가 감지되지 않았습니다. CPU 사용은 매우 느릴 수 있습니다.")
            use_cpu = st.checkbox(
                "CPU로 이미지 생성하기", 
                value=False,
                key="use_cpu_for_sd"
            )
            if not use_cpu:
                use_stable_diffusion = False
        
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
            "use_stable_diffusion": use_stable_diffusion,
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
                    st.rerun()
        
        return {
            "generate_button": generate_button,
            "new_content_button": new_content_button
        } 