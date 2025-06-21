"""
파일 내보내기 서비스 (PDF, HTML)
"""
import unicodedata
import base64
from fpdf import FPDF  # type: ignore
import streamlit as st

from src.models.content_types import ExportFormat


class ExportService:
    """컨텐츠 내보내기 서비스"""
    
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
        
        return f"""
        <div class="module">
            <h1>{config['grade']} {config['semester']} - {config['unit_name']}</h1>
            <h2>학습 목표</h2>
            <p>{config['learning_objectives']}</p>
            
            <div class="content">
                {main_content}
            </div>
            
            {f'<div class="interactive"><h3>상호작용 활동</h3>{interactive_content}</div>' if interactive_content else ''}
            
            {f'<div class="quiz"><h3>퀴즈</h3>{quiz_content}</div>' if quiz_content else ''}
        </div>
        """


# 싱글톤 인스턴스
export_service = ExportService() 