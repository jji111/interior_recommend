import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import time
import io

# 1. 페이지 설정
st.set_page_config(page_title="Roomie AI", page_icon="🏠", layout="wide")

# CSS (메뉴 숨기기)
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. 클라이언트 설정
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요.")
    st.stop()

def analyze_room(image_bytes, room_size, furniture, mood):
    # 404가 나지 않았던 유일한 모델: 2.0-flash
    model_id = 'gemini-2.0-flash'
    
    # PIL 이미지를 다시 바이츠로 변환 (압축된 상태 유지)
    image_input = Image.open(io.BytesIO(image_bytes))
    
    prompt = f"인테리어 분석 JSON: 면적 {room_size}, 가구 {furniture}, 스타일 {mood}"
    
    response = client.models.generate_content(
        model=model_id,
        contents=[image_input, prompt],
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    return json.loads(response.text)

# 3. UI
with st.sidebar:
    st.header("Design Your Space")
    img_file = st.file_uploader("방 사진 (3.5MB도 전송 가능하도록 압축됨)", type=["png", "jpg", "jpeg"])
    room_size = st.text_input("방 크기")
    furniture = st.text_area("필요 가구")
    mood = st.text_input("원하는 스타일")
    btn = st.button("✨ 분석 시작")

st.title("Roomie AI")

if img_file:
    # --- [이미지 극단적 압축 로직] ---
    raw_image = Image.open(img_file)
    # 1. 해상도를 600px로 확 줄임 (AI 분석에는 충분함)
    raw_image.thumbnail((600, 600), Image.Resampling.LANCZOS)
    
    # 2. JPEG 화질을 60%로 낮춰 용량을 수십 KB로 만듦 (429 에러 방지 핵심)
    buffer = io.BytesIO()
    raw_image.convert("RGB").save(buffer, format="JPEG", quality=60)
    compressed_bytes = buffer.getvalue()
    # -------------------------------

    col1, col2 = st.columns([1, 1.2])
    with col1:
        # [2026 규격] width='stretch' 사용 (로그 경고 해결)
        st.image(raw_image, width='stretch', caption=f"최적화 완료 (약 {len(compressed_bytes)/1024:.1f} KB)")

    if btn:
        with col2:
            # 안전을 위해 2초 대기 (API Rate Limit 준수)
            time.sleep(2)
            with st.spinner("최적화된 데이터로 AI 분석 중..."):
                try:
                    result = analyze_room(compressed_bytes, room_size, furniture, mood)
                    st.success("분석 성공!")
                    st.write(result)
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ 아직 구글 서버가 당신을 차단 중입니다. 1분만 더 기다렸다가 눌러주세요!")
                    else:
                        st.error(f"오류: {e}")
