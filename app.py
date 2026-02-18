import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json
import io

# 1. 페이지 설정
st.set_page_config(page_title="Roomie AI", page_icon="🏠", layout="wide")

# 2. 클라이언트 설정 (새로 발급받은 API 키 사용)
try:
    # 2026년형 google-genai 방식
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ Streamlit Secrets에서 API 키가 올바른지 확인해주세요.")
    st.stop()

def analyze_room(image_input, room_size, furniture, mood):
    # 404 에러가 나지 않는 확실한 모델 이름
    model_id = 'gemini-2.0-flash'
    
    prompt = f"인테리어 전문가로서 분석해주세요. JSON 형식으로 응답하세요. 면적:{room_size}, 가구:{furniture}, 스타일:{mood}"
    
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
    # --- [이미지 최적화: 429 에러 방지 핵심] ---
    raw_image = Image.open(img_file)
    # 해상도를 600px로 줄여서 전송량을 최소화합니다.
    # image = Image.open(img_file) 바로 아래 추가    
    # 해상도를 512px로 더 줄이고, 화질을 50%로 압축하여 데이터 양을 최소화합니다.
    raw_image.thumbnail((512, 512), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    raw_image.convert("RGB").save(buffer, format="JPEG", quality=50)
    image_for_ai = Image.open(buffer)
    # ----------------------------------------

    col1, col2 = st.columns([1, 1.2])
    with col1:
        # [2026년형 규격] width='stretch' 사용 (로그 경고 해결)
        st.image(raw_image, width='stretch', caption="최적화 완료")

    if btn:
        with col2:
            with st.spinner("새로운 프로젝트 할당량으로 분석 중..."):
                try:
                    # 압축된 이미지를 전송
                    result = analyze_room(image_for_ai, room_size, furniture, mood)
                    st.success("분석 성공!")
                    st.write(result)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    st.info("혹시 새 API 키를 넣고 'Save' 버튼을 누르셨나요?")


