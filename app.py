"""
초등 디지털 교과서 컨텐츠 생성기 - 메인 애플리케이션
"""
import streamlit as st

from src.config.settings import settings
from src.utils.session_manager import SessionManager
from src.ui.sidebar import SidebarUI
from src.ui.content_display import ContentDisplayUI
from src.services.ai_service import ai_service


def main():
    """메인 애플리케이션 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.LAYOUT,
        initial_sidebar_state="collapsed",
    )
    
    # 타이틀 표시
    st.title(settings.APP_TITLE)
    
    # 세션 상태 초기화
    SessionManager.init_session_state()
    
    # AI 클라이언트 초기화
    provider = SessionManager.get_session_value("ai_provider")
    if provider and not ai_service.client:
        ai_service.initialize_client(provider)
    
    # 레이아웃 설정
    col1, col_divider, col2 = st.columns([3.0, 0.1, 7.0])
    
    # 사이드바 렌더링 (col1에 표시)
    with col1:
        config = SidebarUI.render()
    
    # 구분선
    with col_divider:
        pass
    
    # 메인 컨텐츠 영역 (col2에 표시)
    with col2:
        ContentDisplayUI.render(config)


if __name__ == "__main__":
    main()
