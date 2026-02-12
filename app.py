import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 (System Configuration) ---
st.set_page_config(
    page_title="O kakonah - 螞蟻之歌", 
    page_icon="🐜", 
    layout="centered"
)

# --- 1. 資料庫 (第 1 課：O kakonah) ---
# [架構師筆記] 這裡映射了所有單字及其翻譯，用於 Tooltip 懸浮顯示
VOCAB_MAP = {
    "o": "主格/焦點標記", "mafoloday": "一群的/群聚的", "a": "連綴詞", "kakonah": "螞蟻", 
    "kami": "我們(排除式)", "malalok": "勤勞的", "matayal": "工作", 
    "matefaday": "掉落的", "i": "在/話題標記", "sasera": "地面/地板", 
    "posak": "飯粒", "ato": "和/與", "fao": "蟲子", 
    "liliden": "搬運(被動)", "niyam": "我們(屬格)", "panokay": "帶回家",
    "malalokay": "勤勞的(名詞化)"
}

# [架構師筆記] 核心單字卡，包含詞根 (Root) 邏輯，符合 EdTech-CRF 規範
VOCABULARY = [
    {"amis": "kakonah", "zh": "螞蟻", "emoji": "🐜", "root": "kakonah", "root_zh": "螞蟻"},
    {"amis": "mafoloday", "zh": "一群的/群聚", "emoji": "👯‍♂️", "root": "folod", "root_zh": "群/堆"},
    {"amis": "malalok", "zh": "勤勞", "emoji": "💪", "root": "lalok", "root_zh": "勤勞"},
    {"amis": "matayal", "zh": "工作", "emoji": "🛠️", "root": "tayal", "root_zh": "工作"},
    {"amis": "matefaday", "zh": "掉落的", "emoji": "📉", "root": "tefad", "root_zh": "掉落"},
    {"amis": "sasera", "zh": "地面", "emoji": "🟫", "root": "sera", "root_zh": "土/地"},
    {"amis": "posak", "zh": "飯粒", "emoji": "🍚", "root": "posak", "root_zh": "散落的穀粒"},
    {"amis": "fao", "zh": "蟲子", "emoji": "🐛", "root": "fao", "root_zh": "蟲"},
    {"amis": "liliden", "zh": "搬運/拖", "emoji": "🏋️", "root": "lilid", "root_zh": "拖/帶"},
    {"amis": "panokay", "zh": "帶回/送回", "emoji": "🏠", "root": "nokay", "root_zh": "回"},
]

# [架構師筆記] 句型分析，內嵌 HTML 格式的語法筆記
SENTENCES = [
    {
        "amis": "O mafoloday a kakonah kami.", 
        "zh": "我們是一群螞蟻。", 
        "note": """
        <br><b>O ... kami</b>：名詞句結構「我們是...」。
        <br><b>mafoloday</b>：詞根 <i>folod</i> (群) + <i>ma-</i> (狀態) + <i>-ay</i> (名詞化)。
        <br><b>kakonah</b>：核心名詞「螞蟻」。
        <br><b>kami</b>：主格代名詞「我們」(排除式，不包含聽話者)。"""
    },
    {
        "amis": "Malalok matayal kami.", 
        "zh": "我們勤勞地工作。", 
        "note": """
        <br><b>Malalok</b>：動詞「勤勞」，在此作副詞修飾後面的動作。
        <br><b>matayal</b>：動詞「工作」。
        <br><b>連動結構</b>：兩個動詞連用，表示「勤勞地做工作」。"""
    },
    {
        "amis": "O matefaday i sasera a posak ato fao i.", 
        "zh": "那些掉在地面上的飯粒和蟲子...", 
        "note": """
        <br><b>matefaday</b>：掉下來的東西 (名詞化動詞)。
        <br><b>i sasera</b>：在地面 (方位介系詞片語)。
        <br><b>posak ato fao</b>：飯粒和蟲子。
        <br><b>句尾 i</b>：話題標記 (Topic Marker)，表示「關於這些東西...」，句子未完，引起注意。"""
    },
    {
        "amis": "Liliden niyam a panokay.", 
        "zh": "我們都把它們搬回家。", 
        "note": """
        <br><b>Liliden</b>：被搬運 (PF 受事焦點)。詞根 <i>lilid</i> + <i>-en</i>。
        <br><b>niyam</b>：我們 (屬格)。因為動詞是被動態，執行者用屬格。
        <br><b>panokay</b>：使...回家 (使動 <i>pa-</i> + <i>nokay</i>)。
        <br><b>邏輯</b>：(那些東西) 被我們搬運並帶回家。"""
    },
    {
        "amis": "O malalokay a kakonah kami.", 
        "zh": "我們是勤勞的螞蟻。", 
        "note": """
        <br><b>malalokay</b>：勤勞的 (形容詞名詞化)。
        <br><b>首尾呼應</b>：與第一句結構相同，再次強調身份。"""
    }
]

