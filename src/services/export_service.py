"""
파일 내보내기 서비스 (PDF, HTML)
"""
import unicodedata
import base64
from fpdf import FPDF  # type: ignore
import streamlit as st
import markdown2

from src.models.content_types import ExportFormat


class ExportService:
    """컨텐츠 내보내기 서비스"""
    
    @staticmethod
    def markdown_to_html(markdown_text: str) -> str:
        """마크다운을 HTML로 변환"""
        if not markdown_text:
            return ""
        
        # markdown2 extras 설정
        extras = [
            'tables',  # 테이블 지원
            'fenced-code-blocks',  # 코드 블록 지원
            'cuddled-lists',  # 리스트 처리 개선
            'break-on-newline',  # 줄바꿈 처리
            'header-ids',  # 헤더에 ID 자동 생성
            'task_list',  # 체크박스 리스트 지원
        ]
        
        # 마크다운을 HTML로 변환
        html_content = markdown2.markdown(markdown_text, extras=extras)
        
        # 추가 스타일링을 위한 CSS 클래스 적용
        # 헤딩 스타일
        html_content = html_content.replace('<h1>', '<h1 class="md-h1">')
        html_content = html_content.replace('<h2>', '<h2 class="md-h2">')
        html_content = html_content.replace('<h3>', '<h3 class="md-h3">')
        
        # 리스트 스타일
        html_content = html_content.replace('<ul>', '<ul class="md-list">')
        html_content = html_content.replace('<ol>', '<ol class="md-list-ordered">')
        
        # 코드 블록 스타일
        html_content = html_content.replace('<pre>', '<pre class="md-code-block">')
        html_content = html_content.replace('<code>', '<code class="md-code">')
        
        # 테이블 스타일
        html_content = html_content.replace('<table>', '<table class="md-table">')
        
        return html_content
    
    @staticmethod
    def generate_pdf(content: str, filename: str) -> FPDF:
        """PDF 파일 생성"""
        # 유니코드 정규화
        content = unicodedata.normalize('NFKD', content).encode('utf-8', 'ignore').decode('utf-8')
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, content)
        pdf.output(filename, 'F')
        return pdf
    
    @staticmethod
    def generate_html(content: str, filename: str) -> str:
        """HTML 파일 생성"""
        html_template = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>디지털 교과서 컨텐츠</title>
            <style>
                body {{
                    font-family: 'Noto Sans KR', sans-serif;
                    line-height: 1.8;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                }}
                .module {{
                    background: white;
                    padding: 30px;
                    margin-bottom: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
                }}
                /* 마크다운 변환 스타일 */
                .md-h1 {{
                    font-size: 2em;
                    margin: 1em 0 0.5em 0;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 0.3em;
                }}
                .md-h2 {{
                    font-size: 1.5em;
                    margin: 0.8em 0 0.4em 0;
                    color: #444;
                }}
                .md-h3 {{
                    font-size: 1.2em;
                    margin: 0.6em 0 0.3em 0;
                    color: #555;
                }}
                .md-list {{
                    margin: 1em 0;
                    padding-left: 2em;
                }}
                .md-list li {{
                    margin: 0.3em 0;
                }}
                .md-code-block {{
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 1em;
                    overflow-x: auto;
                    margin: 1em 0;
                }}
                .md-code {{
                    background: #f0f0f0;
                    padding: 0.2em 0.4em;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                .md-table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                .md-table th, .md-table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                .md-table th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                .md-table tr:hover {{
                    background-color: #fafafa;
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
                .image-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .image-container img {{
                    max-width: 100%;
                    height: auto;
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
                /* 체크박스 리스트 스타일 */
                input[type="checkbox"] {{
                    margin-right: 0.5em;
                }}
                /* 인용문 스타일 */
                blockquote {{
                    border-left: 4px solid #ccc;
                    margin: 1em 0;
                    padding-left: 1em;
                    color: #666;
                }}
            </style>
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap" rel="stylesheet">
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_template.format(content=content))
        
        return filename
    
    @staticmethod
    def create_download_buttons(content: str, format_type: str) -> None:
        """다운로드 버튼 생성"""
        col1, col2 = st.columns(2)
        
        if format_type in [ExportFormat.HTML.value, ExportFormat.BOTH.value]:
            with col1:
                # HTML 파일 생성
                html_file = ExportService.generate_html(content, "digital_textbook.html")
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_data = f.read()
                st.download_button(
                    label="HTML로 다운로드 🌐",
                    data=html_data,
                    file_name="digital_textbook.html",
                    mime="text/html"
                )
        
        if format_type in [ExportFormat.PDF.value, ExportFormat.BOTH.value]:
            with col2:
                try:
                    # PDF 생성
                    pdf = ExportService.generate_pdf(content, "digital_textbook.pdf")
                    b64 = base64.b64encode(pdf.output(dest="S").encode('latin1')).decode()
                    st.download_button(
                        label="PDF로 다운로드 📄",
                        data=b64,
                        file_name="digital_textbook.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.warning(f"PDF 생성 중 오류가 발생했습니다: {str(e)}. HTML 형식을 사용해주세요.")
    
    @staticmethod
    def format_full_content(config: dict, generated_content: dict) -> str:
        """전체 컨텐츠 포맷팅"""
        main_content = generated_content.get('main_content', '')
        interactive_content = generated_content.get('interactive_content', '')
        quiz_content = generated_content.get('quiz_content', '')
        
        # 마크다운을 HTML로 변환
        main_content_html = ExportService.markdown_to_html(main_content)
        interactive_content_html = ExportService.markdown_to_html(interactive_content) if interactive_content else ''
        quiz_content_html = ExportService.markdown_to_html(quiz_content) if quiz_content else ''
        
        return f"""
        <div class="module">
            <h1>{config['grade']} {config['semester']} - {config['unit_name']}</h1>
            <h2>학습 목표</h2>
            <p>{config['learning_objectives']}</p>
            
            <div class="content">
                {main_content_html}
            </div>
            
            {f'<div class="interactive"><h3>상호작용 활동</h3>{interactive_content_html}</div>' if interactive_content_html else ''}
            
            {f'<div class="quiz"><h3>퀴즈</h3>{quiz_content_html}</div>' if quiz_content_html else ''}
        </div>
        """


# 싱글톤 인스턴스
export_service = ExportService() 