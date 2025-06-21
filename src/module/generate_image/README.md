# Stable Diffusion 이미지 생성 모듈

로컬 Stable Diffusion을 사용하여 교육용 이미지를 생성하는 모듈입니다.

## 기능

- 🎨 로컬 Stable Diffusion을 사용한 이미지 생성
- 📚 교육용 콘텐츠에 최적화된 프롬프트
- 🔄 배치 이미지 생성 지원
- 💾 이미지 저장 및 Base64 변환
- 🖼️ 기존 Unsplash API와의 통합
- ⚙️ 다양한 품질 설정 지원

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# GPU 사용을 위한 PyTorch CUDA 설치 (선택사항)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 사용법

### 기본 사용법

```python
from src.module.generate_image import StableDiffusionGenerator

# 생성기 인스턴스 생성
generator = StableDiffusionGenerator()

# 이미지 생성
image = generator.generate_image("수학 공식 그래프", subject="math")

if image:
    # 이미지 저장
    generator.save_image(image, "math_formula.png")
```

### 교육 콘텐츠와 통합

```python
from src.services.image_service import image_service

# Stable Diffusion 사용 설정
image_service.set_image_source(use_stable_diffusion=True)

# 콘텐츠에 이미지 플레이스홀더 포함
content = """
# 수학 - 기하학
[이미지: 삼각형 도형]
삼각형의 기본 성질을 학습해보겠습니다.
"""

# 이미지가 포함된 콘텐츠 생성
enhanced_content = image_service.enhance_content_with_images(content, "math")
```

### 고급 설정

```python
# 고품질 이미지 생성
image = generator.generate_image(
    prompt="교육용 과학 실험 다이어그램",
    subject="science",
    width=768,
    height=768,
    num_inference_steps=50,
    guidance_scale=8.5,
    seed=42  # 재현 가능한 결과
)
```

### 배치 생성

```python
prompts = [
    "수학 덧셈 문제",
    "수학 곱셈 표", 
    "기하학적 도형"
]

images = generator.batch_generate_images(prompts, subject="math")
```

## 설정

### 모델 설정

`config.py`에서 사용할 모델을 선택할 수 있습니다:

```python
# 기본 모델
model = "runwayml/stable-diffusion-v1-5"

# 고품질 모델 (더 느림)
model = "stabilityai/stable-diffusion-2"

# 고해상도 모델 (훨씬 더 느림)
model = "stabilityai/stable-diffusion-xl-base-1.0"
```

### 품질 설정

```python
from src.module.generate_image.config import get_generation_params

# 빠른 생성 (낮은 품질)
params = get_generation_params("fast")

# 기본 품질
params = get_generation_params("default")

# 고품질 (느림)
params = get_generation_params("high")
```

## 주제별 최적화

각 교육 주제에 맞게 프롬프트가 최적화됩니다:

- **수학 (math)**: 다이어그램, 그래프, 기하학적 도형에 특화
- **영어 (english)**: 언어 학습, 문법, 문학에 특화  
- **과학 (science)**: 실험, 자연, 생물학/화학/물리학에 특화
- **역사 (history)**: 역사적 장면, 문명, 문화에 특화
- **지리 (geography)**: 지도, 지형, 기후에 특화

## 성능 최적화

### GPU 사용

- CUDA GPU가 있으면 자동으로 감지하여 사용
- GPU 메모리 최적화 기능 포함
- CPU에서도 실행 가능 (훨씬 느림)

### 메모리 관리

```python
# 메모리 정리
generator.cleanup()

# 또는 자동 메모리 최적화 활성화 (GPU만)
# pipeline.enable_memory_efficient_attention()
# pipeline.enable_attention_slicing()
```

## 안전성

- 교육용 콘텐츠에 적합하도록 안전 필터 설정
- 부적절한 콘텐츠 생성 방지를 위한 네거티브 프롬프트 사용
- 아동 안전 수준의 필터링 옵션 제공

## 기존 시스템과의 통합

### Unsplash API와 전환

```python
# Unsplash 사용 (기본값)
image_service.set_image_source(use_stable_diffusion=False)

# Stable Diffusion 사용
image_service.set_image_source(use_stable_diffusion=True)
```

### Streamlit UI 통합

```python
import streamlit as st

# 사용자가 이미지 소스 선택
use_ai = st.sidebar.checkbox("AI 이미지 생성 사용", value=False)
image_service.set_image_source(use_stable_diffusion=use_ai)
```

## 예제 실행

```bash
# 예제 앱 실행
streamlit run src/module/generate-image/usage_example.py
```

## 문제 해결

### 일반적인 오류

1. **CUDA 메모리 부족**: 이미지 크기를 줄이거나 배치 크기를 1로 설정
2. **모델 다운로드 실패**: 인터넷 연결 확인 및 Hugging Face 접근 권한 확인
3. **생성 속도 느림**: GPU 사용 확인 또는 생성 단계 수 줄이기

### 성능 개선 팁

- 첫 실행시 모델 다운로드로 시간이 오래 걸림
- GPU 메모리가 부족하면 이미지 크기를 512x512 이하로 설정
- 빠른 생성을 원하면 `num_inference_steps`를 10-15로 설정
- 배치 생성시 메모리 사용량 주의

## 라이선스 및 크레딧

- Stable Diffusion 모델: CreativeML Open RAIL-M 라이선스
- 생성된 이미지: 상업적 사용 가능 (모델 라이선스 조건 확인 필요)
- 교육용 목적으로 최적화됨