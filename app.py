import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

# 1. 페이지 설정
st.set_page_config(page_title="Roomie AI", page_icon="🏠", layout="wide")

# CSS 스타일 (메뉴 숨기기)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    .stButton>button {
        width: 100%; background-color: #1E1E1E; color: white;
        font-weight: 600; height: 3.5em; border-radius: 8px; border: none;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 클라이언트 설정
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요.")
    st.stop()

def analyze_room(image, room_size, furniture, mood):
    # [안정성 확보] 2.0보다 한도가 넉넉한 1.5-flash 사용
    model_id = 'gemini-1.5-flash'
    
    prompt = f"방 사진을 분석하여 인테리어 솔루션을 JSON으로 제공하세요. 면적:{room_size}, 가구:{furniture}, 스타일:{mood}"
    
    response = client.models.generate_content(
        model=model_id,
        contents=[image, prompt],
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    return json.loads(response.text)

# 3. UI
with st.sidebar:
    st.header("Design Your Space")
    img_file = st.file_uploader("방 사진 업로드 (3MB 이상도 OK)", type=["png", "jpg", "jpeg"])
    room_size = st.text_input("방 크기")
    furniture = st.text_area("필요 가구")
    mood = st.text_input("원하는 스타일")
    btn = st.button("✨ 분석 시작")

st.title("Roomie AI")

if img_file:
    image = Image.open(img_file)
    
    # --- [이미지 최적화: 429 에러 방지 핵심] ---
    # 사진이 잘리지 않게 비율을 유지하며 용량만 줄입니다.
    # [Image of digital image resizing process]
    image.thumbnail((800, 800), Image.Resampling.LANCZOS)
    # ----------------------------------------

    col1, col2 = st.columns([1, 1.2])
    with col1:
        # [2026년 규격] width='stretch' 사용 (로그 경고 해결)
        st.image(image, width='stretch', caption="최적화된 이미지")

    if btn:
        with col2:
            with st.spinner("AI가 분석 중... (한도 최적화 모드)"):
                try:
                    result = analyze_room(image, room_size, furniture, mood)
                    st.success("분석 완료!")
                    st.write(result)
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ 구글 서버가 바쁩니다. 1분만 쉬었다가 다시 눌러주세요!")
                    else:
                        st.error(f"오류 발생: {e}")
