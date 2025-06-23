"""
컨텐츠 표시 UI 컴포넌트
"""
import streamlit as st
import streamlit.components.v1 as components
import html
from typing import Dict, Any

from src.entity.content_types import CourseConfig, GeneratedContent
from src.service.ai_service import ai_service
from src.service.image_service import image_service
from src.service.export_service import export_service
from src.service.slide_generator import slide_generator
from src.service.ppt_generator import ppt_generator
from src.utils.session_manager import SessionManager
from src.utils.validators import Validators
from src.config.settings import settings
from streamlit_quill import st_quill


class ContentDisplayUI:
    """컨텐츠 표시 UI 클래스"""
    
    @staticmethod
    def render(config: Dict[str, Any]) -> None:
        """메인 컨텐츠 영역 렌더링"""
        st.markdown('<h2 class="content-header">생성된 교과서 컨텐츠 📝</h2>', unsafe_allow_html=True)
        
        # 컨텐츠 생성 버튼이 클릭되었을 때
        if config.get("generate_button"):
            # 새 생성 요청 표시
            SessionManager.mark_new_generation()
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
            model=config["model"],
            image_generator=config.get("image_generator", "Unsplash"),
            local_files_only=config.get("local_files_only", False)
        )
        
        # 메시지 기록에 추가
        SessionManager.set_session_value("messages", SessionManager.get_session_value("messages", []))
        messages = SessionManager.get_session_value("messages")
        messages.append({"role": "user", "content": course_config.to_prompt_string()})
        
        # PPT 전용 생성인지 확인
        export_format = config.get("export_format", "HTML")
        is_presentation_only = export_format == "PPT"
        
        # 컨텐츠 생성
        spinner_text = "슬라이드를 생성중입니다... 🎯" if is_presentation_only else "디지털 교과서 컨텐츠를 생성중입니다... 📚"
        
        with st.spinner(spinner_text):
            try:
                if is_presentation_only:
                    # PPT 전용 생성
                    generated_content = ai_service.generate_content(course_config)
                    
                    # 슬라이드 생성기에 AI 클라이언트 전달
                    slide_gen = slide_generator
                    slide_gen.ai_client = ai_service.client
                    
                    # 퀴즈 데이터 처리
                    quiz_data = []
                    if generated_content.quiz_content:
                        if isinstance(generated_content.quiz_content, str):
                            # 구조화된 퀴즈 파싱
                            quiz_data = ContentDisplayUI._parse_quiz_content(generated_content.quiz_content)
                        elif isinstance(generated_content.quiz_content, list):
                            quiz_data = generated_content.quiz_content
                    
                    # 슬라이드 HTML 생성
                    course_data = {
                        'title': f"{course_config.grade} {course_config.subject} - {course_config.unit_name}",
                        'subject': course_config.subject,
                        'education_level': course_config.grade,
                        'modules': {course_config.unit_name: generated_content.main_content},
                        'quizzes': {course_config.unit_name: quiz_data},
                        'image_generator': course_config.image_generator
                    }
                    
                    slide_html = slide_gen.generate_slides_html(course_data)
                    
                    # 세션에 슬라이드 저장
                    SessionManager.set_session_value("generated_content", slide_html)
                    SessionManager.set_session_value("is_presentation", True)
                    
                    # 로컬 스토리지에 저장
                    SessionManager.save_content_to_storage(slide_html, True)
                    
                else:
                    # 기존 HTML 방식 생성
                    generated_content = ai_service.generate_content(course_config)
                    
                    # 전체 HTML 포맷팅
                    full_html = ContentDisplayUI._format_full_content(
                        config, 
                        generated_content,
                        course_config.subject
                    )
                    
                    # 세션에 저장
                    SessionManager.set_session_value("generated_content", full_html)
                    SessionManager.set_session_value("is_presentation", False)
                    
                    # 로컬 스토리지에 저장
                    SessionManager.save_content_to_storage(full_html, False)
                
                SessionManager.set_session_value("content_generated", True)
                SessionManager.set_session_value("image_generator", config.get("image_generator", "Unsplash"))
                SessionManager.set_session_value("local_files_only", config.get("local_files_only", False))
                SessionManager.save_chat_history(messages)
                
                # 새 생성 플래그 초기화
                SessionManager.clear_new_generation_flag()
                
                success_text = "슬라이드가 성공적으로 생성되었습니다! 🎯" if is_presentation_only else "컨텐츠가 성공적으로 생성되었습니다! ✨"
                st.success(success_text)
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"컨텐츠 생성 중 오류가 발생했습니다: {str(e)}")
    
    @staticmethod
    def _format_full_content(config: Dict[str, Any], generated: GeneratedContent, subject: str) -> str:
        """생성된 컨텐츠를 전체 HTML로 포맷팅"""
        image_generator = config.get("image_generator", "Unsplash")
        local_files_only = config.get("local_files_only", False)
        # 이미지 플레이스홀더 교체
        main_content_with_images = image_service.enhance_content_with_images(
            generated.main_content, subject, image_generator, local_files_only
        )
        
        interactive_content_with_images = ""
        if generated.interactive_content:
            interactive_content_with_images = image_service.enhance_content_with_images(
                generated.interactive_content, subject, image_generator, local_files_only
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
        is_presentation = SessionManager.get_session_value("is_presentation", False)
        
        # HTML 이스케이프 해제 (필요한 경우)
        if generated_content and '&lt;' in generated_content:
            generated_content = html.unescape(generated_content)
        
        # PPT인 경우 다른 방식으로 표시
        if is_presentation:
            st.markdown("### 🎯 생성된 슬라이드")
            
            # 편집 모드 관리 (슬라이드용)
            is_editing_slide = SessionManager.get_session_value("is_editing_slide", False)
            button_text_slide = "✏️ 편집 모드 닫기" if is_editing_slide else "✏️ 슬라이드 HTML 편집하기"
            
            if st.button(button_text_slide, key="edit_toggle_slide"):
                new_state = not is_editing_slide
                SessionManager.set_session_value("is_editing_slide", new_state)
                
                # 편집 모드 진입 시, st.session_state에 현재 컨텐츠를 저장
                if new_state:
                    st.session_state.slide_editor_quill = generated_content
                # 편집 모드 종료 시 (저장 안 함), st.session_state 정리
                elif "slide_editor_quill" in st.session_state:
                    del st.session_state.slide_editor_quill
                
                st.experimental_rerun()

            if is_editing_slide:
                st.info("아래 텍스트 상자에서 슬라이드의 HTML을 직접 수정할 수 있습니다. 수정 후 '변경사항 저장' 버튼을 클릭하세요.")
                
                # st.session_state의 값을 value로 명시적으로 전달
                edited_content_slide = st_quill(
                    value=st.session_state.get("slide_editor_quill", ""),
                    html=True,
                    key="slide_editor_quill"
                )

                if st.button("💾 변경사항 저장", key="save_changes_slide"):
                    # st_quill의 반환값(최신 편집 내용)을 저장
                    # 슬라이드는 전체 HTML 구조를 유지해야 하므로 직접 저장
                    SessionManager.set_session_value("generated_content", st.session_state.slide_editor_quill)
                    SessionManager.set_session_value("is_editing_slide", False)
                    # 상태 정리
                    if "slide_editor_quill" in st.session_state:
                        del st.session_state.slide_editor_quill
                    st.success("슬라이드가 성공적으로 업데이트되었습니다!")
                    st.experimental_rerun()
                
                if st.button("❌ 편집 취소", key="cancel_edit_slide"):
                    SessionManager.set_session_value("is_editing_slide", False)
                    # 상태 정리
                    if "slide_editor_quill" in st.session_state:
                        del st.session_state.slide_editor_quill
                    st.experimental_rerun()

            # 슬라이드 미리보기
            with st.expander("슬라이드 미리보기", expanded=not is_editing_slide):
                # 슬라이드 HTML을 iframe으로 표시
                components.html(generated_content, height=600, scrolling=True)
            
            # 다운로드 버튼
            st.download_button(
                label="슬라이드 HTML 다운로드",
                data=generated_content,
                file_name="slides.html",
                mime="text/html",
                help="슬라이드를 HTML 파일로 다운로드합니다"
            )
            
            return
        
        # 편집 모드 관리
        is_editing = SessionManager.get_session_value("is_editing", False)

        button_text = "✏️ 편집 모드 닫기" if is_editing else "✏️ 컨텐츠 편집하기"
        if st.button(button_text, key="edit_toggle"):
            new_state = not is_editing
            SessionManager.set_session_value("is_editing", new_state)

            # 편집 모드 진입 시, st.session_state에 현재 컨텐츠를 저장
            if new_state:
                st.session_state.content_editor_quill = generated_content
            # 편집 모드 종료 시 (저장 안 함), st.session_state 정리
            elif "content_editor_quill" in st.session_state:
                del st.session_state.content_editor_quill
            
            st.experimental_rerun()

        if is_editing:
            st.info("아래 텍스트 상자에서 HTML 형식의 콘텐츠를 직접 수정할 수 있습니다. 수정 후 '변경사항 저장' 버튼을 클릭하세요.")
            
            # st.session_state의 값을 value로 명시적으로 전달
            edited_content = st_quill(
                value=st.session_state.get("content_editor_quill", ""),
                html=True,
                key="content_editor_quill"
            )

            if st.button("💾 변경사항 저장", key="save_changes"):
                # st_quill의 반환값(최신 편집 내용)을 저장
                edited_body = st.session_state.content_editor_quill
                
                # 스타일이 포함된 전체 HTML로 재구성
                full_html_content = export_service.get_full_html_template(edited_body)
                
                SessionManager.set_session_value("generated_content", full_html_content)
                SessionManager.set_session_value("is_editing", False)
                # 상태 정리
                if "content_editor_quill" in st.session_state:
                    del st.session_state.content_editor_quill
                st.success("콘텐츠가 성공적으로 업데이트되었습니다!")
                st.experimental_rerun()
            
            if st.button("❌ 편집 취소", key="cancel_edit"):
                SessionManager.set_session_value("is_editing", False)
                # 상태 정리
                if "content_editor_quill" in st.session_state:
                    del st.session_state.content_editor_quill
                st.experimental_rerun()
        
        # 기존 방식 (일반 교과서 컨텐츠)
        with st.expander("생성된 컨텐츠 미리보기", expanded=not is_editing):
            # HTML 컨텐츠를 위한 전체 스타일과 함께 렌더링
            full_html = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        background-color: #ffffff;
                    }}
                    .module {{
                        background: white;
                        padding: 20px;
                        margin-bottom: 20px;
                        border-radius: 8px;
                    }}
                    .content {{
                        margin: 20px 0;
                    }}
                    .interactive {{
                        background: #e3f2fd;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 8px;
                        border-left: 4px solid #2196f3;
                    }}
                    .quiz {{
                        background: #fff3e0;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 8px;
                        border-left: 4px solid #ff9800;
                    }}
                    h1, h2, h3 {{
                        color: #333;
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    h1 {{ font-size: 1.8em; }}
                    h2 {{ font-size: 1.5em; }}
                    h3 {{ font-size: 1.2em; }}
                    p {{ margin: 1em 0; }}
                    ul, ol {{ margin: 1em 0; padding-left: 2em; }}
                    li {{ margin: 0.3em 0; }}
                    .image-container {{
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .image-container img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }}
                    .image-caption {{
                        margin-top: 10px;
                        color: #666;
                        font-size: 0.9em;
                    }}
                    .image-caption a {{
                        color: #2196f3;
                        text-decoration: none;
                    }}
                    .image-caption a:hover {{
                        text-decoration: underline;
                    }}
                    .image-placeholder {{
                        background: #f0f0f0;
                        padding: 40px;
                        text-align: center;
                        border-radius: 8px;
                        margin: 20px 0;
                        color: #666;
                        font-style: italic;
                    }}
                </style>
            </head>
            <body>
                {generated_content}
            </body>
            </html>
            """
            
            # HTML 컴포넌트로 렌더링
            components.html(full_html, height=800, scrolling=True)
        
        # 보기 모드 선택
        st.markdown("### 📋 보기 모드 선택")
        view_mode = st.radio(
            "컨텐츠를 어떤 형태로 보시겠습니까?",
            ["📄 기본 보기", "🎬 슬라이드 보기", "📱 모바일 보기"],
            horizontal=True
        )
        
        if view_mode == "🎬 슬라이드 보기":
            ContentDisplayUI._show_slide_view()
        elif view_mode == "📱 모바일 보기":
            ContentDisplayUI._show_mobile_view()
        
        # 다운로드 버튼
        st.markdown("### 💾 다운로드 옵션")
        
        # 기본 다운로드 (HTML/PDF)
        export_format = SessionManager.get_session_value("export_format")
        ContentDisplayUI._create_basic_download_buttons(generated_content, export_format)
        
        # 추가 다운로드 옵션
        st.markdown("#### 🎯 추가 다운로드 옵션")
        
        # 버튼들을 수직으로 배치 (컬럼 중첩 방지)
        if st.button("🎬 슬라이드 HTML 다운로드"):
            ContentDisplayUI._download_slide_html()
            
        if st.button("📄 PPT 다운로드"):
            ContentDisplayUI._download_ppt()
    
    @staticmethod
    def _show_slide_view() -> None:
        """슬라이드 형태로 컨텐츠 표시"""
        st.markdown("### 🎬 슬라이드 프레젠테이션")
        st.info("키보드 화살표 키나 하단 버튼을 사용해 슬라이드를 넘겨보세요!")
        
        # 저장된 컨텐츠를 슬라이드 데이터로 변환
        slide_data = ContentDisplayUI._convert_content_to_slide_data()
        
        if slide_data:
            # 슬라이드 HTML 생성
            slide_html = slide_generator.generate_slides_html(slide_data)
            
            # 슬라이드 컴포넌트 렌더링
            components.html(slide_html, height=700, scrolling=False)
        else:
            st.warning("슬라이드를 생성할 수 있는 컨텐츠가 없습니다.")
    
    @staticmethod
    def _show_mobile_view() -> None:
        """모바일 친화적인 형태로 컨텐츠 표시"""
        st.markdown("### 📱 모바일 보기")
        
        generated_content = SessionManager.get_session_value("generated_content")
        if generated_content:
            # 모바일 최적화 스타일 적용
            mobile_html = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 10px;
                        background-color: #f8f9fa;
                    }}
                    .mobile-container {{
                        max-width: 100%;
                        background: white;
                        border-radius: 12px;
                        padding: 16px;
                        margin-bottom: 16px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }}
                    h1 {{ font-size: 1.5em; color: #2c3e50; }}
                    h2 {{ font-size: 1.3em; color: #34495e; }}
                    h3 {{ font-size: 1.1em; color: #7f8c8d; }}
                    p {{ font-size: 1em; margin: 12px 0; }}
                    .image-container {{
                        text-align: center;
                        margin: 16px 0;
                    }}
                    .image-container img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 8px;
                    }}
                    .interactive, .quiz {{
                        background: #e8f4f8;
                        padding: 16px;
                        border-radius: 8px;
                        margin: 16px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="mobile-container">
                    {generated_content}
                </div>
            </body>
            </html>
            """
            
            components.html(mobile_html, height=600, scrolling=True)
        else:
            st.warning("표시할 컨텐츠가 없습니다.")
    
    @staticmethod
    def _convert_content_to_slide_data() -> dict:
        """저장된 컨텐츠를 슬라이드 데이터 형태로 변환"""
        # 세션에서 원본 데이터 가져오기
        generated_content = SessionManager.get_session_value("generated_content")
        if not generated_content:
            return None
        
        # 기본 구조 생성
        slide_data = {
            'title': SessionManager.get_session_value("unit_name", "디지털 교과서"),
            'subject': SessionManager.get_session_value("subject", ""),
            'education_level': SessionManager.get_session_value("grade", ""),
            'image_generator': SessionManager.get_session_value("image_generator", "Unsplash"),
            'local_files_only': SessionManager.get_session_value("local_files_only", False),
            'modules': {},
            'quizzes': {}
        }
        
        # HTML에서 모듈 정보 추출 (간단한 파싱)
        import re
        
        # 제목들을 찾아서 모듈로 구성
        h2_titles = re.findall(r'<h2[^>]*>(.*?)</h2>', generated_content, re.IGNORECASE)
        h3_titles = re.findall(r'<h3[^>]*>(.*?)</h3>', generated_content, re.IGNORECASE)
        
        # 컨텐츠를 섹션별로 분할
        sections = re.split(r'<h[23][^>]*>.*?</h[23]>', generated_content, flags=re.IGNORECASE)
        
        # 모듈 구성
        module_count = 1
        for i, title in enumerate(h2_titles[:5]):  # 최대 5개 모듈
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if clean_title:
                slide_data['modules'][f"모듈 {module_count}: {clean_title}"] = sections[i + 1] if i + 1 < len(sections) else ""
                module_count += 1
        
        # 기본 모듈이 없으면 전체 컨텐츠를 하나의 모듈로
        if not slide_data['modules']:
            slide_data['modules']['주요 내용'] = generated_content
        
        # 퀴즈 데이터 추가 (간단한 예시)
        if '퀴즈' in generated_content.lower() or 'quiz' in generated_content.lower():
            slide_data['quizzes']['퀴즈'] = [
                {
                    'question': '학습한 내용을 복습해보세요.',
                    'options': ['옵션 1', '옵션 2', '옵션 3', '옵션 4'],
                    'correct_answer': '옵션 1'
                }
            ]
        
        return slide_data
    
    @staticmethod
    def _download_slide_html() -> None:
        """슬라이드 HTML 파일 다운로드"""
        slide_data = ContentDisplayUI._convert_content_to_slide_data()
        
        if slide_data:
            # 슬라이드 HTML 생성
            slide_html = slide_generator.generate_slides_html(slide_data)
            
            # 다운로드 링크 생성
            download_link = slide_generator.get_html_download_link(
                slide_html, 
                f"{slide_data['title']}_slides.html"
            )
            
            st.markdown(
                f'<a href="{download_link}" download="{slide_data["title"]}_slides.html" '
                f'style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                f'color: white; padding: 12px 24px; text-decoration: none; '
                f'border-radius: 8px; font-weight: bold; display: inline-block;">'
                f'🎬 슬라이드 HTML 다운로드</a>',
                unsafe_allow_html=True
            )
        else:
            st.error("슬라이드를 생성할 수 있는 컨텐츠가 없습니다.")
    
    @staticmethod
    def _download_ppt() -> None:
        """PowerPoint 파일 다운로드"""
        if not ppt_generator.is_available:
            st.error("PowerPoint 생성 기능을 사용하려면 python-pptx 패키지가 필요합니다.")
            st.code("pip install python-pptx")
            return
        
        slide_data = ContentDisplayUI._convert_content_to_slide_data()
        
        if slide_data:
            with st.spinner("PowerPoint 파일을 생성중입니다..."):
                try:
                    ppt_file_path = ppt_generator.generate_ppt(slide_data)
                    
                    if ppt_file_path:
                        # 파일을 바이너리로 읽어서 다운로드 제공
                        with open(ppt_file_path, "rb") as f:
                            ppt_data = f.read()
                        
                        st.download_button(
                            label="📄 PowerPoint 다운로드",
                            data=ppt_data,
                            file_name=f"{slide_data['title']}_presentation.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                        st.success("PowerPoint 파일이 생성되었습니다!")
                    else:
                        st.error("PowerPoint 파일 생성에 실패했습니다.")
                        
                except Exception as e:
                    st.error(f"PowerPoint 생성 중 오류가 발생했습니다: {str(e)}")
        else:
            st.error("PowerPoint를 생성할 수 있는 컨텐츠가 없습니다.")
    
    @staticmethod
    def _create_basic_download_buttons(content: str, format_type: str) -> None:
        """기본 다운로드 버튼 생성 (컬럼 중첩 방지)"""
        from src.entity.content_types import ExportFormat
        
        # HTML 다운로드
        if format_type in [ExportFormat.HTML.value, ExportFormat.BOTH.value]:
            # HTML 파일 생성
            html_file = export_service.generate_html(content, "digital_textbook.html")
            with open(html_file, 'r', encoding='utf-8') as f:
                html_data = f.read()
            st.download_button(
                label="HTML로 다운로드 🌐",
                data=html_data,
                file_name="digital_textbook.html",
                mime="text/html"
            )
        
        # PDF 다운로드
        if format_type in [ExportFormat.PDF.value, ExportFormat.BOTH.value]:
            try:
                # PDF 파일 생성
                pdf_file = export_service.generate_pdf(content, "digital_textbook.pdf")
                with open(pdf_file, 'rb') as f:
                    pdf_data = f.read()
                st.download_button(
                    label="PDF로 다운로드 📄",
                    data=pdf_data,
                    file_name="digital_textbook.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
    
    @staticmethod
    def _parse_quiz_content(quiz_content: str) -> list:
        """구조화된 퀴즈 컨텐츠를 파싱하여 퀴즈 데이터 리스트로 변환"""
        import re
        
        quiz_data = []
        
        # Q1:, Q2: 패턴으로 각 문제를 분리
        quiz_pattern = r'Q\d+:\s*(.*?)(?=Q\d+:|$)'
        questions = re.findall(quiz_pattern, quiz_content.strip(), re.DOTALL)
        
        for question_block in questions:
            question_block = question_block.strip()
            if not question_block:
                continue
                
            try:
                # 문제와 선택지, 정답 분리
                lines = question_block.split('\n')
                question_text = ""
                options = []
                correct_answer = "A"
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # 첫 번째 비어있지 않은 줄이 문제
                    if not question_text and not line.startswith(('A)', 'B)', 'C)', 'D)', '정답:')):
                        question_text = line
                    # 선택지 파싱
                    elif line.startswith('A)'):
                        options.append(line[2:].strip())
                    elif line.startswith('B)'):
                        options.append(line[2:].strip())
                    elif line.startswith('C)'):
                        options.append(line[2:].strip())
                    elif line.startswith('D)'):
                        options.append(line[2:].strip())
                    # 정답 파싱
                    elif line.startswith('정답:'):
                        answer_match = re.search(r'정답:\s*([ABCD])', line)
                        if answer_match:
                            correct_answer = answer_match.group(1)
                
                # 유효한 데이터가 있으면 추가
                if question_text and len(options) == 4:
                    quiz_data.append({
                        'question': question_text,
                        'options': options,
                        'correct_answer': correct_answer
                    })
                    
            except Exception as e:
                # 파싱 실패한 경우 기본값으로 추가
                print(f"퀴즈 파싱 오류: {e}")
                if question_block:
                    quiz_data.append({
                        'question': question_block.split('\n')[0] if '\n' in question_block else question_block,
                        'options': ['선택지 1', '선택지 2', '선택지 3', '선택지 4'],
                        'correct_answer': 'A'
                    })
        
        # 최소 1개 문제는 보장
        if not quiz_data:
            quiz_data.append({
                'question': '다음 중 올바른 답을 선택하세요.',
                'options': ['선택지 1', '선택지 2', '선택지 3', '선택지 4'],
                'correct_answer': 'A'
            })
            
        return quiz_data 
