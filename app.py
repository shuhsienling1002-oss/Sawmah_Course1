import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---\
st.set_page_config(
    page_title="Kaolahan - 所喜歡的", 
    page_icon="💖", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 (賽博龐克霓虹風 - 高對比版) ---\
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600&family=Noto+Sans+TC:wght@300;500;700&display=swap');

    /* 全局背景：深空黑 + 網格 */
    .stApp { 
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(255, 0, 128, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
        font-family: 'Noto Sans TC', 'Rajdhani', sans-serif; /* 優先使用中文優化字體 */
        color: #FFFFFF; /* 全局文字預設為白色，確保可讀性 */
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* --- Header (全息投影面板) --- */
    .header-container {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid #FF0080;
        box-shadow: 0 0 15px rgba(255, 0, 128, 0.4), inset 0 0 20px rgba(255, 0, 128, 0.1);
        border-radius: 5px;
        padding: 25px;
        text-align: center;
        margin-bottom: 40px;
        position: relative;
        overflow: hidden;
    }
    
    /* 掃描線動畫效果 */
    .header-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: rgba(0, 255, 255, 0.5);
        box-shadow: 0 0 10px #00E5FF;
        animation: scan 3s linear infinite;
        opacity: 0.6;
    }

    @keyframes scan {
        0% { top: 0%; }
        100% { top: 100%; }
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #FF0080, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(255, 0, 128, 0.5);
    }
    
    .sub-title { 
        color: #00E5FF; 
        font-size: 20px; 
        margin-top: 5px; 
        font-weight: 700; 
        letter-spacing: 1px; 
        text-shadow: 0 0 5px rgba(0, 229, 255, 0.6);
    }
    
    .teacher-tag { 
        display: inline-block; 
        margin-top: 15px; 
        padding: 6px 15px; 
        background: rgba(255, 0, 255, 0.15); 
        color: #FF80FF; /* 亮粉色，提高可讀性 */
        border: 1px solid #FF00FF;
        font-size: 14px; 
        font-weight: bold;
        box-shadow: 0 0 5px rgba(255, 0, 255, 0.4);
        border-radius: 4px;
    }

    /* --- Cards (HUD 數據框風格) --- */
    .word-card {
        background: rgba(30, 30, 30, 0.8); /* 背景加深，增加文字對比 */
        backdrop-filter: blur(5px);
        border: 1px solid #555;
        border-left: 4px solid #00E5FF; 
        padding: 15px 10px;
        text-align: center;
        height: 100%;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        position: relative;
    }
    
    /* 角落裝飾 */
    .word-card::before {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 10px; height: 10px;
        border-top: 2px solid #00E5FF;
        border-right: 2px solid #00E5FF;
    }

    .word-card h3 {
        color: #FFFFFF !important; /* 純白標題 */
        font-family: 'Orbitron', 'Noto Sans TC', sans-serif;
        font-weight: 700;
        margin: 0;
        padding-bottom: 8px;
        font-size: 22px;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    .word-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4); 
        border-color: #00E5FF;
        background: rgba(0, 229, 255, 0.1);
    }
    
    .icon-box { font-size: 30px; margin-bottom: 5px; filter: drop-shadow(0 0 5px rgba(255,255,255,0.5)); }
    
    /* 中文解釋文字：改成亮灰色，確保清楚 */
    .zh-word { font-size: 16px; color: #DDDDDD; font-weight: 500; font-family: 'Noto Sans TC'; }

    /* --- Sentences (終端機風格) --- */
    .sentence-box {
        background: #111111;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px dashed #555;
        border-left: 3px solid #FF00FF;
        font-family: 'Noto Sans TC', monospace;
    }
    .sentence-amis { 
        font-size: 20px; 
        color: #FF55FF; /* 亮洋紅 */
        font-weight: 700; 
        margin-bottom: 8px; 
        text-shadow: 0 0 5px rgba(255,0,255,0.4); 
    }
    .sentence-zh { 
        font-size: 16px; 
        color: #EEEEEE; /* 幾乎純白，確保好讀 */
        font-weight: 400;
    }

    /* --- Buttons (發光按鈕) --- */
    .stButton>button { 
        width: 100%; 
        border-radius: 0px; 
        background: rgba(0, 0, 0, 0.5); 
        border: 1px solid #00E5FF; 
        color: #00E5FF !important; 
        font-family: 'Noto Sans TC', sans-serif;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s;
    }
    .stButton>button:hover { 
        background: #00E5FF; 
        color: #000 !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.8);
        border-color: #FFFFFF;
    }
    .stButton>button:active { transform: scale(0.98); }

    /* --- Tabs (導航欄) --- */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] {
        color: #AAAAAA !important; 
        background-color: transparent !important;
        font-family: 'Noto Sans TC', sans-serif;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #00E5FF !important;
        border-bottom: 2px solid #00E5FF;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        font-weight: bold;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00E5FF, #FF00FF);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料設定 (主題：Kaolahan 所喜歡的) ---
VOCABULARY = [
    {"amis": "kaolahan",  "zh": "所喜歡的",   "emoji": "💖", "file": "v_kaolahan"},
    {"amis": "facidol",   "zh": "麵包樹果",   "emoji": "🍈", "file": "v_facidol"},
    {"amis": "haca",      "zh": "也",         "emoji": "➕", "file": "v_haca"},
    {"amis": "maemin",    "zh": "全部",       "emoji": "👐", "file": "v_maemin"},
    {"amis": "sikaen",    "zh": "菜餚",       "emoji": "🍱", "file": "v_sikaen"},
    {"amis": "dateng",    "zh": "菜",         "emoji": "🥬", "file": "v_dateng"},
    {"amis": "kohaw",     "zh": "湯",         "emoji": "🥣", "file": "v_kohaw"},
    {"amis": "mato'asay", "zh": "老人",       "emoji": "👵", "file": "v_matoasay"},
]

SENTENCES = [
    {"amis": "O maan ko kaolahan iso a sikaen?", 
     "zh": "你喜歡什麼樣的菜呢？", 
     "emoji": "❓", "file": "s_o_maan_ko_kaolahan"},
     
    {"amis": "O foting ko kaolahan ako a dateng.", 
     "zh": "魚是我最喜歡的菜。", 
     "emoji": "🐟", "file": "s_o_foting_ko_kaolahan"},
     
    {"amis": "Kaolahan no wama konini a kohaw.", 
     "zh": "這碗是爸爸最喜歡的湯。", 
     "emoji": "👨", "file": "s_kaolahan_no_wama"},
     
    {"amis": "Tadakaolahan no mato'asay kona dateng.", 
     "zh": "這些是老人家最喜歡的菜。", 
     "emoji": "👵", "file": "s_tadakaolahan_no_matoasay"},
     
    {"amis": "Kaolahan ako a maemin konini a sikaen.", 
     "zh": "這些都是我最喜歡的菜餚。", 
     "emoji": "😋", "file": "s_kaolahan_ako_a_maemin"},
     
    {"amis": "O facidol i, o tadakaolahan haca no 'Amis.", 
     "zh": "麵包樹果也是阿美族人最愛。", 
     "emoji": "🍈", "file": "s_o_facidol_i"},
]

# 測驗題庫
QUIZ_DATA = [
    {"q": "O maan ko ______ iso a sikaen? / 你喜歡什麼...", "zh": "所喜歡的", "ans": "kaolahan", "opts": ["kaolahan", "facidol", "haca"]},
    {"q": "______ no wama konini a kohaw / 爸爸喜歡的湯", "zh": "所喜歡的", "ans": "Kaolahan", "opts": ["Kaolahan", "Maemin", "Dateng"]},
    {"q": "O ______ i, o tadakaolahan haca / 麵包樹果", "zh": "麵包樹果", "ans": "facidol", "opts": ["facidol", "kohaw", "sikaen"]},
    {"q": "Kaolahan ako a ______ konini / 這些全部", "zh": "全部", "ans": "maemin", "opts": ["maemin", "haca", "mato'asay"]},
    {"q": "Tadakaolahan no ______ / 老人家", "zh": "老人", "ans": "mato'asay", "opts": ["mato'asay", "wama", "foting"]},
]

# --- 1.5 語音核心 ---
def play_audio(text, filename_base=None):
    if filename_base:
        extensions = ['m4a', 'mp3', 'wav']
        folders = ['audio', '.'] 
        for folder in folders:
            for ext in extensions:
                path = os.path.join(folder, f"{filename_base}.{ext}")
                if os.path.exists(path):
                    mime = 'audio/mp4' if ext == 'm4a' else 'audio/mp3'
                    st.audio(path, format=mime)
                    return 
        # 樣式微調：配合暗色背景
        st.markdown(f"<span style='color:#FF00FF; font-size:12px; border:1px solid #FF00FF; padding:2px 5px;'>🔇 缺少音檔: {filename_base}</span>", unsafe_allow_html=True)
    else:
        try:
            speak_text = text.split('/')[0].strip()
            tts = gTTS(text=speak_text, lang='id') 
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format='audio/mp3')
        except:
            st.caption("🔇")

# --- 2. 測驗邏輯 ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1: 聽力
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2: 填空
    q2_data = random.choice(QUIZ_DATA)
    random.shuffle(q2_data['opts'])
    st.session_state.q2_data = q2_data

    # Q3: 句子翻譯
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    if len(other_sentences) < 2:
        q3_options = other_sentences + [q3_target['zh']] + ["天氣很好"]
        q3_options = q3_options[:3]
    else:
        q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面呈現 ---
def show_learning_mode():
    st.markdown("<h3 style='color:#00E5FF; text-align:center; margin-bottom:20px; font-family:Orbitron;'>// 單字資料庫 (Vocabulary)</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, item in enumerate(VOCABULARY):
        with cols[idx % 3]:
            # 根據順序給予不同的邊框顏色
            border_color = ["#00E5FF", "#FF00FF", "#FFFF00"][idx % 3]
            
            st.markdown(f"""
            <div class="word-card" style="border-left-color: {border_color};">
                <div class="icon-box">{item['emoji']}</div>
                <h3>{item['amis']}</h3>
                <div class="zh-word">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])
            st.write("") 

    st.markdown("---")
    st.markdown("<h3 style='color:#FF00FF; text-align:center; margin-bottom:20px; font-family:Orbitron;'>// 例句檔案 (Sentences)</h3>", unsafe_allow_html=True)
    
    for item in SENTENCES:
        st.markdown(f"""
        <div class="sentence-box">
            <div class="sentence-amis">>> {item['amis']}</div>
            <div class="sentence-zh">{item['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(item['amis'], filename_base=item['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #E0E0E0; font-family:Orbitron;'>// 系統測驗 (System Test)</h3>", unsafe_allow_html=True)
    st.progress((st.session_state.current_q) / 3)
    st.write("")

    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        st.markdown(f"""
        <div class="word-card" style="border-left-color:#00E5FF;">
            <h3>🎧 聽力同步檢測</h3>
            <p style="color:#CCCCCC;">請選擇與聲音相符的單字</p>
        </div>
        """, unsafe_allow_html=True)
        play_audio(target['amis'], filename_base=target['file'])
        st.write("")
        
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                if st.button(f"{opt['zh']}", key=f"q1_{idx}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success("存取授權 (答對了)")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("存取拒絕 (再試一次)")

    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        st.markdown(f"""
        <div class="word-card" style="border-left-color:#FFFF00;">
            <h3>🧩 數據修復 (填空)</h3>
            <h2 style="color:#FFF;">{data['q'].replace('______', '<span style="color:#FFFF00; text-shadow:0 0 10px #FFFF00;">[ 遺失數據 ]</span>')}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, opt in enumerate(data['opts']):
            with cols[i]:
                if st.button(opt, key=f"q2_{i}"):
                    if opt.lower() in data['ans'].lower() or data['ans'].lower() in opt.lower():
                        st.balloons()
                        st.success("數據已修復 (太棒了)")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("錯誤 (不對喔)")

    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown(f"""
        <div class="word-card" style="border-left-color:#FF00FF;">
            <h3>🗣️ 翻譯協定</h3>
            <h3 style="color:#FF00FF;">{target['amis']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        play_audio(target['amis'], filename_base=target['file'])
        
        for opt in data['options']:
            if st.button(opt):
                if opt == target['zh']:
                    st.balloons()
                    st.success("同步完成 (全對)")
                    time.sleep(1)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("同步失敗 (再想一下)")

    else:
        st.markdown(f"""
        <div class="word-card" style="border-left: 4px solid #00E5FF; background: rgba(0, 229, 255, 0.1);">
            <h1 style='color: #00E5FF; font-family:Orbitron;'>任務完成 (Mission Complete)</h1>
            <p style='color:#FFF;'>得分: {st.session_state.score} / 3</p>
            <div style='font-size: 60px;'>🚀</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("重啟系統 (重新開始)"):
            init_quiz()
            st.rerun()

# --- 4. 診斷工具 ---
def show_debug_info():
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#888; font-size:12px; font-family:Orbitron;">
        SYSTEM VER 2.0 | DEVELOPED BY AI | POWERED BY STREAMLIT
    </div>
    """, unsafe_allow_html=True)

# --- 主程式 ---
def main():
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">KAOLAHAN</h1>
        <div class="sub-title">所喜歡的</div>
        <div class="teacher-tag">講師：高春美 | 教材提供者：高春美</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📂 單字學習", "⚔️ 自我測驗"])
    
    with tab1:
        show_learning_mode()
    with tab2:
        show_quiz_mode()
        
    show_debug_info()

if __name__ == "__main__":
    main()
