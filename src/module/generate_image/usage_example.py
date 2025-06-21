"""
Stable Diffusion 이미지 생성기 사용 예제
"""
import streamlit as st
from stable_diffusion_generator import stable_diffusion_generator
from config import get_generation_params, get_style_preset

def example_basic_usage():
    """기본 사용법 예제"""
    st.header("기본 이미지 생성")
    
    # 사용자 입력
    prompt = st.text_input("이미지 설명을 입력하세요:", "수학 공식 그래프")
    subject = st.selectbox("주제 선택:", ["math", "english", "science", "history", "default"])
    
    if st.button("이미지 생성"):
        # 이미지 생성
        image = stable_diffusion_generator.generate_image(prompt, subject)
        
        if image:
            st.image(image, caption=f"생성된 이미지: {prompt}")
            
            # 이미지 저장 옵션
            if st.button("이미지 저장"):
                filename = f"{prompt.replace(' ', '_')}.png"
                filepath = stable_diffusion_generator.save_image(image, filename)
                if filepath:
                    st.success(f"이미지가 저장되었습니다: {filepath}")

def example_batch_generation():
    """배치 이미지 생성 예제"""
    st.header("여러 이미지 일괄 생성")
    
    # 여러 프롬프트 입력
    prompts_text = st.text_area(
        "이미지 설명들을 각 줄에 하나씩 입력하세요:",
        "수학 덧셈 문제\n수학 곱셈 표\n기하학적 도형"
    )
    
    subject = st.selectbox("주제 선택:", ["math", "english", "science", "history", "default"], key="batch")
    
    if st.button("일괄 생성"):
        prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
        
        if prompts:
            # 배치 생성
            images = stable_diffusion_generator.batch_generate_images(prompts, subject)
            
            # 결과 표시
            cols = st.columns(min(len(images), 3))
            for i, image in enumerate(images):
                with cols[i % 3]:
                    if image:
                        st.image(image, caption=prompts[i])
                        
                        # 개별 저장 버튼
                        if st.button(f"저장 {i+1}", key=f"save_{i}"):
                            filename = f"{prompts[i].replace(' ', '_')}.png"
                            filepath = stable_diffusion_generator.save_image(image, filename)
                            if filepath:
                                st.success(f"저장됨: {filepath}")

def example_advanced_settings():
    """고급 설정 예제"""
    st.header("고급 설정으로 이미지 생성")
    
    # 고급 설정
    col1, col2 = st.columns(2)
    
    with col1:
        prompt = st.text_input("프롬프트:", "교육용 수학 다이어그램")
        subject = st.selectbox("주제:", ["math", "english", "science", "history", "default"], key="advanced")
        width = st.slider("너비:", 256, 1024, 512, 64)
        height = st.slider("높이:", 256, 1024, 512, 64)
        
    with col2:
        num_steps = st.slider("생성 단계:", 10, 50, 20)
        guidance_scale = st.slider("가이던스 스케일:", 1.0, 20.0, 7.5, 0.5)
        seed = st.number_input("시드 (재현 가능한 결과):", min_value=0, max_value=2147483647, value=42)
        use_seed = st.checkbox("시드 사용")
    
    if st.button("고급 설정으로 생성"):
        # 고급 설정으로 이미지 생성
        image = stable_diffusion_generator.generate_image(
            prompt=prompt,
            subject=subject,
            width=width,
            height=height,
            num_inference_steps=num_steps,
            guidance_scale=guidance_scale,
            seed=seed if use_seed else None
        )
        
        if image:
            st.image(image, caption=f"생성된 이미지: {prompt}")
            
            # 설정 정보 표시
            st.info(f"설정: {width}x{height}, 단계: {num_steps}, 가이던스: {guidance_scale}, 시드: {seed if use_seed else 'None'}")

def example_content_integration():
    """콘텐츠 통합 예제"""
    st.header("교육 콘텐츠와 이미지 통합")
    
    # 샘플 교육 콘텐츠
    sample_content = """
    # 수학 - 기하학 기초
    
    ## 1. 기본 도형
    [이미지: 삼각형 사각형 원]
    
    기본적인 기하학적 도형들을 살펴보겠습니다.
    
    ## 2. 삼각형의 종류
    [이미지: 정삼각형 이등변삼각형 직각삼각형]
    
    삼각형은 변의 길이와 각도에 따라 분류됩니다.
    
    ## 3. 원의 성질
    [이미지: 원 반지름 지름 원주]
    
    원은 중심점에서 같은 거리에 있는 점들의 집합입니다.
    """
    
    content = st.text_area("교육 콘텐츠 (이미지 플레이스홀더 포함):", sample_content, height=300)
    subject = st.selectbox("주제:", ["math", "english", "science", "history", "default"], key="content")
    
    if st.button("이미지가 포함된 콘텐츠 생성"):
        # 이미지 플레이스홀더를 실제 이미지로 교체
        enhanced_content = stable_diffusion_generator.enhance_content_with_images(content, subject)
        
        # 결과 표시 (HTML 렌더링)
        st.markdown("### 생성된 콘텐츠:")
        st.markdown(enhanced_content, unsafe_allow_html=True)

def main():
    """메인 함수"""
    st.set_page_config(page_title="Stable Diffusion 이미지 생성기", layout="wide")
    
    st.title("🎨 Stable Diffusion 이미지 생성기")
    st.write("로컬 Stable Diffusion을 사용한 교육용 이미지 생성")
    
    # 사이드바 설정
    st.sidebar.header("설정")
    
    # GPU 상태 확인
    import torch
    if torch.cuda.is_available():
        st.sidebar.success(f"GPU 사용 가능: {torch.cuda.get_device_name()}")
    else:
        st.sidebar.warning("GPU 없음 - CPU 사용 (느림)")
    
    # 예제 선택
    example_choice = st.sidebar.selectbox(
        "예제 선택:",
        ["기본 사용법", "배치 생성", "고급 설정", "콘텐츠 통합"]
    )
    
    # 메모리 정리 버튼
    if st.sidebar.button("메모리 정리"):
        stable_diffusion_generator.cleanup()
        st.sidebar.success("메모리 정리 완료")
    
    # 선택된 예제 실행
    if example_choice == "기본 사용법":
        example_basic_usage()
    elif example_choice == "배치 생성":
        example_batch_generation()
    elif example_choice == "고급 설정":
        example_advanced_settings()
    elif example_choice == "콘텐츠 통합":
        example_content_integration()

if __name__ == "__main__":
    main()