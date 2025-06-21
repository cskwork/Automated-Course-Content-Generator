"""
Stable Diffusion 설정 파일
"""
import os
from typing import Dict, Any

# 모델 설정 (최신 모델 우선)
DEFAULT_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

# 대안 모델들 (용도별)
AVAILABLE_MODELS = {
    "stable-diffusion-xl": "stabilityai/stable-diffusion-xl-base-1.0",  # 최신 고해상도 (기본)
    "stable-diffusion-xl-turbo": "stabilityai/sdxl-turbo",  # 빠른 생성
    "stable-diffusion-v2-1": "stabilityai/stable-diffusion-2-1",  # 개선된 v2
    "stable-diffusion-v1-5": "runwayml/stable-diffusion-v1-5",  # 호환성용
}

# 기본 생성 파라미터 (SDXL 최적화)
DEFAULT_GENERATION_PARAMS = {
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 25,
    "guidance_scale": 7.0,
    "seed": None
}

# 고품질 설정 (더 오래 걸림)
HIGH_QUALITY_PARAMS = {
    "width": 1024,
    "height": 1024,
    "num_inference_steps": 50,
    "guidance_scale": 7.5,
    "seed": None
}

# 빠른 생성 설정 (SDXL Turbo 활용)
FAST_GENERATION_PARAMS = {
    "width": 512,
    "height": 512,
    "num_inference_steps": 4,
    "guidance_scale": 0.0,
    "seed": None
}

# 교육 주제별 프롬프트 키워드
SUBJECT_KEYWORDS = {
    "math": ["mathematics", "geometric", "diagram", "chart", "graph", "equation", "calculation"],
    "english": ["language", "alphabet", "grammar", "reading", "writing", "literature"],
    "science": ["scientific", "laboratory", "experiment", "nature", "biology", "chemistry", "physics"],
    "history": ["historical", "ancient", "timeline", "civilization", "culture", "monument"],
    "geography": ["map", "landscape", "continent", "country", "climate", "terrain"],
    "art": ["artistic", "creative", "painting", "drawing", "sculpture", "design"],
    "default": ["educational", "learning", "academic", "study", "knowledge"]
}

# 스타일 프리셋
STYLE_PRESETS = {
    "educational": "clean, simple, educational illustration, textbook style, professional",
    "cartoon": "cartoon style, colorful, child-friendly, animated, playful",
    "realistic": "photorealistic, detailed, high quality, professional photography",
    "diagram": "technical diagram, clean lines, minimal, schematic, instructional",
    "infographic": "infographic style, data visualization, clean design, modern"
}

# 네거티브 프롬프트 (제외할 요소들)
NEGATIVE_PROMPTS = {
    "default": "blurry, low quality, distorted, nsfw, inappropriate, violent, scary, dark, watermark, text, signature",
    "child_safe": "nsfw, inappropriate, violent, scary, dark, disturbing, adult content, weapons, blood",
    "educational": "nsfw, inappropriate, distracting, cluttered, confusing, low quality, blurry"
}

# 출력 디렉토리 설정
OUTPUT_DIRS = {
    "images": "output/images",
    "temp": "output/temp",
    "cache": "output/cache"
}

def get_model_config(model_name: str = "stable-diffusion-v1-5") -> str:
    """모델 ID 반환"""
    return AVAILABLE_MODELS.get(model_name, DEFAULT_MODEL_ID)

def get_generation_params(quality: str = "default") -> Dict[str, Any]:
    """품질에 따른 생성 파라미터 반환"""
    if quality == "high":
        return HIGH_QUALITY_PARAMS.copy()
    elif quality == "fast":
        return FAST_GENERATION_PARAMS.copy()
    else:
        return DEFAULT_GENERATION_PARAMS.copy()

def get_subject_keywords(subject: str) -> list:
    """주제별 키워드 반환"""
    return SUBJECT_KEYWORDS.get(subject.lower(), SUBJECT_KEYWORDS["default"])

def get_style_preset(style: str) -> str:
    """스타일 프리셋 반환"""
    return STYLE_PRESETS.get(style.lower(), STYLE_PRESETS["educational"])

def get_negative_prompt(safety_level: str = "default") -> str:
    """안전 수준에 따른 네거티브 프롬프트 반환"""
    return NEGATIVE_PROMPTS.get(safety_level, NEGATIVE_PROMPTS["default"])

def ensure_output_dirs():
    """출력 디렉토리 생성"""
    for dir_path in OUTPUT_DIRS.values():
        os.makedirs(dir_path, exist_ok=True)