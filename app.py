from openai import OpenAI, OpenAIError
import ollama
import streamlit as st
from dotenv import load_dotenv
import os
import json
import shelve
import unicodedata
from fpdf import FPDF # type: ignore
import base64
import requests
from prompts.elementary_english_prompt import ELEMENTARY_ENGLISH_PROMPT
from prompts.elementary_math_prompt import ELEMENTARY_MATH_PROMPT
from prompts.interactive_content_prompt import INTERACTIVE_CONTENT_PROMPT
from prompts.quiz_generator_prompt import QUIZ_GENERATOR_PROMPT


# Unsplash API 함수들
def search_unsplash_images(query, per_page=5):
    """Unsplash API를 사용하여 이미지 검색"""
    api_key = os.getenv("UNSPLASH_API_KEY")
    if not api_key:
        st.warning("UNSPLASH_API_KEY가 설정되지 않았습니다. 이미지가 표시되지 않습니다.")
        return []
    
    # API 엔드포인트
    url = "https://api.unsplash.com/search/photos"
    
    # 헤더 설정
    headers = {
        "Authorization": f"Client-ID {api_key}"
    }
    
    # 파라미터 설정
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",  # 가로 이미지 선호
        "content_filter": "high"     # 안전한 콘텐츠만
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 이미지 정보 추출
        images = []
        for photo in data.get("results", []):
            images.append({
                "id": photo["id"],
                "url": photo["urls"]["regular"],
                "thumb_url": photo["urls"]["small"],
                "description": photo.get("description", photo.get("alt_description", "")),
                "author": photo["user"]["name"],
                "author_url": photo["user"]["links"]["html"]
            })
        
        return images
    except requests.exceptions.RequestException as e:
        st.error(f"Unsplash API 오류: {str(e)}")
        return []

def get_image_for_topic(topic, subject="educational"):
    """주제에 맞는 교육용 이미지 가져오기"""
    # 교육용 키워드 추가
    educational_keywords = {
        "영어": "english learning kids education",
        "수학": "mathematics education kids learning"
    }
    
    # 주제별 검색어 생성
    base_keyword = educational_keywords.get(subject, "education learning")
    search_query = f"{topic} {base_keyword}"
    
    # 이미지 검색
    images = search_unsplash_images(search_query, per_page=1)
    
    if images:
        return images[0]
    else:
        # 대체 검색어로 재시도
        images = search_unsplash_images(base_keyword, per_page=1)
        return images[0] if images else None

def extract_image_placeholders(content):
    """컨텐츠에서 이미지 플레이스홀더 추출"""
    import re
    pattern = r'\[이미지: ([^\]]+)\]'
    matches = re.findall(pattern, content)
    return matches

def replace_image_placeholders(content, subject):
    """이미지 플레이스홀더를 실제 이미지로 교체"""
    placeholders = extract_image_placeholders(content)
    
    for placeholder in placeholders:
        image_info = get_image_for_topic(placeholder, subject)
        
        if image_info:
            # HTML 이미지 태그로 교체
            image_html = f'''
            <div class="image-container">
                <img src="{image_info['url']}" alt="{placeholder}" style="width: 100%; max-width: 600px; border-radius: 8px;">
                <p class="image-caption">
                    <small>{placeholder} - Photo by <a href="{image_info['author_url']}?utm_source=course_generator&utm_medium=referral" target="_blank">{image_info['author']}</a> on <a href="https://unsplash.com/?utm_source=course_generator&utm_medium=referral" target="_blank">Unsplash</a></small>
                </p>
            </div>
            '''
            content = content.replace(f'[이미지: {placeholder}]', image_html)
        else:
            # 이미지를 찾을 수 없는 경우 플레이스홀더 유지
            content = content.replace(f'[이미지: {placeholder}]', f'<div class="image-placeholder">이미지: {placeholder}</div>')
    
    return content


def generate_pdf(content, filename):
    content = unicodedata.normalize('NFKD', content).encode('utf-8', 'ignore').decode('utf-8')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename, 'F')
    return pdf

def generate_html(content, filename):
    """HTML 파일 생성 함수"""
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

