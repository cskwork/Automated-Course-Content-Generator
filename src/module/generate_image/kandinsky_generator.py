"""
칸딘스키 2.2 이미지 생성기
"""
import os
import re
import base64
from io import BytesIO
from typing import List, Optional
import streamlit as st
from PIL import Image
import torch
from diffusers import AutoPipelineForText2Image, DiffusionPipeline
import logging
from urllib3.exceptions import MaxRetryError, NameResolutionError
from requests.exceptions import ConnectionError

from src.models.content_types import ImageInfo


class KandinskyGenerator:
    """칸딘스키 2.2를 사용한 이미지 생성기"""

    def __init__(self, prior_model_id: str = "kandinsky-community/kandinsky-2-2-prior", decoder_model_id: str = "kandinsky-community/kandinsky-2-2-decoder"):
        self.prior_model_id = prior_model_id
        self.decoder_model_id = decoder_model_id
        self.pipeline = None
        self.local_files_only = False
        if torch.cuda.is_available():
            self.device = "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Using device: {self.device}")

        self.educational_prompts = {
            "math": "educational illustration, mathematics concept, cartoon style, colorful, child-friendly, playful, clean simple diagram, textbook style, high quality, detailed",
            "english": "educational illustration, english language concept, cartoon style, colorful, child-friendly, playful, clean simple design, textbook style, high quality, detailed",
            "science": "educational illustration, science concept, cartoon style, colorful, child-friendly, playful, clean simple diagram, textbook style, high quality, detailed",
            "history": "educational illustration, historical concept, cartoon style, colorful, child-friendly, playful, clean simple design, textbook style, high quality, detailed",
            "default": "educational illustration, learning concept, cartoon style, colorful, child-friendly, playful, clean simple design, textbook style, high quality, detailed"
        }
        
        self.negative_prompt = "blurry, low quality, distorted, nsfw, inappropriate, text, watermark, signature, dark, scary"

    def _load_pipeline(self, local_files_only: bool = False) -> bool:
        """Kandinsky 파이프라인 로드"""
        self.local_files_only = local_files_only
        try:
            if self.pipeline is None:
                st.info("Kandinsky 2.2 모델을 로딩중입니다... (최초 실행시 시간이 걸릴 수 있습니다)")
                
                if self.device == "cuda":
                    torch_dtype = torch.float16
                else:
                    torch_dtype = torch.float32

                prior_pipeline = DiffusionPipeline.from_pretrained(
                    self.prior_model_id, 
                    torch_dtype=torch_dtype,
                    local_files_only=self.local_files_only
                )
                prior_pipeline.to(self.device)
                
                prior_components = {"prior_" + k: v for k,v in prior_pipeline.components.items()}

                self.pipeline = AutoPipelineForText2Image.from_pretrained(
                    self.decoder_model_id, 
                    **prior_components, 
                    torch_dtype=torch_dtype,
                    local_files_only=self.local_files_only
                )
                self.pipeline.to(self.device)

                if self.device == "cuda":
                    self.pipeline.enable_attention_slicing()
                elif self.device == "mps":
                    self.pipeline.enable_attention_slicing()
                
                self.logger.info(f"Kandinsky 2.2 파이프라인 로드 완료 (device: {self.device})")
                st.success("Kandinsky 2.2 모델 로드 완료!")
            return True
        except (ConnectionError, MaxRetryError, NameResolutionError) as e:
            self.logger.error(f"네트워크 오류로 모델 로드 실패: {str(e)}")
            st.error(
                "모델 다운로드 중 네트워크 오류가 발생했습니다. "
                "인터넷 연결을 확인하시거나, 잠시 후 다시 시도해주세요. "
                "방화벽이나 프록시 설정이 원인일 수도 있습니다."
            )
            st.info(f"자세한 오류: {e}")
            self.pipeline = None
            return False
        except Exception as e:
            self.logger.error(f"파이프라인 로드 실패: {str(e)}")
            st.error(f"Kandinsky 2.2 모델 로드 실패: {str(e)}")
            st.info("Hugging Face Hub 토큰이 올바른지, 또는 로컬 모델 캐시가 손상되지 않았는지 확인해보세요.")
            self.pipeline = None
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
        num_inference_steps: int = 25,
        guidance_scale: float = 7.0,
        seed: Optional[int] = None,
        local_files_only: bool = False
    ) -> Optional[Image.Image]:
        """이미지 생성"""
        if not self._load_pipeline(local_files_only=local_files_only):
            return None
            
        try:
            enhanced_prompt = self._enhance_prompt(prompt, subject)
            
            generator = torch.Generator(device=self.device).manual_seed(seed) if seed else None
            
            with st.spinner(f"'{prompt}' 이미지를 생성중입니다..."):
                with torch.no_grad():
                    image = self.pipeline(
                        prompt=enhanced_prompt,
                        negative_prompt=self.negative_prompt,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        generator=generator
                    ).images[0]
                    
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
        base64_image = self.image_to_base64(image)
        
        return ImageInfo(
            id=f"kandinsky_{hash(prompt)}",
            url=base64_image,
            thumb_url=base64_image,
            description=description,
            author="AI Generated (Kandinsky)",
            author_url=""
        )

    def get_image_for_topic(self, topic: str, subject: str = "default", local_files_only: bool = False) -> Optional[ImageInfo]:
        """주제에 맞는 교육용 이미지 생성"""
        try:
            image = self.generate_image(topic, subject, local_files_only=local_files_only)
            if image:
                return self.generate_image_info(image, topic, topic)
            return None
        except Exception as e:
            self.logger.error(f"주제별 이미지 생성 실패: {str(e)}")
            return None

    def cleanup(self):
        """메모리 정리"""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                torch.mps.empty_cache()
            self.logger.info("Kandinsky 2.2 파이프라인 메모리 정리 완료")


# 싱글톤 인스턴스
kandinsky_generator = KandinskyGenerator() 