import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# 1. 페이지 설정 (탭 이름도 깔끔하게)
st.set_page_config(
    page_title="Roomie AI",
    page_icon="🏠",
    layout="wide"
)

# 스타일 꾸미기 (CSS) - 버튼과 카드 디자인
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
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #333333;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h3 { font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# 2. API 키 연결
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정을 확인해주세요.")
    st.stop()

def analyze_room(image, room_size, furniture, mood):
    # 모델 설정
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    당신은 수석 인테리어 디자이너입니다. 
    제공된 방 사진과 요청사항을 분석하여 감각적인 인테리어 솔루션을 제안해주세요.
    
    [요청 사항]
    - 공간 규격: {room_size}
    - 배치할 가구: {furniture}
    - 선호 분위기: {mood if mood else "공간 구조와 채광에 어울리는 최적의 스타일"}

    반드시 아래 JSON 포맷으로만 응답해주세요:
    {{
        "analysis": "공간의 장단점 및 특징 분석 (전문적인 톤으로)",
        "colors": [
            {{"hex": "#색상코드", "name": "색상명", "desc": "활용 포인트"}}
        ],
        "layout": "효율적인 동선과 공간 활용을 위한 배치 가이드",
        "items": [
            {{"name": "추천 가구", "style": "디자인/소재", "reason": "선정 이유"}}
        ]
    }}
    """
    
    response = model.generate_content(
        [image, prompt],
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

# 3. 사이드바 (입력창)
with st.sidebar:
    st.header("Design Your Space")
    st.write("공간 정보를 입력해주세요.")
    
    img_file = st.file_uploader("공간 사진 업로드", type=["png", "jpg", "jpeg", "webp"])
    room_size = st.text_input("공간 면적/규격", placeholder="예: 3m x 3.5m, 6평 원룸")
    furniture = st.text_area("필요 가구 리스트", placeholder="예: 퀸사이즈 침대, 1600 책상, 라운지 체어")
    mood = st.text_input("원하는 스타일", placeholder="예: 미니멀, 미드센추리 모던, 코지")
    
    st.markdown("---")
    btn = st.button("✨ 공간 분석 시작")

# 4. 메인 화면
st.title("Roomie AI")
st.caption("AI 인테리어 디자이너가 제안하는 맞춤형 공간 솔루션")
st.markdown("---")

if img_file:
    col1, col2 = st.columns([1, 1.2])
    
    image = Image.open(img_file)
    with col1:
        st.image(image, caption="Uploaded Space", use_container_width=True)

    if btn:
        with col2:
            with st.spinner("공간을 분석하고 스타일링을 구상 중입니다..."):
                try:
                    result = analyze_room(image, room_size, furniture, mood)
                    
                    # 결과 표시
                    st.markdown(f"""
                    <div class='card'>
                        <h3>🔍 공간 분석</h3>
                        <p style='line-height:1.6; color:#444;'>{result['analysis']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🎨 Color Palette")
                    cols = st.columns(len(result['colors']))
                    for i, c in enumerate(result['colors']):
                        cols[i].markdown(f"""
                        <div class='color-box' style='background-color:{c['hex']}'>{c['hex']}</div>
                        <div style='text-align:center; font-size:0.9em;'>
                            <b>{c['name']}</b><br>
                            <span style='color:#666; font-size:0.8em;'>{c['desc']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='card'>
                        <h3>📐 레이아웃 솔루션</h3>
                        <p style='line-height:1.6; color:#444;'>{result['layout']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### 🪑 Furniture Styling")
                    for item in result['items']:
                        st.markdown(f"""
                        <div class='card' style='padding:15px; margin-bottom:10px;'>
                            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;'>
                                <span style='font-weight:bold; font-size:1.1em;'>{item['name']}</span>
                                <span style='background:#eee; padding:2px 8px; border-radius:4px; font-size:0.8em;'>{item['style']}</span>
                            </div>
                            <p style='margin:0; color:#666; font-size:0.95em;'>{item['reason']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"분석 중 문제가 발생했습니다: {e}")
else:
    # 사진 없을 때 빈 화면 안내
    st.markdown("""
    <div style='text-align:center; padding: 50px; color:#666;'>
        <h3>👋 환영합니다!</h3>
        <p>왼쪽 사이드바에서 <b>방 사진</b>을 업로드하고<br>나만의 공간 컨설팅을 받아보세요.</p>
    </div>
    """, unsafe_allow_html=True)