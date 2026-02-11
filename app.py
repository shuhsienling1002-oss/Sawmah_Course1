import streamlit as st
import time
import os
import random
import re
from gtts import gTTS
from io import BytesIO
import base64

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="O kakonah - 螞蟻", 
    page_icon="🐜", 
    layout="centered"
)

# --- CSS & JS 視覺魔法 (賽博龐克 + 互動引擎) ---
st.markdown("""
    <script>
        function speak(text) {
            // 使用瀏覽器原生 TTS，設置為印尼語 (id-ID) 作為阿美語近似音
            // 這是純前端方案，零延遲
            var msg = new SpeechSynthesisUtterance();
            msg.text = text;
            msg.lang = 'id-ID'; 
            msg.rate = 0.9; // 稍微放慢語速
            window.speechSynthesis.cancel(); // 切斷上一句
            window.speechSynthesis.speak(msg);
        }
    </script>
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
    
    /* Header */
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

    /* --- Tabs 修正 --- */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        color: #FFFFFF !important;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(57, 255, 20, 0.1) !important;
        border: 1px solid #39FF14;
        border-bottom: none;
        color: #39FF14 !important;
        box-shadow: 0 -5px 10px rgba(57, 255, 20, 0.1);
    }

    /* --- 互動式文字 (Interactive Text) --- */
    .interactive-word {
        position: relative;
        display: inline-block;
        border-bottom: 1px dashed #39FF14; /* 下劃線提示可互動 */
        cursor: pointer;
        margin: 0 4px;
        transition: 0.3s;
    }
    
    .interactive-word:hover {
        background-color: rgba(57, 255, 20, 0.2);
        color: #FFF;
        text-shadow: 0 0 5px #39FF14;
    }

    /* Tooltip 本體 */
    .interactive-word .tooltip-text {
        visibility: hidden;
        width: 80px;
        background-color: #000;
        color: #39FF14;
        text-align: center;
        border: 1px solid #39FF14;
        border-radius: 6px;
        padding: 5px 0;
        position: absolute;
        z-index: 1;
        bottom: 125%; /* 顯示在上方 */
        left: 50%;
        margin-left: -40px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 14px;
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.5);
    }

    .interactive-word:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* 箭頭 */
    .interactive-word .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #39FF14 transparent transparent transparent;
    }

    /* 卡片與按鈕樣式保持不變 */
    .word-card {
        background: rgba(20, 30, 20, 0.9);
        border: 1px solid #39FF14;
        border-left: 5px solid #39FF14;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
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
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料庫 ---
# 為了讓 Tooltip 抓到對應中文，這裡建立一個快速查找字典
VOCAB_MAP = {
    "kakonah": "螞蟻",
    "hananay": "所謂的",
    "i": "(語氣詞)",
    "o": "是/主格",
    "tada": "非常",
    "malalokay": "勤勞的",
    "a": "的/連詞",
    "fao": "昆蟲",
    "ano": "當/若",
    "matayal": "工作(主焦)",
    "cangra": "他們",
    "saheto": "全部/都",
    "foloday": "一群的",
    "masadak": "出來",
    "caay": "不",
    "ka": "(否定連接)",
    "pahanhan": "休息",
    "ko": "主格標記",
    "tayal": "工作",
    "nangra": "他們的",
    "ma'araw": "看見",
    "matefaday": "掉下來的",
    "posak": "飯粒",
    "lalan": "路",
    "liliden": "搬運(處置)",
    "kora": "那個",
    "panokay": "帶回家",
    "mafana'": "懂得/會",
    "mapapadang": "互相幫忙",
    "saka": "所以",
    "matatodong": "值得/剛好",
    "minanam": "學習",
    "kita": "我們(包含)",
    "to": "受格標記",
    "lalok": "勤勞(名詞)"
}

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
    {"amis": "Liliden nangra ko matefaday a posak.", "zh": "牠們搬運掉下來的飯粒。", "note": "OF 處置焦點"},
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

# --- 2. 核心功能：互動式文字生成器 ---
def render_interactive_text(text):
    """將純文本轉換為帶有 Tooltip 和 OnClick 事件的 HTML"""
    words = text.split() # 簡單按空格分詞
    html_parts = []
    
    for word in words:
        # 清除標點符號以便查找字典 (例如 "fao." -> "fao")
        clean_word = re.sub(r'[^\w\']', '', word).lower()
        display_word = word
        
        # 查找翻譯，若無則顯示 '...'
        translation = VOCAB_MAP.get(clean_word, "")
        
        if translation:
            # 構建 HTML: 
            # onclick="speak('word')" -> 觸發 JS 發音
            # span class="tooltip-text" -> 懸停顯示中文
            html_chunk = f"""
            <span class="interactive-word" onclick="speak('{clean_word}')">
                {display_word}
                <span class="tooltip-text">{translation}</span>
            </span>
            """
        else:
            # 字典裡沒有的詞，就不加互動效果，或只加發音不加翻譯
            html_chunk = f"""
            <span class="interactive-word" onclick="speak('{clean_word}')">
                {display_word}
            </span>
            """
        html_parts.append(html_chunk)
    
    return " ".join(html_parts)

# 舊的 gTTS 函數 (保留給整句播放)
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

tab1, tab2, tab3, tab4 = st.tabs(["🐜 互動課文", "📖 核心單字", "🧬 句型解析", "⚔️ 實戰測驗"])

with tab1:
    st.markdown("### // 沉浸模式 (Interactive Immersion)")
    st.caption("👆 滑鼠懸停單字可看翻譯，點擊單字可聽發音")
    
    # 處理課文
    interactive_html = render_interactive_text(STORY.replace('\n', ' <br> '))
    
    st.markdown(f"""
    <div style="padding:20px; border-left:4px solid #39FF14; background:rgba(20,20,20,0.5); font-size:20px; line-height:2.0; color:#EEE;">
        {interactive_html}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("查看中文全文翻譯"):
        st.markdown(f"<p style='color:#AAA;'>{STORY_ZH.replace(chr(10), '<br>')}</p>", unsafe_allow_html=True)
    
    if st.button("🔊 播放全課文 (整段)"):
        play_audio(STORY.replace('\n', ' '))

with tab2:
    st.markdown("### // 數據掃描：原子單字")
    for v in VOCABULARY:
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            # 這裡也加上互動效果
            st.markdown(f"""
            <div class="word-card">
                <span class="root-tag">ROOT: {v['root']}</span>
                <div class="amis-text" style="cursor:pointer;" onclick="speak('{v['amis']}')">
                    {v['emoji']} {v['amis']}
                </div>
                <div class="zh-text">{v['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.write("") 
            # 保留原本的按鈕作為備用
            if st.button("🔊", key=f"voc_{v['amis']}"):
                play_audio(v['amis'])

with tab3:
    st.markdown("### // 語法解碼：句型結構")
    for s in SENTENCES:
        # 將例句也轉換為互動式
        interactive_sentence = render_interactive_text(s['amis'])
        
        st.markdown(f"""
        <div class="grammar-box">
            <div style="color:#39FF14; font-size:18px; font-weight:bold; margin-bottom:5px;">
                >> {interactive_sentence}
            </div>
            <div style="color:#FFF; margin-bottom:8px;">{s['zh']}</div>
            <div style="color:#CCC; font-size:13px; border-top:1px dashed #555; padding-top:5px;">
                <span class="grammar-title">ANALYSIS:</span> {s['note']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 這裡也可以讓點擊 ">>" 播放整句
        if st.button("唸句型", key=f"sen_{s['amis'][:5]}"):
            play_audio(s['amis'])

with tab4:
    st.markdown("### // 認知驗證 (Quiz)")
    if 'quiz_pool' not in st.session_state:
        init_quiz()
    
    if st.session_state.step < len(st.session_state.quiz_pool):
        current_q = st.session_state.quiz_pool[st.session_state.step]
        st.markdown(f"#### Q{st.session_state.step + 1}: 請選擇「<span style='color:#39FF14'>{current_q['zh']}</span>」的阿美語", unsafe_allow_html=True)
        
        if 'current_options' not in st.session_state or st.session_state.current_q_ref != current_q['amis']:
            options = [current_q['amis']] + [v['amis'] for v in random.sample(VOCABULARY, 3) if v['amis'] != current_q['amis']]
            options = options[:3] 
            random.shuffle(options)
            st.session_state.current_options = options
            st.session_state.current_q_ref = current_q['amis']
        
        locked_options = st.session_state.current_options
        
        cols = st.columns(3)
        for i, opt in enumerate(locked_options):
            with cols[i]:
                if st.button(opt, key=f"opt_{i}_{st.session_state.step}"):
                    if opt == current_q['amis']:
                        st.success("通過 (Access Granted)")
                        st.session_state.score += 1
                        time.sleep(1)
                    else:
                        st.error(f"錯誤 (Denied) - 正解: {current_q['amis']}")
                        time.sleep(2)
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
st.caption("SYSTEM VER 6.6 | Interactive Text Engine Loaded (JS+CSS)")
