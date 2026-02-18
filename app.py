import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import io

# 1. 페이지 설정
st.set_page_config(page_title="Roomie AI", page_icon="🏠", layout="wide")

# 2. 클라이언트 설정
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요.")
    st.stop()

def analyze_room(image_input, room_size, furniture, mood):
    model_id = 'gemini-2.0-flash'
    prompt = f"인테리어 전문가 분석 JSON: {room_size}, {furniture}, {mood}"
    
    response = client.models.generate_content(
        model=model_id,
        contents=[image_input, prompt],
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    return json.loads(response.text)

# 3. UI 구성
with st.sidebar:
    st.header("Design Your Space")
    img_file = st.file_uploader("방 사진", type=["png", "jpg", "jpeg"])
    room_size = st.text_input("방 크기")
    furniture = st.text_area("필요 가구")
    mood = st.text_input("스타일")
    btn = st.button("✨ 분석 시작")

st.title("Roomie AI")

if img_file:
    # --- 들여쓰기 주의: 여기서부터 모든 줄은 정확히 4칸 들여쓰기 ---
    raw_image = Image.open(img_file)
    # 이미지 최적화
    raw_image.thumbnail((600, 600), Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    raw_image.convert("RGB").save(buffer, format="JPEG", quality=70)
    buffer.seek(0)  # 버퍼의 시작점으로 이동
    image_for_ai = Image.open(buffer)
    # --------------------------------------------------------

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(raw_image, width='stretch', caption="최적화 완료")

    if btn:
        with col2:
            with st.spinner("AI 분석 중..."):
                try:
                    result = analyze_room(image_for_ai, room_size, furniture, mood)
                    st.success("분석 성공!")
                    st.write(result)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
