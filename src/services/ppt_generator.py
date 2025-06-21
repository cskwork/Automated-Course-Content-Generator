"""
PowerPoint 생성 서비스
python-pptx를 사용하여 PPT 파일을 생성합니다.
"""
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False


class PPTGenerator:
    """PowerPoint 생성 클래스"""
    
    def __init__(self):
        self.prs = None
        self.slide_width = Inches(13.33) if PPTX_AVAILABLE else None
        self.slide_height = Inches(7.5) if PPTX_AVAILABLE else None
    
    def generate_ppt(self, course_data: Dict[str, Any]) -> Optional[str]:
        """
        코스 데이터를 기반으로 PowerPoint 파일을 생성합니다.
        
        Args:
            course_data: 코스 데이터
            
        Returns:
            str: 생성된 PPT 파일 경로 (성공시), None (실패시)
        """
        if not PPTX_AVAILABLE:
            return None
        
        try:
            # 새 프레젠테이션 생성
            self.prs = Presentation()
            
            # 슬라이드 마스터 설정
            self._setup_slide_master()
            
            # 타이틀 슬라이드
            self._create_title_slide(course_data)
            
            # 목차 슬라이드
            if course_data.get('modules'):
                self._create_toc_slide(course_data)
            
            # 모듈 슬라이드들
            modules = course_data.get('modules', {})
            for module_name, module_content in modules.items():
                self._create_module_slides(module_name, module_content)
            
            # 퀴즈 슬라이드들
            quizzes = course_data.get('quizzes', {})
            for module_name, quiz_list in quizzes.items():
                self._create_quiz_slides(module_name, quiz_list)
            
            # 마무리 슬라이드
            self._create_ending_slide(course_data)
            
            # 파일 저장
            return self._save_ppt_file(course_data.get('title', 'course'))
            
        except Exception as e:
            print(f"PPT 생성 중 오류: {e}")
            return None
    
    def _setup_slide_master(self):
        """슬라이드 마스터 설정"""
        # 기본 레이아웃 사용
        pass
    
    def _create_title_slide(self, course_data: Dict[str, Any]):
        """타이틀 슬라이드 생성"""
        slide_layout = self.prs.slide_layouts[0]  # 타이틀 슬라이드 레이아웃
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목
        title = slide.shapes.title
        title.text = course_data.get('title', '디지털 교과서')
        
        # 부제목
        subtitle = slide.placeholders[1]
        subject = course_data.get('subject', '')
        level = course_data.get('education_level', '')
        subtitle.text = f"{subject} • {level}"
        
        # 폰트 설정
        self._set_font_style(title.text_frame, size=44, bold=True, color=RGBColor(102, 126, 234))
        self._set_font_style(subtitle.text_frame, size=24, color=RGBColor(113, 128, 150))
    
    def _create_toc_slide(self, course_data: Dict[str, Any]):
        """목차 슬라이드 생성"""
        slide_layout = self.prs.slide_layouts[1]  # 제목 및 내용 레이아웃
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목
        title = slide.shapes.title
        title.text = "📚 목차"
        self._set_font_style(title.text_frame, size=36, bold=True, color=RGBColor(102, 126, 234))
        
        # 내용
        content = slide.placeholders[1]
        text_frame = content.text_frame
        text_frame.clear()
        
        modules = course_data.get('modules', {})
        for i, module_name in enumerate(modules.keys(), 1):
            p = text_frame.paragraphs[0] if i == 1 else text_frame.add_paragraph()
            p.text = f"{i}. {module_name}"
            p.level = 0
            self._set_paragraph_style(p, size=20, color=RGBColor(45, 55, 72))
    
    def _create_module_slides(self, module_name: str, module_content: str):
        """모듈 슬라이드들 생성"""
        # 모듈 소개 슬라이드
        slide_layout = self.prs.slide_layouts[5]  # 빈 슬라이드
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목 추가
        title_box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(11.33), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = f"📖 {module_name}"
        self._set_font_style(title_frame, size=36, bold=True, color=RGBColor(102, 126, 234))
        
        # 컨텐츠를 슬라이드로 분할
        content_sections = self._split_content_for_ppt_slides(module_content)
        
        for i, section in enumerate(content_sections):
            self._create_content_slide(f"{module_name} (Part {i + 1})", section)
    
    def _create_content_slide(self, title: str, content: str):
        """내용 슬라이드 생성"""
        slide_layout = self.prs.slide_layouts[1]  # 제목 및 내용 레이아웃
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목
        slide.shapes.title.text = title
        self._set_font_style(slide.shapes.title.text_frame, size=32, bold=True, color=RGBColor(102, 126, 234))
        
        # 내용
        content_placeholder = slide.placeholders[1]
        text_frame = content_placeholder.text_frame
        text_frame.clear()
        
        # HTML 태그 제거 및 텍스트 정리
        clean_content = self._clean_content_for_ppt(content)
        
        # 문단별로 분할하여 추가
        paragraphs = clean_content.split('\n\n')
        for i, para in enumerate(paragraphs[:10]):  # 최대 10개 문단
            if para.strip():
                p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
                p.text = para.strip()
                self._set_paragraph_style(p, size=16, color=RGBColor(74, 85, 104))
    
    def _create_quiz_slides(self, module_name: str, quiz_list: List[Dict]):
        """퀴즈 슬라이드들 생성"""
        # 퀴즈 섹션 소개 슬라이드
        slide_layout = self.prs.slide_layouts[5]  # 빈 슬라이드
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목
        title_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.33), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = f"🧠 {module_name} 퀴즈"
        self._set_font_style(title_frame, size=36, bold=True, color=RGBColor(102, 126, 234))
        
        # 설명
        desc_box = slide.shapes.add_textbox(Inches(2), Inches(4), Inches(9.33), Inches(2))
        desc_frame = desc_box.text_frame
        desc_frame.text = f"총 {len(quiz_list)}개의 문제가 준비되어 있습니다.\n학습한 내용을 확인해보세요!"
        self._set_font_style(desc_frame, size=20, color=RGBColor(113, 128, 150))
        
        # 각 퀴즈를 개별 슬라이드로 생성
        for i, quiz in enumerate(quiz_list[:10]):  # 최대 10문제
            self._create_single_quiz_slide(quiz, i + 1)
    
    def _create_single_quiz_slide(self, quiz: Dict, question_number: int):
        """단일 퀴즈 슬라이드 생성"""
        slide_layout = self.prs.slide_layouts[1]  # 제목 및 내용 레이아웃
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목
        title = slide.shapes.title
        title.text = f"❓ 문제 {question_number}"
        self._set_font_style(title.text_frame, size=32, bold=True, color=RGBColor(102, 126, 234))
        
        # 질문 및 옵션
        content = slide.placeholders[1]
        text_frame = content.text_frame
        text_frame.clear()
        
        # 질문
        question_p = text_frame.paragraphs[0]
        question_p.text = quiz.get('question', '')
        self._set_paragraph_style(question_p, size=20, bold=True, color=RGBColor(45, 55, 72))
        
        # 빈 줄
        text_frame.add_paragraph()
        
        # 옵션들
        options = quiz.get('options', [])
        correct_answer = quiz.get('correct_answer', '')
        
        for i, option in enumerate(options):
            option_p = text_frame.add_paragraph()
            option_p.text = f"{chr(65 + i)}. {option}"
            
            # 정답은 다른 색상으로 표시
            if option == correct_answer:
                self._set_paragraph_style(option_p, size=16, color=RGBColor(56, 161, 105))  # 녹색
            else:
                self._set_paragraph_style(option_p, size=16, color=RGBColor(74, 85, 104))
    
    def _create_ending_slide(self, course_data: Dict[str, Any]):
        """마무리 슬라이드 생성"""
        slide_layout = self.prs.slide_layouts[5]  # 빈 슬라이드
        slide = self.prs.slides.add_slide(slide_layout)
        
        # 제목
        title_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11.33), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = "🎉 수고하셨습니다!"
        self._set_font_style(title_frame, size=40, bold=True, color=RGBColor(102, 126, 234))
        
        # 부제목
        subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(11.33), Inches(1))
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.text = f"{course_data.get('title', '디지털 교과서')} 완료"
        self._set_font_style(subtitle_frame, size=24, color=RGBColor(113, 128, 150))
        
        # 완료 메시지
        message_box = slide.shapes.add_textbox(Inches(2), Inches(4.5), Inches(9.33), Inches(2))
        message_frame = message_box.text_frame
        
        p1 = message_frame.paragraphs[0]
        p1.text = "🌟 모든 내용을 성공적으로 학습하셨습니다."
        self._set_paragraph_style(p1, size=18, color=RGBColor(74, 85, 104))
        
        p2 = message_frame.add_paragraph()
        p2.text = "계속해서 학습하시고 더 많은 지식을 쌓아가세요! 🚀"
        self._set_paragraph_style(p2, size=18, color=RGBColor(74, 85, 104))
    
    def _split_content_for_ppt_slides(self, content: str) -> List[str]:
        """PPT 슬라이드에 적합한 크기로 컨텐츠 분할"""
        # HTML 태그 제거
        clean_content = self._clean_content_for_ppt(content)
        
        # 섹션별로 분할
        sections = re.split(r'\n(?=#{1,3}\s)', clean_content)
        
        processed_sections = []
        for section in sections:
            if len(section) > 800:  # PPT는 더 적은 텍스트가 적합
                # 문단별로 분할
                paragraphs = section.split('\n\n')
                current_section = ""
                
                for paragraph in paragraphs:
                    if len(current_section + paragraph) > 600:
                        if current_section:
                            processed_sections.append(current_section.strip())
                            current_section = paragraph
                        else:
                            processed_sections.append(paragraph.strip())
                    else:
                        current_section += "\n\n" + paragraph if current_section else paragraph
                
                if current_section:
                    processed_sections.append(current_section.strip())
            else:
                processed_sections.append(section.strip())
        
        return [section for section in processed_sections if section]
    
    def _clean_content_for_ppt(self, content: str) -> str:
        """PPT용 컨텐츠 정리"""
        # HTML 태그 제거
        content = re.sub(r'<[^>]+>', '', content)
        
        # 이미지 플레이스홀더 제거
        content = re.sub(r'\[이미지:\s*.*?\]', '', content)
        
        # 여러 공백을 하나로
        content = re.sub(r'\s+', ' ', content)
        
        # 여러 줄바꿈을 두 개로
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return content.strip()
    
    def _set_font_style(self, text_frame, size: int = 18, bold: bool = False, color: RGBColor = None):
        """텍스트 프레임의 폰트 스타일 설정"""
        if not text_frame.paragraphs:
            return
        
        paragraph = text_frame.paragraphs[0]
        font = paragraph.runs[0].font if paragraph.runs else paragraph.font
        
        font.size = Pt(size)
        font.bold = bold
        if color:
            font.color.rgb = color
        
        # 텍스트 정렬
        paragraph.alignment = PP_ALIGN.CENTER if bold else PP_ALIGN.LEFT
    
    def _set_paragraph_style(self, paragraph, size: int = 16, bold: bool = False, color: RGBColor = None):
        """문단 스타일 설정"""
        run = paragraph.runs[0] if paragraph.runs else None
        if run:
            font = run.font
            font.size = Pt(size)
            font.bold = bold
            if color:
                font.color.rgb = color
    
    def _save_ppt_file(self, title: str) -> str:
        """PPT 파일 저장"""
        # 임시 디렉토리에 저장
        temp_dir = Path(tempfile.gettempdir()) / "course_ppts"
        temp_dir.mkdir(exist_ok=True)
        
        filename = f"{title}_presentation.pptx"
        file_path = temp_dir / filename
        
        self.prs.save(str(file_path))
        return str(file_path)
    
    @property
    def is_available(self) -> bool:
        """python-pptx 사용 가능 여부"""
        return PPTX_AVAILABLE


# 싱글톤 인스턴스
ppt_generator = PPTGenerator()