STORY_DATA = [
    {"amis": "O mafoloday a kakonah kami.", "zh": "我們是一群螞蟻。"},
    {"amis": "Malalok matayal kami.", "zh": "我們勤勞地工作。"},
    {"amis": "O matefaday i sasera a posak ato fao i.", "zh": "掉在地面上的飯粒和蟲子。"},
    {"amis": "Liliden niyam a panokay.", "zh": "我們都把它們搬回家。"},
    {"amis": "O malalokay a kakonah kami.", "zh": "我們是勤勞的螞蟻。"}
]

# --- 2. 視覺系統 (CSS 注入 - Cyberpunk Style) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    .stApp { background-color: #0a0e05; color: #ECF0F1; font-family: 'Noto Sans TC', sans-serif; }
    
    /* 霓虹綠邊框容器 */
    .header-container { 
        background: rgba(0, 20, 0, 0.8); 
        border: 2px solid #39FF14; 
        box-shadow: 0 0 20px rgba(57, 255, 20, 0.3); 
        border-radius: 10px; 
        padding: 20px; 
        text-align: center; 
        margin-bottom: 30px; 
    }
    
    .main-title { font-family: 'Orbitron', sans-serif; color: #39FF14; font-size: 36px; text-shadow: 0 0 10px #39FF14; margin-bottom: 5px; }
    .sub-title { color: #FFF; font-size: 14px; letter-spacing: 2px; opacity: 0.8; }
    
    /* Tab 樣式客製化 */
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.05); }
    .stTabs [aria-selected="true"] { border: 1px solid #39FF14; color: #39FF14 !important; font-weight: bold; }
    
    /* 按鈕樣式 */
    .stButton>button { border: 1px solid #39FF14 !important; background: transparent !important; color: #39FF14 !important; width: 100%; border-radius: 5px; transition: 0.3s; }
    .stButton>button:hover { background: #39FF14 !important; color: #000 !important; box-shadow: 0 0 15px #39FF14; }
    
    /* 測驗卡片 */
    .quiz-card { background: rgba(20, 30, 20, 0.9); border: 1px solid #39FF14; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .quiz-tag { background: #39FF14; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-right: 10px; }
    
    /* 翻譯區塊 */
    .zh-translation-block {
        background: rgba(20, 20, 20, 0.6);
        border-left: 4px solid #AAA;
        padding: 20px;
        margin-top: 0px; 
        border-radius: 5px;
        color: #CCC;
        font-size: 16px;
        line-height: 2.0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 (v9.1 - Optimized) ---
def get_html_card(item, type="word"):
    # 設定：full_amis_block 依然保持 100px padding (防切頭)，下方負邊距拉近
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        body {{ background-color: transparent; color: #ECF0F1; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 1px dashed #39FF14; cursor: pointer; margin: 0 3px; color: #EEE; transition: 0.3s; font-size: 19px; }}
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #000; color: #39FF14; text-align: center; border: 1px solid #39FF14; border-radius: 6px; padding: 5px; position: absolute; z-index: 100; bottom: 135%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; box-shadow: 0 0 10px rgba(57,255,20,0.2); }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        .play-btn-inline {{ background: rgba(57, 255, 20, 0.1); border: 1px solid #39FF14; color: #39FF14; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #39FF14; color: #000; transform: scale(1.1); }}
        
        /* 單字卡樣式 */
        .word-card-static {{ background: rgba(20, 30, 20, 0.9); border: 1px solid #39FF14; border-left: 5px solid #39FF14; padding: 15px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; }}
        .wc-root-tag {{ font-size: 12px; background: #39FF14; color: #000; padding: 2px 6px; border-radius: 3px; font-weight: bold; margin-right: 5px; }}
        .wc-amis {{ color: #39FF14; font-size: 24px; font-weight: bold; margin: 5px 0; }}
        .wc-zh {{ color: #FFF; font-size: 16px; font-weight: bold; }}
        .play-btn-large {{ background: transparent; border: 1px solid #39FF14; color: #39FF14; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #39FF14; color: #000; }}
        
        /* 阿美語全文區塊樣式 */
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#BBB;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        # 互動課文區塊
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        # 句型解析區塊
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:rgba(57, 255, 20, 0.1); border:1px solid #39FF14; color:#39FF14; padding:5px 12px; border-radius:4px; cursor:pointer;" onclick="speak(`{full_js}`)">▶ 播放整句</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 (Logic Hardened) ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#39FF14'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#39FF14'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探 (Root Logic)
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["roma", "lalan", "cidal"] # Fallback
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#39FF14'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#39FF14'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字 (Cloze)
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2] # 避免選到太短的干擾項
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#FFF; font-size:18px;'>{q_text}</span><br><span style='color:#BBB; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    # 8. 補一題
    questions.append(random.choice(questions[:4])) 

    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        # 使用印尼語 (id) 近似阿美語發音
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 ---
st.markdown("""
<div class="header-container">
    <h1 class="main-title">O kakonah</h1>
    <div class="sub-title">第 1 課：螞蟻之歌</div>
    <div style="font-size: 12px; margin-top:10px; color:#888;">Code-CRF v6.4 | EdTech Engine Loaded</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🐝 互動課文", "📕 核心單字", "🧬 
