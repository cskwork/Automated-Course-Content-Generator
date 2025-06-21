# 🇰🇷 초등 디지털 교과서 컨텐츠 생성기

한국 초등학교 교육과정에 맞춘 AI 기반 디지털 교과서 컨텐츠 생성 도구입니다.

## 📚 주요 기능

- **과목 지원**: 영어, 수학
- **학년별 맞춤**: 1학년부터 6학년까지 학년별 수준 조정
- **다양한 컨텐츠 유형**:
  - 개념 설명 및 시각 자료
  - 예시 문제와 연습 활동
  - 상호작용 학습 활동
  - 퀴즈 및 평가 문제
  - 게임형 학습 컨텐츠
- **내보내기 형식**: HTML, PDF 지원

## 🚀 설치 및 실행

### Windows

```bash
install_and_run.bat
```

### macOS/Linux

```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

### 수동 설치

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

## ⚙️ 환경 설정

`.env` 파일을 생성하고 다음 API 키를 설정하세요:

```
OPENAI_API_KEY=your_openai_api_key
# 또는
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## 📖 사용 방법

1. 앱을 실행하고 브라우저에서 `http://localhost:8501` 접속
2. 왼쪽 패널에서 과목, 학년, 학기 선택
3. 단원명과 학습 목표 입력
4. 포함할 컨텐츠 유형 선택
5. "컨텐츠 생성" 버튼 클릭
6. 생성된 컨텐츠를 HTML 또는 PDF로 다운로드

## 🎯 특징

- **한국 교육과정 준수**: 교육부 초등 교육과정 기준 적용
- **학습자 중심**: 연령별 인지 발달 수준 고려
- **상호작용성**: 디지털 환경의 장점을 활용한 인터랙티브 컨텐츠
- **시각적 학습**: 이미지와 그래픽을 활용한 이해도 향상
- **즉각적 피드백**: 퀴즈와 활동에 대한 실시간 피드백 제공

## 📄 라이선스

MIT License