# Customizing the page configuration
st.set_page_config(
    page_title="초등 디지털 교과서 컨텐츠 생성기",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv()

st.title("🇰🇷 초등 디지털 교과서 컨텐츠 생성기 📚")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Helper function to make AI API calls
def make_ai_request(client, provider, model, messages):
    """Make API request to different AI providers with unified interface"""
    if provider in ['openai', 'openrouter']:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    elif provider == 'ollama':
        # Convert messages format for Ollama
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        response = client.chat(
            model=model,
            messages=ollama_messages
        )
        return response['message']['content']
    else:
        raise ValueError(f"Unsupported provider: {provider}")

# Initialize AI client based on provider selection
def initialize_ai_client():
    provider = st.session_state.get('ai_provider', 'openai')
    
    if provider == 'openai':
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OPENAI_API_KEY를 .env 파일에 설정해주세요")
            return None
        return OpenAI(api_key=api_key), 'openai'
    
    elif provider == 'openrouter':
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if not api_key:
            st.error("OPENROUTER_API_KEY를 .env 파일에 설정해주세요")
            return None
        # OpenRouter uses OpenAI-compatible API
        return OpenAI(api_key=api_key, base_url=base_url), 'openrouter'
    
    elif provider == 'ollama':
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        try:
            # Test connection to Ollama
            client = ollama.Client(host=host)
            # Try to list models to verify connection
            client.list()
            return client, 'ollama'
        except Exception as e:
            st.error(f"Ollama 연결 실패: {str(e)}. Ollama가 실행중인지 확인해주세요.")
            return None
    
    return None, None

try:
    client, current_provider = initialize_ai_client()
except Exception as e:
    st.error(f"AI 클라이언트 초기화 오류: {str(e)}")
    client, current_provider = None, None

# Initialize session state for AI provider and model
if "ai_provider" not in st.session_state:
    # 환경 변수에서 모델 선택 설정을 읽어와서 기본값으로 사용
    default_provider = os.getenv("MODEL_SELECTION", "openai")
    st.session_state["ai_provider"] = default_provider

if "ai_model" not in st.session_state:
    if st.session_state["ai_provider"] == "openai":
        st.session_state["ai_model"] = "gpt-4"
    elif st.session_state["ai_provider"] == "openrouter":
        st.session_state["ai_model"] = "openai/gpt-4"
    else:  # ollama
        st.session_state["ai_model"] = os.getenv("OLLAMA_DEFAULT_MODEL", "gemma3:latest")

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("대화 기록 삭제"):
        st.session_state.messages = []
        save_chat_history([])

# Example of using columns for advanced layouts
col1, col2 = st.columns(2)

col1, col_divider, col2 = st.columns([3.0,0.1,7.0])

with col1:
    st.header("교과서 설정 📋")
    
    # AI Provider Selection
    st.subheader("AI 설정")
    provider_options = ["openai", "openrouter", "ollama"]
    selected_provider = st.selectbox(
        "AI 제공자 선택",
        provider_options,
        index=provider_options.index(st.session_state.get("ai_provider", "openai")),
        help="사용할 AI 제공자를 선택하세요"
    )
    
    # Update session state if provider changed
    if selected_provider != st.session_state.get("ai_provider"):
        st.session_state["ai_provider"] = selected_provider
        # Reinitialize client when provider changes
        client, current_provider = initialize_ai_client()
        # Update default model based on provider
        if selected_provider == "openai":
            st.session_state["ai_model"] = "gpt-4"
        elif selected_provider == "openrouter":
            st.session_state["ai_model"] = "openai/gpt-4"
        else:  # ollama
            st.session_state["ai_model"] = os.getenv("OLLAMA_DEFAULT_MODEL", "gemma3:latest")
    
    # Model Selection based on provider
    if selected_provider == "openai":
        model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    elif selected_provider == "openrouter":
        model_options = [
            "openai/gpt-3.5-turbo",
            "openai/gpt-4",
            "openai/gpt-4-turbo",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro"
        ]
    else:  # ollama
        # Get available Ollama models dynamically
        try:
            if client:
                available_models = client.list()
                model_options = [model['name'] for model in available_models['models']]
                if not model_options:
                    model_options = ["llama3.2", "llama3.1", "codellama", "mistral", "qwen2.5"]
            else:
                model_options = ["gemma3:latest", "llama3.2", "llama3.1", "codellama", "mistral", "qwen2.5"]
        except:
            model_options = ["gemma3:latest", "llama3.2", "llama3.1", "codellama", "mistral", "qwen2.5"]
    
    selected_model = st.selectbox(
        "AI 모델 선택",
        model_options,
        index=model_options.index(st.session_state.get("ai_model", model_options[0])) if st.session_state.get("ai_model") in model_options else 0,
        help="컨텐츠 생성에 사용할 AI 모델을 선택하세요"
    )
    st.session_state["ai_model"] = selected_model
    
    st.divider()
    
    # 한국 초등학교 교육과정 설정
    subject = st.selectbox(
        "과목 선택",
        ["영어", "수학"]
    )
    
    grade = st.selectbox(
        "학년",
        ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"]
    )
    
    semester = st.selectbox(
        "학기",
        ["1학기", "2학기"]
    )
    
    unit_name = st.text_input("단원명")
    
    learning_objectives = st.text_area("학습 목표", height=100)
    
    # 컨텐츠 유형 선택
    content_types = st.multiselect(
        "포함할 컨텐츠 유형",
        ["개념 설명", "예시 문제", "상호작용 활동", "시각 자료", "퀴즈", "게임형 학습"],
        default=["개념 설명", "예시 문제", "상호작용 활동", "퀴즈"]
    )
    
    # Export 형식 선택
    export_format = st.radio(
        "내보내기 형식",
        ["HTML", "PDF", "둘 다"]
    )

    # Save widget states in session_state
    st.session_state.subject = subject
    st.session_state.grade = grade
    st.session_state.semester = semester
    st.session_state.unit_name = unit_name
    st.session_state.learning_objectives = learning_objectives
    st.session_state.content_types = content_types
    st.session_state.export_format = export_format

    button1, button2 = st.columns([1, 0.8])
    with button1:
        generate_button = st.button("컨텐츠 생성", help="클릭하여 디지털 교과서 컨텐츠를 생성하세요! 🎯")
    with button2:
        if "content_generated" in st.session_state:
            new_content_button = st.button("새 컨텐츠", help="새로운 컨텐츠를 만들어보세요! 💡")
            if new_content_button:
                # 세션 상태 초기화
                for key in ['subject', 'grade', 'semester', 'unit_name', 'learning_objectives', 
                           'content_types', 'content_generated', 'generated_content']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()
                
    


with col2:
    st.header("생성된 교과서 컨텐츠 📝")
    # Display the generated content here
    if generate_button and "content_generated" not in st.session_state:
        if not client:
            st.error("선택한 AI 제공자의 API 키를 .env 파일에 설정해주세요.")
            st.stop()
        # Include user selections in the message history
        user_selections = f"""
        과목: {subject}
        학년: {grade}
        학기: {semester}
        단원명: {unit_name}
        학습 목표: {learning_objectives}
        컨텐츠 유형: {', '.join(content_types)}
        """
        st.session_state.messages.append({"role": "user", "content": user_selections})

        # 과목에 따라 적절한 프롬프트 선택
        if subject == "영어":
            base_prompt = ELEMENTARY_ENGLISH_PROMPT
        else:  # 수학
            base_prompt = ELEMENTARY_MATH_PROMPT
            
        # 전체 컨텐츠 생성
        with st.spinner("디지털 교과서 컨텐츠를 생성중입니다... 📚"):
            # 1. 기본 컨텐츠 생성
            content_prompt = f"""{base_prompt}
            
            학년: {grade}
            학기: {semester}
            단원명: {unit_name}
            학습 목표: {learning_objectives}
            
            다음 형식으로 컨텐츠를 생성해주세요:
            1. 도입부 (학습 동기 유발)
            2. 핵심 개념 설명 (이미지 위치 표시 포함)
            3. 예시와 연습 문제
            4. 상호작용 활동 제안
            5. 학습 정리
            
            각 섹션에서 적절한 위치에 [이미지: 설명] 형태로 이미지 위치를 표시해주세요.
            상호작용 요소는 [상호작용: 활동 설명] 형태로 표시해주세요.
            """
            
            main_content = make_ai_request(
                client, 
                current_provider, 
                st.session_state["ai_model"],
                [
                    {"role": "system", "content": content_prompt},
                    {"role": "user", "content": user_selections}
                ]
            )
            
            # 2. 상호작용 컨텐츠 생성
            if "상호작용 활동" in content_types:
                interactive_content = make_ai_request(
                    client,
                    current_provider,
                    st.session_state["ai_model"],
                    [
                        {"role": "system", "content": INTERACTIVE_CONTENT_PROMPT},
                        {"role": "user", "content": f"기본 컨텐츠: {main_content}\n\n위 내용을 바탕으로 상호작용 활동을 구체적으로 설계해주세요."}
                    ]
                )
            else:
                interactive_content = ""
            
            # 3. 퀴즈 생성
            if "퀴즈" in content_types:
                quiz_content = make_ai_request(
                    client,
                    current_provider,
                    st.session_state["ai_model"],
                    [
                        {"role": "system", "content": QUIZ_GENERATOR_PROMPT},
                        {"role": "user", "content": f"학습 내용: {main_content}\n\n위 내용을 바탕으로 {grade} 수준의 퀴즈를 5문제 생성해주세요."}
                    ]
                )
            else:
                quiz_content = ""
            
            # 전체 컨텐츠 조합
            full_content = f"""
            <div class="module">
                <h1>{grade} {semester} - {unit_name}</h1>
                <h2>학습 목표</h2>
                <p>{learning_objectives}</p>
                
                <div class="content">
                    {main_content.replace('[이미지:', '<div class="image-placeholder">이미지: ').replace(']', '</div>')}
                </div>
                
                {f'<div class="interactive"><h3>상호작용 활동</h3>{interactive_content}</div>' if interactive_content else ''}
                
                {f'<div class="quiz"><h3>퀴즈</h3>{quiz_content}</div>' if quiz_content else ''}
            </div>
            """
            
            # Unsplash API를 사용하여 이미지 플레이스홀더를 실제 이미지로 교체
            if os.getenv("UNSPLASH_API_KEY"):
                with st.spinner("관련 이미지를 검색중입니다... 🖼️"):
                    # 메인 컨텐츠의 이미지 교체
                    main_content_with_images = replace_image_placeholders(main_content, subject)
                    # 상호작용 컨텐츠의 이미지 교체
                    if interactive_content:
                        interactive_content_with_images = replace_image_placeholders(interactive_content, subject)
                    else:
                        interactive_content_with_images = interactive_content
                    
                    # 최종 컨텐츠 조합 (이미지 포함)
                    full_content = f"""
                    <div class="module">
                        <h1>{grade} {semester} - {unit_name}</h1>
                        <h2>학습 목표</h2>
                        <p>{learning_objectives}</p>
                        
                        <div class="content">
                            {main_content_with_images}
                        </div>
                        
                        {f'<div class="interactive"><h3>상호작용 활동</h3>{interactive_content_with_images}</div>' if interactive_content_with_images else ''}
                        
                        {f'<div class="quiz"><h3>퀴즈</h3>{quiz_content}</div>' if quiz_content else ''}
                    </div>
                    """
            
            st.session_state['generated_content'] = full_content
            st.session_state['content_generated'] = True
            st.success("컨텐츠가 성공적으로 생성되었습니다! ✨")

    # 생성된 컨텐츠 표시
    if 'generated_content' in st.session_state:
        with st.expander("생성된 컨텐츠 미리보기"):
            st.markdown(st.session_state['generated_content'], unsafe_allow_html=True)
        
        # Export 옵션
        col1, col2 = st.columns(2)
        
        if st.session_state.export_format in ["HTML", "둘 다"]:
            with col1:
                # HTML 파일 생성
                html_file = generate_html(st.session_state['generated_content'], "digital_textbook.html")
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_data = f.read()
                st.download_button(
                    label="HTML로 다운로드 🌐",
                    data=html_data,
                    file_name="digital_textbook.html",
                    mime="text/html"
                )
        
        if st.session_state.export_format in ["PDF", "둘 다"]:
            with col2:
                # PDF 생성 (한글 지원 필요)
                try:
                    pdf = generate_pdf(st.session_state['generated_content'], "digital_textbook.pdf")
                    b64 = base64.b64encode(pdf.output(dest="S").encode('latin1')).decode()
                    st.download_button(
                        label="PDF로 다운로드 📄",
                        data=b64,
                        file_name="digital_textbook.pdf",
                        mime="application/pdf"
                    )
                except:
                    st.warning("PDF 생성 중 오류가 발생했습니다. HTML 형식을 사용해주세요.")
    
    else:
        st.info("👈 왼쪽에서 설정을 입력하고 '컨텐츠 생성' 버튼을 클릭하세요.")

# Save chat history after each interaction
save_chat_history(st.session_state.messages)
