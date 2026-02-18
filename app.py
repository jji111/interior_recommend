import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import io
import time

# 1. 페이지 설정
st.set_page_config(page_title="Roomie AI", page_icon="🏠", layout="wide")

# 2. 클라이언트 설정
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요.")
    st.stop()

def analyze_room(image_bytes, room_size, furniture, mood):
    # [안정성 최우선] 429 에러가 가장 적은 8b(가벼운) 모델 사용
    model_id = 'gemini-1.5-flash-8b'
    
    image_input = Image.open(io.BytesIO(image_bytes))
    prompt = f"인테리어 분석 JSON: {room_size}, {furniture}, {mood}"
    
    # 404 방지를 위해 모델 리스트를 명시적으로 호출하는 방식
    response = client.models.generate_content(
        model=model_id,
        contents=[image_input, prompt],
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    return json.loads(response.text)

# 3. UI
with st.sidebar:
    st.header("Design Your Space")
    img_file = st.file_uploader("방 사진", type=["png", "jpg", "jpeg"])
    room_size = st.text_input("방 크기")
    furniture = st.text_area("필요 가구")
    mood = st.text_input("스타일")
    btn = st.button("✨ 분석 시작")

if img_file:
    # --- [초압축: 429 에러 원천 차단] ---
    raw_image = Image.open(img_file)
    raw_image.thumbnail((512, 512), Image.Resampling.LANCZOS) # 더 작게 줄임
    
    buffer = io.BytesIO()
    raw_image.convert("RGB").save(buffer, format="JPEG", quality=50) # 화질 50%
    compressed_bytes = buffer.getvalue()
    # -------------------------------

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(raw_image, width='stretch', caption=f"압축 완료 ({len(compressed_bytes)/1024:.1f}KB)")

    if btn:
        with col2:
            with st.spinner("가장 가벼운 모델로 분석 중..."):
                try:
                    # 429 방지를 위해 3초 대기
                    time.sleep(3)
                    result = analyze_room(compressed_bytes, room_size, furniture, mood)
                    st.success("드디어 분석 성공!")
                    st.write(result)
                except Exception as e:
                    st.error(f"⚠️ 현재 구글 API 한도 초과 상태입니다.\n\n해결법: 1. 새 API 키 발급 2. 내일 다시 시도\n\n(상세: {e})")
