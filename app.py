"""
초등 디지털 교과서 컨텐츠 생성기 - 메인 애플리케이션
"""
import streamlit as st

from src.Config.settings import settings
from src.Utils.session_manager import SessionManager
from src.UI.sidebar import SidebarUI
from src.UI.content_display import ContentDisplayUI
from src.Service.ai_service import ai_service


def main():
    """메인 애플리케이션 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.LAYOUT,
        initial_sidebar_state="collapsed",
    )
    
    # 세션 상태 초기화 (로컬 스토리지에서 컨텐츠 복원 포함)
    SessionManager.init_session_state()
    
    # 커스텀 CSS 추가
    st.markdown("""
    <style>
    /* 전체 앱 스타일 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: none;
    }
    
    /* 타이틀 스타일 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 헤더 스타일 */
    .content-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1.5rem;
        padding: 0.75rem 1rem;
        background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%);
        border-left: 4px solid #667eea;
        border-radius: 0.5rem;
    }
    
    /* 컬럼 스타일 */
    .main-content {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 1.5rem;
        margin: 0.5rem;
        min-height: 600px;
    }
    
    /* 사이드바 스타일 */
    .sidebar-content {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 1.5rem;
        margin: 0.5rem;
        min-height: 600px;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 0.5rem;
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 정보 박스 스타일 */
    .stInfo {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #38bdf8;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    /* 구분선 스타일 */
    .divider {
        width: 2px;
        background: linear-gradient(to bottom, #667eea, #764ba2);
        margin: 0 1rem;
        border-radius: 1px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 타이틀 표시
    st.markdown(f'<h1 class="main-title">{settings.APP_TITLE}</h1>', unsafe_allow_html=True)
    
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
        st.markdown('<div style="width: 2px; height: 600px; background: linear-gradient(to bottom, #667eea, #764ba2); margin: 0 auto; border-radius: 1px;"></div>', unsafe_allow_html=True)
    
    # 메인 컨텐츠 영역 (col2에 표시)
    with col2:
        ContentDisplayUI.render(config)


if __name__ == "__main__":
    main()
