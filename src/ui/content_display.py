"""
컨텐츠 표시 UI 컴포넌트
"""
import streamlit as st
from typing import Dict, Any

from src.models.content_types import CourseConfig, GeneratedContent
from src.services.ai_service import ai_service
from src.services.image_service import image_service
from src.services.export_service import export_service
from src.utils.session_manager import SessionManager
from src.utils.validators import Validators


class ContentDisplayUI:
    """컨텐츠 표시 UI 클래스"""
    
    @staticmethod
    def render(config: Dict[str, Any]) -> None:
        """메인 컨텐츠 영역 렌더링"""
        st.header("생성된 교과서 컨텐츠 📝")
        
        # 컨텐츠 생성 버튼이 클릭되었을 때
        if config.get("generate_button") and not SessionManager.get_session_value("content_generated"):
            ContentDisplayUI._generate_content(config)
        
        # 생성된 컨텐츠 표시
        elif SessionManager.get_session_value("generated_content"):
            ContentDisplayUI._display_generated_content()
        
        # 초기 상태
        else:
            st.info("👈 왼쪽에서 설정을 입력하고 '컨텐츠 생성' 버튼을 클릭하세요.")
    
    @staticmethod
    def _generate_content(config: Dict[str, Any]) -> None:
        """컨텐츠 생성 처리"""
        # 입력값 검증
        is_valid, error_message = Validators.validate_course_config(config)
        if not is_valid:
            st.error(error_message)
            return
        
        # AI 클라이언트 초기화 확인
        if not ai_service.client:
            ai_service.initialize_client(config["provider"])
            if not ai_service.client:
                st.error("선택한 AI 제공자의 API 키를 .env 파일에 설정해주세요.")
                return
        
        # CourseConfig 객체 생성
        course_config = CourseConfig(
            subject=config["subject"],
            grade=config["grade"],
            semester=config["semester"],
            unit_name=config["unit_name"],
            learning_objectives=config["learning_objectives"],
            content_types=config["content_types"],
            export_format=config["export_format"],
            provider=config["provider"],
            model=config["model"]
        )
        
        # 메시지 기록에 추가
        SessionManager.set_session_value("messages", SessionManager.get_session_value("messages", []))
        messages = SessionManager.get_session_value("messages")
        messages.append({"role": "user", "content": course_config.to_prompt_string()})
        
        # 컨텐츠 생성
        with st.spinner("디지털 교과서 컨텐츠를 생성중입니다... 📚"):
            try:
                # AI를 통한 컨텐츠 생성
                generated_content = ai_service.generate_content(course_config)
                
                # 전체 HTML 포맷팅
                full_html = ContentDisplayUI._format_full_content(
                    config, 
                    generated_content,
                    course_config.subject
                )
                
                # 세션에 저장
                SessionManager.set_session_value("generated_content", full_html)
                SessionManager.set_session_value("content_generated", True)
                SessionManager.save_chat_history(messages)
                
                st.success("컨텐츠가 성공적으로 생성되었습니다! ✨")
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"컨텐츠 생성 중 오류가 발생했습니다: {str(e)}")
    
    @staticmethod
    def _format_full_content(config: Dict[str, Any], generated: GeneratedContent, subject: str) -> str:
        """생성된 컨텐츠를 전체 HTML로 포맷팅"""
        # 이미지 플레이스홀더 교체
        main_content_with_images = image_service.enhance_content_with_images(
            generated.main_content, subject
        )
        
        interactive_content_with_images = ""
        if generated.interactive_content:
            interactive_content_with_images = image_service.enhance_content_with_images(
                generated.interactive_content, subject
            )
        
        # HTML 포맷팅
        content_dict = {
            'main_content': main_content_with_images,
            'interactive_content': interactive_content_with_images,
            'quiz_content': generated.quiz_content or ""
        }
        
        return export_service.format_full_content(config, content_dict)
    
    @staticmethod
    def _display_generated_content() -> None:
        """생성된 컨텐츠 표시"""
        generated_content = SessionManager.get_session_value("generated_content")
        
        # 미리보기
        with st.expander("생성된 컨텐츠 미리보기"):
            st.markdown(generated_content, unsafe_allow_html=True)
        
        # 다운로드 버튼
        export_format = SessionManager.get_session_value("export_format")
        export_service.create_download_buttons(generated_content, export_format) 