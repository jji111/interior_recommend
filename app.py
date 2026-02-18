import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# 1. 페이지 설정
st.set_page_config(
    page_title="Roomie AI",
    page_icon="🏠",
    layout="wide"
)

# CSS 스타일 (메뉴바 숨기기 포함)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button {
        width: 100%;
        background-color: #1E1E1E; 
        color: white;
        font-weight: 600;
        height: 3.5em;
        border-radius: 8px;
        border: none;
    }
    .card {
        background-color: #f8f9fa;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
    .color-box {
        width: 100%; height: 80px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        margin-bottom: 8px;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. API 키 연결
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요 (Streamlit Secrets).")
    st.stop()

def analyze_room(image, room_size, furniture, mood):
    # 모델 이름 수정: gemini-1.5-flash-latest
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""
    당신은 수석 인테리어 디자이너입니다. 
    제공된 방 사진과 요청사항을 분석하여 감각적인 인테리어 솔루션을 제안해주세요.
    반드시 아래 JSON 포맷으로만 응답해주세요:
    {{
        "analysis": "공간의 특징 분석",
        "colors": [{{"hex": "#코드", "name": "색상명", "desc": "이유"}}],
        "layout": "가구 배치 가이드",
        "items": [{{"name": "가구", "style": "스타일", "reason": "이유"}}]
    }}
    """
    
    response = model.generate_content(
        [image, prompt],
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

# 3. 사이드바 및 메인 화면
with st.sidebar:
    st.header("Design Your Space")
    img_file = st.file_uploader("공간 사진 업로드", type=["png", "jpg", "jpeg", "webp"])
    room_size = st.text_input("공간 면적", placeholder="예: 3m x 3.5m")
    furniture = st.text_area("필요 가구", placeholder="예: 침대, 책상")
    mood = st.text_input("원하는 스타일", placeholder="예: 미니멀, 우드톤")
    btn = st.button("✨ 공간 분석 시작")

st.title("Roomie AI")
st.markdown("---")

if img_file:
    col1, col2 = st.columns([1, 1.2])
    image = Image.open(img_file)
    with col1:
        st.image(image, caption="Uploaded Space", use_container_width=True)

    if btn:
        with col2:
            with st.spinner("AI가 분석 중입니다..."):
                try:
                    result = analyze_room(image, room_size, furniture, mood)
                    st.success("분석 완료!")
                    
                    st.markdown(f"<div class='card'><h3>🔍 분석 결과</h3><p>{result['analysis']}</p></div>", unsafe_allow_html=True)
                    
                    st.markdown("### 🎨 Color Palette")
                    cols = st.columns(len(result['colors']))
                    for i, c in enumerate(result['colors']):
                        cols[i].markdown(f"<div class='color-box' style='background-color:{c['hex']}'>{c['hex']}</div><p style='text-align:center'><b>{c['name']}</b></p>", unsafe_allow_html=True)

                    st.markdown(f"<div class='card'><h3>📐 레이아웃 솔루션</h3><p>{result['layout']}</p></div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"상세 에러 발생: {e}")
else:
    st.info("👈 왼쪽에서 사진을 업로드해주세요.")
