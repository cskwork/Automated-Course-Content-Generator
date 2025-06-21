"""
슬라이드 생성 서비스
PPT 스타일의 HTML 슬라이드를 생성합니다.
"""
import os
import re
import base64
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path

# 프롬프트 import
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.Prompts.slide_prompt import get_slide_optimization_prompt
from src.Service.image_service import image_service


class SlideGenerator:
    """슬라이드 생성 클래스"""
    
    def __init__(self, ai_client=None):
        self.template_path = Path(__file__).parent.parent / "templates" / "slide_template.html"
        self.ai_client = ai_client
        self.image_generator = "Unsplash"
        self.subject = "default"
    
    def generate_slides_html(self, course_data: Dict[str, Any]) -> str:
        """
        코스 데이터를 기반으로 슬라이드 HTML을 생성합니다.
        
        Args:
            course_data: 코스 데이터 (제목, 모듈, 퀴즈 등)
            
        Returns:
            str: 완성된 HTML 문자열
        """
        # 이미지 생성 옵션 설정
        self.image_generator = course_data.get('image_generator', 'Unsplash')
        self.subject = course_data.get('subject', 'default')

        # 템플릿 로드
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 슬라이드 컨텐츠 생성
        slides_content = self._generate_slides_content(course_data)
        total_slides = len(self._extract_slides_from_content(slides_content))
        
        # 템플릿 변수 치환
        html_content = template.replace('{{course_title}}', course_data.get('title', '디지털 교과서'))
        html_content = html_content.replace('{{slides_content}}', slides_content)
        html_content = html_content.replace('{{total_slides}}', str(total_slides))
        
        return html_content
    
    def _generate_slides_content(self, course_data: Dict[str, Any]) -> str:
        """슬라이드 컨텐츠를 생성합니다."""
        slides = []
        
        # 타이틀 슬라이드
        title_slide = self._create_title_slide(course_data)
        slides.append(title_slide)
        
        # 목차 슬라이드
        if course_data.get('modules'):
            toc_slide = self._create_toc_slide(course_data)
            slides.append(toc_slide)
        
        # 각 모듈의 컨텐츠 슬라이드들
        modules = course_data.get('modules', {})
        for module_name, module_content in modules.items():
            module_slides = self._create_module_slides(module_name, module_content)
            slides.extend(module_slides)
        
        # 퀴즈 슬라이드들
        quizzes = course_data.get('quizzes', {})
        for module_name, quiz_list in quizzes.items():
            quiz_slides = self._create_quiz_slides(module_name, quiz_list)
            slides.extend(quiz_slides)
        
        # 마무리 슬라이드
        ending_slide = self._create_ending_slide(course_data)
        slides.append(ending_slide)
        
        return '\n'.join(slides)
    
    def _create_title_slide(self, course_data: Dict[str, Any]) -> str:
        """타이틀 슬라이드를 생성합니다."""
        title = course_data.get('title', '디지털 교과서')
        subject = course_data.get('subject', '')
        level = course_data.get('education_level', '')
        
        return f'''
        <div class="slide active">
            <div class="slide-header">
                <h1 class="slide-title">{title}</h1>
                <p class="slide-subtitle">{subject} • {level}</p>
            </div>
            <div class="slide-content">
                <div style="text-align: center; margin-top: 100px;">
                    <h2 style="color: #667eea; font-size: 2rem; margin-bottom: 30px;">
                        🎓 디지털 교과서에 오신 것을 환영합니다!
                    </h2>
                    <p style="font-size: 1.3rem; color: #718096; line-height: 1.8;">
                        이 교과서는 여러분의 학습을 돕기 위해 제작되었습니다.<br>
                        키보드 화살표 키나 하단 버튼을 사용해 슬라이드를 넘겨보세요.
                    </p>
                    <div style="margin-top: 50px; padding: 20px; background: #f7fafc; border-radius: 15px; border-left: 5px solid #667eea;">
                        <p><strong>🎯 학습 목표:</strong> 체계적이고 재미있는 학습 경험</p>
                        <p><strong>⏱️ 예상 시간:</strong> 자신만의 속도로</p>
                        <p><strong>🎮 상호작용:</strong> 퀴즈와 활동 포함</p>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    def _create_toc_slide(self, course_data: Dict[str, Any]) -> str:
        """목차 슬라이드를 생성합니다."""
        modules = course_data.get('modules', {})
        
        toc_items = []
        for i, module_name in enumerate(modules.keys(), 1):
            toc_items.append(f'<li style="margin: 15px 0; font-size: 1.2rem;"><strong>{i}.</strong> {module_name}</li>')
        
        toc_content = '\n'.join(toc_items)
        
        return f'''
        <div class="slide">
            <div class="slide-header">
                <h1 class="slide-title">📚 목차</h1>
                <p class="slide-subtitle">학습할 내용들을 살펴보세요</p>
            </div>
            <div class="slide-content">
                <ul style="list-style: none; padding: 0;">
                    {toc_content}
                </ul>
                <div style="margin-top: 50px; padding: 20px; background: #e6fffa; border-radius: 15px; border-left: 5px solid #38b2ac;">
                    <p style="color: #2d3748;"><strong>💡 학습 팁:</strong> 각 모듈을 차례대로 학습하면서 퀴즈로 실력을 확인해보세요!</p>
                </div>
            </div>
        </div>
        '''
    
    def _create_module_slides(self, module_name: str, module_content: str) -> List[str]:
        """모듈 컨텐츠를 여러 슬라이드로 분할합니다."""
        slides = []
        
        # 모듈 소개 슬라이드
        intro_slide = f'''
        <div class="slide">
            <div class="slide-header">
                <h1 class="slide-title">📖 {module_name}</h1>
                <p class="slide-subtitle">새로운 학습을 시작해볼까요?</p>
            </div>
            <div class="slide-content">
                <div style="text-align: center; margin-top: 80px;">
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px; border-radius: 20px; margin-bottom: 30px;">
                        <h2 style="color: white; margin-bottom: 20px;">🎯 {module_name}</h2>
                        <p style="font-size: 1.2rem;">이번 모듈에서는 새로운 개념들을 배워보겠습니다.</p>
                    </div>
                    <p style="font-size: 1.1rem; color: #718096;">다음 슬라이드에서 자세한 내용을 확인하세요!</p>
                </div>
            </div>
        </div>
        '''
        slides.append(intro_slide)
        
        # AI를 사용해 슬라이드 최적화된 콘텐츠 생성
        if self.ai_client:
            optimized_content = self._optimize_content_for_slides(module_content)
            slide_sections = self._parse_optimized_slides(optimized_content)
        else:
            # 기존 방식으로 폴백
            content_sections = self._split_content_for_slides(module_content)
            slide_sections = [(f"Part {i+1}", section) for i, section in enumerate(content_sections)]
        
        # 최적화된 슬라이드 생성
        for title, content in slide_sections:
            slide = f'''
            <div class="slide">
                <div class="slide-header">
                    <h1 class="slide-title">{module_name}</h1>
                    <p class="slide-subtitle">{title}</p>
                </div>
                <div class="slide-content">
                    {self._process_content_for_slide(content)}
                </div>
            </div>
            '''
            slides.append(slide)
        
        return slides
    
    def _create_quiz_slides(self, module_name: str, quiz_list: List[Dict]) -> List[str]:
        """퀴즈 슬라이드들을 생성합니다."""
        slides = []
        
        # 퀴즈 섹션 소개 슬라이드
        quiz_intro = f'''
        <div class="slide">
            <div class="slide-header">
                <h1 class="slide-title">🧠 {module_name} 퀴즈</h1>
                <p class="slide-subtitle">학습한 내용을 확인해보세요!</p>
            </div>
            <div class="slide-content">
                <div style="text-align: center; margin-top: 80px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 20px; margin-bottom: 30px;">
                        <h2 style="color: white; margin-bottom: 20px;">🎯 퀴즈 시간!</h2>
                        <p style="font-size: 1.2rem;">총 {len(quiz_list)}개의 문제가 준비되어 있습니다.</p>
                        <p style="font-size: 1rem; margin-top: 15px;">각 선택지를 클릭하면 정답을 확인할 수 있어요!</p>
                    </div>
                </div>
            </div>
        </div>
        '''
        slides.append(quiz_intro)
        
        # 각 퀴즈 문제를 개별 슬라이드로 생성
        if quiz_list and len(quiz_list) > 0:
            for i, quiz in enumerate(quiz_list[:10]):  # 최대 10문제만 표시
                if quiz:  # 퀴즈 데이터가 있는 경우만
                    quiz_slide = self._create_single_quiz_slide(quiz, i + 1)
                    slides.append(quiz_slide)
        
        return slides
    
    def _create_single_quiz_slide(self, quiz: Dict, question_number: int) -> str:
        """단일 퀴즈 슬라이드를 생성합니다."""
        # 안전한 데이터 접근
        if isinstance(quiz, str):
            question = quiz
            options = ['A', 'B', 'C', 'D']
            correct_answer = 'A'
        else:
            question = quiz.get('question', '') if isinstance(quiz, dict) else str(quiz)
            options = quiz.get('options', ['A', 'B', 'C', 'D']) if isinstance(quiz, dict) else ['A', 'B', 'C', 'D']
            correct_answer = quiz.get('correct_answer', 'A') if isinstance(quiz, dict) else 'A'
        
        options_html = []
        option_letters = ['A', 'B', 'C', 'D']
        for i, option in enumerate(options):
            option_letter = option_letters[i] if i < len(option_letters) else 'A'
            is_correct = option_letter == correct_answer
            options_html.append(f'''
                <li onclick="selectQuizOption(this, {str(is_correct).lower()})" 
                    data-correct="{str(is_correct).lower()}">
                    {option_letter}) {option}
                </li>
            ''')
        
        return f'''
        <div class="slide">
            <div class="slide-header">
                <h1 class="slide-title">❓ 문제 {question_number}</h1>
                <p class="slide-subtitle">정답을 클릭해보세요!</p>
            </div>
            <div class="slide-content">
                <div class="quiz-container">
                    <div class="quiz-question">{question}</div>
                    <ul class="quiz-options">
                        {''.join(options_html)}
                    </ul>
                </div>
                <div style="margin-top: 30px; padding: 15px; background: #fff5cd; border-radius: 10px; border-left: 4px solid #f6ad55;">
                    <p style="color: #744210;"><strong>💡 힌트:</strong> 신중하게 생각해보고 가장 적절한 답을 선택하세요!</p>
                </div>
            </div>
        </div>
        '''
    
    def _create_ending_slide(self, course_data: Dict[str, Any]) -> str:
        """마무리 슬라이드를 생성합니다."""
        title = course_data.get('title', '디지털 교과서')
        
        return f'''
        <div class="slide">
            <div class="slide-header">
                <h1 class="slide-title">🎉 수고하셨습니다!</h1>
                <p class="slide-subtitle">{title} 완료</p>
            </div>
            <div class="slide-content">
                <div style="text-align: center; margin-top: 60px;">
                    <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); color: white; padding: 40px; border-radius: 20px; margin-bottom: 30px;">
                        <h2 style="color: white; margin-bottom: 20px;">🌟 학습 완료!</h2>
                        <p style="font-size: 1.2rem;">모든 내용을 성공적으로 학습하셨습니다.</p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 40px;">
                        <div style="background: #f7fafc; padding: 20px; border-radius: 15px; border-left: 5px solid #48bb78;">
                            <h3 style="color: #2d3748; margin-bottom: 10px;">📚 학습 완료</h3>
                            <p style="color: #718096;">모든 모듈 학습</p>
                        </div>
                        <div style="background: #f7fafc; padding: 20px; border-radius: 15px; border-left: 5px solid #ed8936;">
                            <h3 style="color: #2d3748; margin-bottom: 10px;">🧠 퀴즈 도전</h3>
                            <p style="color: #718096;">실력 확인 완료</p>
                        </div>
                        <div style="background: #f7fafc; padding: 20px; border-radius: 15px; border-left: 5px solid #667eea;">
                            <h3 style="color: #2d3748; margin-bottom: 10px;">🎯 목표 달성</h3>
                            <p style="color: #718096;">학습 목표 성취</p>
                        </div>
                    </div>
                    
                    <p style="margin-top: 40px; font-size: 1.1rem; color: #4a5568;">
                        계속해서 학습하시고 더 많은 지식을 쌓아가세요! 🚀
                    </p>
                </div>
            </div>
        </div>
        '''
    
    def _split_content_for_slides(self, content: str) -> List[str]:
        """컨텐츠를 슬라이드에 적합한 크기로 분할합니다."""
        # 섹션별로 분할 (제목 기준)
        sections = re.split(r'\n(?=#{1,3}\s)', content)
        
        processed_sections = []
        for section in sections:
            if len(section.strip()) > 1500:  # 너무 긴 섹션은 더 작게 분할
                # 문단별로 분할
                paragraphs = section.split('\n\n')
                current_section = ""
                
                for paragraph in paragraphs:
                    if len(current_section + paragraph) > 1200:
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
    
    def _process_content_for_slide(self, content: str) -> str:
        """슬라이드용 컨텐츠를 HTML로 변환합니다."""
        # 볼드 텍스트 변환 (**text** -> <strong>text</strong>)
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        
        # 리스트 처리
        content = re.sub(r'^\- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'((?:<li>.*?</li>\s*)+)', r'<ul>\1</ul>', content, flags=re.DOTALL)
        
        # 문단 처리
        paragraphs = content.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and not paragraph.startswith('<'):
                paragraph = f'<p>{paragraph}</p>'
            processed_paragraphs.append(paragraph)
        
        return image_service.enhance_content_with_images(
            '\n'.join(processed_paragraphs), 
            self.subject, 
            self.image_generator
        )
    
    def _extract_slides_from_content(self, slides_content: str) -> List[str]:
        """슬라이드 컨텐츠에서 개별 슬라이드들을 추출합니다."""
        slides = re.findall(r'<div class="slide[^"]*">.*?</div>\s*(?=<div class="slide|$)', slides_content, re.DOTALL)
        return slides
    
    def save_html_file(self, html_content: str, filename: str = None) -> str:
        """HTML 파일로 저장하고 파일 경로를 반환합니다."""
        if filename is None:
            filename = f"course_slides_{int(__import__('time').time())}.html"
        
        # 임시 디렉토리에 저장
        temp_dir = Path(tempfile.gettempdir()) / "course_slides"
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(file_path)
    
    def get_html_download_link(self, html_content: str, filename: str) -> str:
        """HTML 다운로드 링크를 생성합니다."""
        b64_html = base64.b64encode(html_content.encode('utf-8')).decode()
        return f'data:text/html;charset=utf-8;base64,{b64_html}'
    
    def _optimize_content_for_slides(self, content: str) -> str:
        """AI를 사용해 콘텐츠를 슬라이드용으로 최적화합니다."""
        try:
            prompt = get_slide_optimization_prompt(content)
            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"슬라이드 최적화 중 오류 발생: {e}")
            return content
    
    def _parse_optimized_slides(self, optimized_content: str) -> List[tuple]:
        """최적화된 콘텐츠에서 개별 슬라이드를 파싱합니다."""
        slide_sections = []
        
        # ---SLIDE--- 패턴으로 분할
        slides = re.split(r'---SLIDE---', optimized_content)
        
        for slide_text in slides[1:]:  # 첫 번째는 빈 텍스트이므로 제외
            if '---END---' in slide_text:
                slide_content = slide_text.split('---END---')[0].strip()
                
                # 제목과 내용 분리
                lines = slide_content.split('\n')
                title = ""
                content_lines = []
                
                for line in lines:
                    if line.startswith('제목:'):
                        title = line.replace('제목:', '').strip()
                    elif line.startswith('내용:'):
                        continue  # 내용: 줄은 건너뛰기
                    elif line.strip():
                        content_lines.append(line)
                
                if not title:
                    title = f"슬라이드 {len(slide_sections) + 1}"
                
                content = '\n'.join(content_lines)
                if content.strip():
                    slide_sections.append((title, content))
        
        # 파싱 실패 시 기본 분할 방식 사용
        if not slide_sections:
            content_sections = self._split_content_for_slides(optimized_content)
            slide_sections = [(f"Part {i+1}", section) for i, section in enumerate(content_sections)]
        
        return slide_sections


# 싱글톤 인스턴스
slide_generator = SlideGenerator()