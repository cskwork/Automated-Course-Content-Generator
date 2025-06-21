"""
로컬 Stable Diffusion 이미지 생성기
"""
import os
import re
import base64
from io import BytesIO
from typing import List, Optional, Dict, Any
import streamlit as st
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import logging

from src.models.content_types import ImageInfo


class StableDiffusionGenerator:
    """로컬 Stable Diffusion을 사용한 이미지 생성기"""
    
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        self.model_id = model_id
        self.pipeline = None
        # 플랫폼별 최적 디바이스 선택
        if torch.cuda.is_available():
            self.device = "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.device = "mps"  # Apple Silicon
        else:
            self.device = "cpu"
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Using device: {self.device}")
        
        # 어린이 만화 스타일을 기본으로 적용하도록 프롬프트 템플릿을 수정
        # 각 과목에 공통적으로 cartoon style 키워드를 추가해 색감이 밝고 친근한 이미지를 생성하도록 설정한다.
        self.educational_prompts = {
            "math": "educational illustration, mathematics concept, cartoon style, colorful, child-friendly, playful, clean simple diagram, textbook style, high quality, detailed",
            "english": "educational illustration, english language concept, cartoon style, colorful, child-friendly, playful, clean simple design, textbook style, high quality, detailed", 
            "science": "educational illustration, science concept, cartoon style, colorful, child-friendly, playful, clean simple diagram, textbook style, high quality, detailed",
            "history": "educational illustration, historical concept, cartoon style, colorful, child-friendly, playful, clean simple design, textbook style, high quality, detailed",
            "default": "educational illustration, learning concept, cartoon style, colorful, child-friendly, playful, clean simple design, textbook style, high quality, detailed"
        }
        
        # 네거티브 프롬프트 (원하지 않는 요소들)
        self.negative_prompt = "blurry, low quality, distorted, nsfw, inappropriate, text, watermark, signature, dark, scary"
        
    def _load_pipeline(self) -> bool:
        """Stable Diffusion 파이프라인 로드"""
        try:
            if self.pipeline is None:
                st.info("Stable Diffusion 모델을 로딩중입니다... (최초 실행시 시간이 걸릴 수 있습니다)")
                
                # 플랫폼별 데이터 타입 설정
                if self.device == "cuda":
                    torch_dtype = torch.float16
                elif self.device == "mps":
                    torch_dtype = torch.float32  # MPS는 float16을 완전히 지원하지 않음
                else:
                    torch_dtype = torch.float32
                
                # 파이프라인 생성
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch_dtype,
                    safety_checker=None,  # 교육용 컨텐츠에 적합하도록 안전 체크 비활성화
                    requires_safety_checker=False
                )
                
                # 스케줄러 최적화
                self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipeline.scheduler.config
                )
                
                # xformers는 CPU에서 지원되지 않으며, CUDA 환경에서도 선택 사항입니다.
                # self.pipeline.enable_memory_efficient_attention()
                
                # 모델을 CPU로 이동
                self.pipeline = self.pipeline.to(self.device)
                
                # 플랫폼별 메모리 최적화
                if self.device == "cuda":
                    self.pipeline.enable_attention_slicing()
                elif self.device == "mps":
                    # Apple Silicon 최적화
                    self.pipeline.enable_attention_slicing()
                
                self.logger.info(f"Stable Diffusion 파이프라인 로드 완료 (device: {self.device})")
                st.success("Stable Diffusion 모델 로드 완료!")
                
            return True
            
        except Exception as e:
            self.logger.error(f"파이프라인 로드 실패: {str(e)}")
            st.error(f"Stable Diffusion 모델 로드 실패: {str(e)}")
            return False
    
    def _enhance_prompt(self, topic: str, subject: str = "default") -> str:
        """교육용 프롬프트 향상"""
        base_prompt = self.educational_prompts.get(subject.lower(), self.educational_prompts["default"])
        enhanced_prompt = f"{topic}, {base_prompt}"
        return enhanced_prompt
    
    def generate_image(
        self, 
        prompt: str, 
        subject: str = "default",
        width: int = 512, 
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Optional[Image.Image]:
        """이미지 생성"""
        if not self._load_pipeline():
            return None
            
        try:
            # 프롬프트 향상
            enhanced_prompt = self._enhance_prompt(prompt, subject)
            
            # 시드 설정
            if seed is not None:
                torch.manual_seed(seed)
            
            # 이미지 생성
            with st.spinner(f"'{prompt}' 이미지를 생성중입니다..."):
                with torch.no_grad():
                    result = self.pipeline(
                        prompt=enhanced_prompt,
                        negative_prompt=self.negative_prompt,
                        width=width,
                        height=height,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        generator=torch.Generator(device=self.device).manual_seed(seed) if seed else None
                    )
                    
                    image = result.images[0]
                    
            self.logger.info(f"이미지 생성 완료: {prompt}")
            return image
            
        except Exception as e:
            self.logger.error(f"이미지 생성 실패: {str(e)}")
            st.error(f"이미지 생성 실패: {str(e)}")
            return None
    
    def save_image(self, image: Image.Image, filename: str, output_dir: str = "output/images") -> Optional[str]:
        """생성된 이미지 저장"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            image.save(filepath, format="PNG", quality=95)
            return filepath
        except Exception as e:
            self.logger.error(f"이미지 저장 실패: {str(e)}")
            return None
    
    def image_to_base64(self, image: Image.Image) -> str:
        """이미지를 base64 문자열로 변환"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def generate_image_info(self, image: Image.Image, description: str, prompt: str) -> ImageInfo:
        """생성된 이미지에 대한 ImageInfo 객체 생성"""
        # 이미지를 base64로 변환
        base64_image = self.image_to_base64(image)
        
        return ImageInfo(
            id=f"sd_{hash(prompt)}",
            url=base64_image,
            thumb_url=base64_image,
            description=description,
            author="AI Generated",
            author_url=""
        )
    
    def extract_placeholders(self, content: str) -> List[str]:
        """컨텐츠에서 이미지 플레이스홀더 추출"""
        pattern = r'\[이미지: ([^\]]+)\]'
        return re.findall(pattern, content)
    
    def get_image_for_topic(self, topic: str, subject: str = "default") -> Optional[ImageInfo]:
        """주제에 맞는 교육용 이미지 생성"""
        try:
            image = self.generate_image(topic, subject)
            if image:
                return self.generate_image_info(image, topic, topic)
            return None
        except Exception as e:
            self.logger.error(f"주제별 이미지 생성 실패: {str(e)}")
            return None
    
    def replace_placeholders(self, content: str, subject: str) -> str:
        """이미지 플레이스홀더를 실제 이미지로 교체"""
        placeholders = self.extract_placeholders(content)
        
        for placeholder in placeholders:
            image_info = self.get_image_for_topic(placeholder, subject)
            
            if image_info:
                image_html = image_info.to_html(placeholder)
                content = content.replace(f'[이미지: {placeholder}]', image_html)
            else:
                # 이미지 생성 실패시 플레이스홀더 유지
                placeholder_html = f'<div class="image-placeholder">이미지: {placeholder} (생성 실패)</div>'
                content = content.replace(f'[이미지: {placeholder}]', placeholder_html)
        
        return content
    
    def enhance_content_with_images(self, content: str, subject: str) -> str:
        """컨텐츠에 AI 생성 이미지 추가"""
        return self.replace_placeholders(content, subject)
    
    def batch_generate_images(
        self, 
        prompts: List[str], 
        subject: str = "default",
        **kwargs
    ) -> List[Optional[Image.Image]]:
        """여러 이미지 일괄 생성"""
        images = []
        for prompt in prompts:
            image = self.generate_image(prompt, subject, **kwargs)
            images.append(image)
        return images
    
    def cleanup(self):
        """메모리 정리"""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
            # 플랫폼별 메모리 정리
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                torch.mps.empty_cache()
            self.logger.info("Stable Diffusion 파이프라인 메모리 정리 완료")


# 싱글톤 인스턴스
stable_diffusion_generator = StableDiffusionGenerator()