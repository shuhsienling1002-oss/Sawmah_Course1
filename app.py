import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="O kakonah - 螞蟻", 
    page_icon="🐜", 
    layout="centered"
)

# --- CSS 視覺魔法 (賽博龐克 - 螞蟻森林版 + 高對比修正) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+TC:wght@300;500;700&display=swap');

    /* 全局背景 */
    .stApp { 
        background-color: #0a0e05;
        background-image: linear-gradient(rgba(57, 255, 20, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(57, 255, 20, 0.05) 1px, transparent 1px);
        background-size: 25px 25px;
        color: #ECF0F1;
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    /* Header 面板 */
    .header-container {
        background: rgba(0, 20, 0, 0.8);
        border: 2px solid #39FF14;
        box-shadow: 0 0 20px rgba(57, 255, 20, 0.3);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #39FF14;
        font-size: 40px;
        text-shadow: 0 0 10px #39FF14;
        margin-bottom: 5px;
    }

    /* --- 修正 Tabs 可讀性 (Critical Patch) --- */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px 5px 0 0;
        color: #FFFFFF !important; /* 強制純白 */
        font-weight: 500;
        border: 1px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(57, 255, 20, 0.1) !important;
        border: 1px solid #39FF14;
        border-bottom: none;
        color: #39FF14 !important; /* 選中變綠 */
        font-weight: bold;
        box-shadow: 0 -5px 10px rgba(57, 255, 20, 0.1);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(57, 255, 20, 0.2);
        color: #39FF14 !important;
    }

    /* 單字卡片 */
    .word-card {
        background: rgba(20, 30, 20, 0.9);
        border: 1px solid #39FF14;
        border-left: 5px solid #39FF14;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        transition: 0.3s;
        position: relative;
    }
    .word-card:hover {
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.6);
        transform: scale(1.02);
    }
    
    .amis-text { color: #39FF14; font-size: 24px; font-weight: bold; }
    .zh-text { color: #BBBBBB; font-size: 16px; margin-top: 5px; }
    .root-tag { 
        font-size: 12px; 
        color: #000; 
        background: #39FF14; 
        padding: 2px 6px; 
        border-radius: 3px;
        font-weight: bold;
        float: right;
    }

    /* 語法重點框 */
    .grammar-box {
        background:rgba(57,255,20,0.05); 
        padding:15px; 
        border:1px dashed #39FF14; 
        margin-bottom:15px;
        border-radius: 5px;
    }
    .grammar-title { color: #39FF14; font-weight: bold; font-family: 'Orbitron'; }

    /* 按鈕樣式 */
    .stButton>button {
        border: 1px solid #39FF14 !important;
        background: transparent !important;
        color: #39FF14 !important;
        width: 100%;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background: #39FF14 !important;
        color: #000 !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料庫 (依據第1課內容) ---
VOCABULARY = [
    {"amis": "kakonah", "zh": "螞蟻", "emoji": "🐜", "root": "kakonah"},
    {"amis": "malalokay", "zh": "勤勞的", "emoji": "💪", "root": "lalok"},
    {"amis": "fao", "zh": "昆蟲/蟲", "emoji": "🐛", "root": "fao"},
    {"amis": "foloday", "zh": "一群的", "emoji": "👥", "root": "folod"},
    {"amis": "tayal", "zh": "工作", "emoji": "🛠️", "root": "tayal"},
    {"amis": "posak", "zh": "飯粒", "emoji": "🍚", "root": "posak"},
    {"amis": "liliden", "zh": "搬移(被...)", "emoji": "📦", "root": "lilid"},
    {"amis": "matefaday", "zh": "掉下來的", "emoji": "🍂", "root": "tefad"},
]

SENTENCES = [
    {"amis": "O tada malalokay a fao ko kakonah.", "zh": "螞蟻是非常勤勞的昆蟲。", "note": "O...ko... (A是B)"},
    {"amis": "Saheto o foloday a masadak cangra.", "zh": "牠們都是成群結隊地出來。", "note": "Saheto (全部/都)"},
    {"amis": "Liliden nangra ko matefaday a posak.", "zh": "牠們搬運掉下來的飯粒。", "note": "OF 處置焦點：強調飯粒(posak)"},
]

STORY = """
O kakonah hananay i, o tada malalokay a fao.
Ano matayal cangra i, saheto o foloday a masadak.
Caay ka pahanhan ko tayal nangra.
Ma'araw nangra ko matefaday a posak i lalan.
Liliden nangra kora posak a panokay.
Mafana' a mapapadang ko kakonah.
Saka, matatodong a minanam kita to lalok no kakonah.
"""

STORY_ZH = """
所謂的螞蟻，是非常勤勞的昆蟲。
當牠們工作時，都是成群結隊地出來。
牠們的工作從不休息。
牠們看見了掉在路上的飯粒。
牠們便將那飯粒搬運回家。
螞蟻懂得互相幫助。
所以，我們值得學習螞蟻的勤勞。
"""

# --- 2. 語音與工具 ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='id') 
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔊 語音模組連線中...")

def init_quiz():
    st.session_state.quiz_pool = random.sample(VOCABULARY, 3)
    st.session_state.step = 0
    st.session_state.score = 0
    # 清除舊的選項紀錄，確保新局開始是乾淨的
    if 'current_options' in st.session_state:
        del st.session_state.current_options

# --- 3. UI 呈現 ---
st.markdown("""
    <div class="header-container">
        <div class="main-title">O KAKONAH</div>
        <div style="color: #39FF14; letter-spacing: 5px; font-weight:bold;">第 1 課：螞蟻</div>
        <div style="font-size: 12px; margin-top:10px; color:#888;">講師：高生榮 | 教材：高生榮</div>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🐜 課文朗讀", "📖 核心單字", "🧬 句型解析", "⚔️ 實戰測驗"])

with tab1:
    st.markdown("### // 沉浸模式 (Immersion)")
    st.markdown(f"""
    <div style="padding:20px; border-left:4px solid #39FF14; background:rgba(20,20,20,0.5);">
        <p style="font-size:18px; line-height:1.6; color:#EEE;">{STORY.replace(chr(10), '<br>')}</p>
        <hr style="border-color:#333;">
        <p style="font-size:16px; color:#AAA;">{STORY_ZH.replace(chr(10), '<br>')}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔊 播放全課文"):
        play_audio(STORY.replace('\n', ' '))

with tab2:
    st.markdown("### // 數據掃描：原子單字")
    for v in VOCABULARY:
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            st.markdown(f"""
            <div class="word-card">
                <span class="root-tag">ROOT: {v['root']}</span>
                <div class="amis-text">{v['emoji']} {v['amis']}</div>
                <div class="zh-text">{v['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.write("") 
            if st.button("🔊", key=f"voc_{v['amis']}"):
                play_audio(v['amis'])

with tab3:
    st.markdown("### // 語法解碼：句型結構")
    for s in SENTENCES:
        st.markdown(f"""
        <div class="grammar-box">
            <div style="color:#39FF14; font-size:18px; font-weight:bold; margin-bottom:5px;">>> {s['amis']}</div>
            <div style="color:#FFF; margin-bottom:8px;">{s['zh']}</div>
            <div style="color:#CCC; font-size:13px; border-top:1px dashed #555; padding-top:5px;">
                <span class="grammar-title">ANALYSIS:</span> {s['note']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("唸句型", key=f"sen_{s['amis'][:5]}"):
            play_audio(s['amis'])

with tab4:
    st.markdown("### // 認知驗證 (Quiz)")
    if 'quiz_pool' not in st.session_state:
        init_quiz()
    
    if st.session_state.step < len(st.session_state.quiz_pool):
        current_q = st.session_state.quiz_pool[st.session_state.step]
        st.markdown(f"#### Q{st.session_state.step + 1}: 請選擇「<span style='color:#39FF14'>{current_q['zh']}</span>」的阿美語", unsafe_allow_html=True)
        
        # --- 核心修復：選項鎖定邏輯 ---
        # 檢查是否已經為當前題目生成過選項，如果沒有（或是進入新的一題），則生成並儲存
        # 使用 'current_q_amis' 來判斷是否是同一題
        if 'current_options' not in st.session_state or st.session_state.current_q_ref != current_q['amis']:
            
            # 生成選項
            options = [current_q['amis']] + [v['amis'] for v in random.sample(VOCABULARY, 3) if v['amis'] != current_q['amis']]
            options = options[:3] 
            random.shuffle(options)
            
            # 鎖定狀態
            st.session_state.current_options = options
            st.session_state.current_q_ref = current_q['amis']
        
        # 從鎖定的狀態中讀取選項，而不是重新生成
        locked_options = st.session_state.current_options
        
        cols = st.columns(3)
        for i, opt in enumerate(locked_options):
            with cols[i]:
                # 這裡的 opt 來自 locked_options，不會因為頁面重整而改變順序
                if st.button(opt, key=f"opt_{i}_{st.session_state.step}"):
                    if opt == current_q['amis']:
                        st.success("通過 (Access Granted)")
                        st.session_state.score += 1
                        time.sleep(1) # 讓用戶看到成功訊息
                    else:
                        st.error(f"錯誤 (Denied) - 正解: {current_q['amis']}")
                        time.sleep(2) # 錯誤時多停留一下
                    
                    # 進入下一題
                    st.session_state.step += 1
                    st.rerun()
    else:
        st.markdown(f"""
        <div style="text-align:center; padding:30px; border:2px solid #39FF14; background:rgba(57,255,20,0.1);">
            <h2 style="color:#39FF14">MISSION COMPLETE</h2>
            <p>最終得分: {st.session_state.score} / 3</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("重新啟動系統 (Reboot)"):
            init_quiz()
            st.rerun()

st.markdown("---")
st.caption("SYSTEM VER 6.5 | Bug Fixed: Option Stability Protocol")
