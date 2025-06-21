"""
AI 클라이언트 관리 및 컨텐츠 생성 서비스
"""
from typing import Optional, Tuple, List, Dict, Any
from openai import OpenAI
import ollama
import streamlit as st

from src.config.settings import settings
from src.models.content_types import Provider, CourseConfig, GeneratedContent
from prompts.elementary_english_prompt import ELEMENTARY_ENGLISH_PROMPT
from prompts.elementary_math_prompt import ELEMENTARY_MATH_PROMPT
from prompts.interactive_content_prompt import INTERACTIVE_CONTENT_PROMPT
from prompts.quiz_generator_prompt import QUIZ_GENERATOR_PROMPT


class AIService:
    """AI 서비스 클래스"""
    
    def __init__(self):
        self.client = None
        self.provider = None
    
    def initialize_client(self, provider: str) -> Tuple[Optional[Any], Optional[str]]:
        """AI 클라이언트 초기화"""
        try:
            if provider == Provider.OPENAI.value:
                if not settings.OPENAI_API_KEY:
                    st.error("OPENAI_API_KEY를 .env 파일에 설정해주세요")
                    return None, None
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.provider = provider
                return self.client, provider
            
            elif provider == Provider.OPENROUTER.value:
                if not settings.OPENROUTER_API_KEY:
                    st.error("OPENROUTER_API_KEY를 .env 파일에 설정해주세요")
                    return None, None
                self.client = OpenAI(
                    api_key=settings.OPENROUTER_API_KEY,
                    base_url=settings.OPENROUTER_BASE_URL
                )
                self.provider = provider
                return self.client, provider
            
            elif provider == Provider.OLLAMA.value:
                try:
                    client = ollama.Client(host=settings.OLLAMA_HOST)
                    client.list()  # 연결 테스트
                    self.client = client
                    self.provider = provider
                    return client, provider
                except Exception as e:
                    st.error(f"Ollama 연결 실패: {str(e)}. Ollama가 실행중인지 확인해주세요.")
                    return None, None
            
            return None, None
            
        except Exception as e:
            st.error(f"AI 클라이언트 초기화 오류: {str(e)}")
            return None, None
    
    def make_request(self, model: str, messages: List[Dict[str, str]]) -> str:
        """AI API 요청 수행"""
        if not self.client or not self.provider:
            raise ValueError("AI 클라이언트가 초기화되지 않았습니다.")
        
        if self.provider in [Provider.OPENAI.value, Provider.OPENROUTER.value]:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        
        elif self.provider == Provider.OLLAMA.value:
            response = self.client.chat(
                model=model,
                messages=messages
            )
            return response['message']['content']
        
        else:
            raise ValueError(f"지원하지 않는 제공자: {self.provider}")
    
    def get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 반환"""
        if self.provider == Provider.OLLAMA.value and self.client:
            try:
                available_models = self.client.list()
                return [model['name'] for model in available_models['models']]
            except:
                pass
        
        return settings.MODEL_OPTIONS.get(self.provider, [])
    
    def generate_content(self, config: CourseConfig) -> GeneratedContent:
        """교과서 컨텐츠 생성"""
        if not self.client:
            raise ValueError("AI 클라이언트가 초기화되지 않았습니다.")
        
        # 과목별 프롬프트 선택
        base_prompt = (ELEMENTARY_ENGLISH_PROMPT if config.subject == "영어" 
                      else ELEMENTARY_MATH_PROMPT)
        
        # 1. 기본 컨텐츠 생성
        content_prompt = f"""{base_prompt}
        
        학년: {config.grade}
        학기: {config.semester}
        단원명: {config.unit_name}
        학습 목표: {config.learning_objectives}
        
        다음 형식으로 컨텐츠를 생성해주세요:
        1. 도입부 (학습 동기 유발)
        2. 핵심 개념 설명 (이미지 위치 표시 포함)
        3. 예시와 연습 문제
        4. 상호작용 활동 제안
        5. 학습 정리
        
        각 섹션에서 적절한 위치에 [이미지: 설명] 형태로 이미지 위치를 표시해주세요.
        상호작용 요소는 [상호작용: 활동 설명] 형태로 표시해주세요.
        """
        
        main_content = self.make_request(
            config.model,
            [
                {"role": "system", "content": content_prompt},
                {"role": "user", "content": config.to_prompt_string()}
            ]
        )
        
        # 2. 상호작용 컨텐츠 생성
        interactive_content = None
        if "상호작용 활동" in config.content_types:
            interactive_content = self.make_request(
                config.model,
                [
                    {"role": "system", "content": INTERACTIVE_CONTENT_PROMPT},
                    {"role": "user", "content": f"기본 컨텐츠: {main_content}\n\n위 내용을 바탕으로 상호작용 활동을 구체적으로 설계해주세요."}
                ]
            )
        
        # 3. 퀴즈 생성
        quiz_content = None
        if "퀴즈" in config.content_types:
            quiz_content = self.make_request(
                config.model,
                [
                    {"role": "system", "content": QUIZ_GENERATOR_PROMPT},
                    {"role": "user", "content": f"학습 내용: {main_content}\n\n위 내용을 바탕으로 {config.grade} 수준의 퀴즈를 5문제 생성해주세요."}
                ]
            )
        
        return GeneratedContent(
            main_content=main_content,
            interactive_content=interactive_content,
            quiz_content=quiz_content
        )


# 싱글톤 인스턴스
ai_service = AIService() 