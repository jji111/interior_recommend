import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import time

# 1. 페이지 설정
st.set_page_config(page_title="Roomie AI", page_icon="🏠", layout="wide")

# 2026년형 스타일링 (메뉴 숨기기)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button {
        width: 100%; background-color: #1E1E1E; color: white;
        font-weight: 600; height: 3.5em; border-radius: 8px; border: none;
    }
    .card {
        background-color: #f8f9fa; padding: 24px; border-radius: 12px;
        border: 1px solid #e9ecef; margin-bottom: 20px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    </style>
""", unsafe_allow_html=True)

# 2. 클라이언트 설정
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요 (Streamlit Secrets).")
    st.stop()

def analyze_room(image, room_size, furniture, mood):
    # 2026년 현재 가장 안정적인 2.0 모델 사용
    model_id = 'gemini-2.0-flash'
    
    prompt = f"""
    당신은 수석 인테리어 디자이너입니다. 
    공간({room_size}), 가구({furniture}), 스타일({mood})을 분석하여 
    최적의 인테리어 솔루션을 JSON 형식으로 응답하세요.
    """
    
    response = client.models.generate_content(
        model=model_id,
        contents=[image, prompt],
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    return json.loads(response.text)

# 3. UI 구성
with st.sidebar:
    st.header("Design Your Space")
    img_file = st.file_uploader("방 사진 업로드", type=["png", "jpg", "jpeg", "webp"])
    room_size = st.text_input("방 크기", placeholder="예: 6평, 20m²")
    furniture = st.text_area("필요 가구", placeholder="예: 침대, 책상")
    mood = st.text_input("원하는 스타일", placeholder="예: 모던, 우드톤")
    btn = st.button("✨ 분석 시작")

st.title("Roomie AI")
st.markdown("---")

if img_file:
    col1, col2 = st.columns([1, 1.2])
    image = Image.open(img_file)
    with col1:
        # [2026년 업데이트] use_container_width 대신 width='stretch' 사용
        st.image(image, width='stretch', caption="현재 공간")

    if btn:
        with col2:
            # 429 에러 방지를 위한 아주 짧은 대기 (0.5초)
            time.sleep(0.5)
            with st.spinner("AI가 분석 중입니다..."):
                try:
                    result = analyze_room(image, room_size, furniture, mood)
                    st.success("분석 완료!")
                    st.json(result)
                except Exception as e:
                    # 429 에러(한도 초과) 발생 시 안내 문구
                    if "429" in str(e):
                        st.error("⚠️ 무료 버전 사용량이 일시적으로 초과되었습니다. 1분만 기다렸다가 다시 눌러주세요!")
                    else:
                        st.error(f"분석 중 오류 발생: {e}")
else:
    st.info("👈 왼쪽에서 사진을 업로드해주세요.")
