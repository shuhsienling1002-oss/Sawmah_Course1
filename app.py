import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="O kakonah - 螞蟻", 
    page_icon="🐜", 
    layout="centered"
)

# --- 1. 資料庫 (第 1 課：O kakonah) ---
VOCAB_MAP = {
    "kakonah": "螞蟻", "hananay": "所謂的", "i": "(語氣)", "o": "是/主格",
    "tada": "非常", "malalokay": "勤勞的", "a": "的/連詞", "fao": "昆蟲",
    "ano": "當/若", "matayal": "工作", "cangra": "他們", "saheto": "全部",
    "foloday": "一群的", "masadak": "出來", "caay": "不", "ka": "(否定)",
    "pahanhan": "休息", "ko": "主格", "tayal": "工作", "nangra": "他們的",
    "ma'araw": "看見", "matefaday": "掉下的", "posak": "飯粒", "lalan": "路",
    "liliden": "搬運(被)", "kora": "那個", "panokay": "帶回家", "mafana'": "懂得",
    "mapapadang": "互助", "saka": "所以", "matatodong": "值得", "minanam": "學習",
    "kita": "我們", "to": "受格", "lalok": "勤勞"
}

VOCABULARY = [
    {"amis": "kakonah", "zh": "螞蟻", "emoji": "🐜", "root": "kakonah", "root_zh": "螞蟻"},
    {"amis": "malalokay", "zh": "勤勞的", "emoji": "💪", "root": "lalok", "root_zh": "勤勞"},
    {"amis": "fao", "zh": "昆蟲/蟲", "emoji": "🐛", "root": "fao", "root_zh": "昆蟲"},
    {"amis": "foloday", "zh": "一群的", "emoji": "👥", "root": "folod", "root_zh": "群體"},
    {"amis": "tayal", "zh": "工作", "emoji": "🛠️", "root": "tayal", "root_zh": "工作"},
    {"amis": "posak", "zh": "飯粒", "emoji": "🍚", "root": "posak", "root_zh": "飯粒"},
    {"amis": "liliden", "zh": "搬移(被...)", "emoji": "📦", "root": "lilid", "root_zh": "搬運"},
    {"amis": "matefaday", "zh": "掉下來的", "emoji": "🍂", "root": "tefad", "root_zh": "掉落"},
]

SENTENCES = [
    {"amis": "O tada malalokay a fao ko kakonah.", "zh": "螞蟻是非常勤勞的昆蟲。", "note": "O...ko... 句型"},
    {"amis": "Saheto o foloday a masadak cangra.", "zh": "牠們都是成群結隊地出來。", "note": "Saheto (全部/都)"},
    {"amis": "Liliden nangra ko matefaday a posak.", "zh": "牠們搬運掉下來的飯粒。", "note": "OF 處置焦點 (受事)"}
]

# 課文資料 (7句獨立)
STORY_DATA = [
    {"amis": "O kakonah hananay i, o tada malalokay a fao.", "zh": "所謂的螞蟻，是非常勤勞的昆蟲。"},
    {"amis": "Ano matayal cangra i, saheto o foloday a masadak.", "zh": "當牠們工作時，都是成群結隊地出來。"},
    {"amis": "Caay ka pahanhan ko tayal nangra.", "zh": "牠們的工作從不休息。"},
    {"amis": "Ma'araw nangra ko matefaday a posak i lalan.", "zh": "牠們看見了掉在路上的飯粒。"},
    {"amis": "Liliden nangra kora posak a panokay.", "zh": "牠們便將那飯粒搬運回家。"},
    {"amis": "Mafana' a mapapadang ko kakonah.", "zh": "螞蟻懂得互相幫助。"},
    {"amis": "Saka, matatodong a minanam kita to lalok no kakonah.", "zh": "所以，我們值得學習螞蟻的勤勞。"}
]

# --- 2. 視覺系統 (CSS 注入) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    .stApp { background-color: #0a0e05; color: #ECF0F1; font-family: 'Noto Sans TC', sans-serif; }
    .header-container { background: rgba(0, 20, 0, 0.8); border: 2px solid #39FF14; box-shadow: 0 0 20px rgba(57, 255, 20, 0.3); border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 30px; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #39FF14; font-size: 40px; text-shadow: 0 0 10px #39FF14; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.05); }
    .stTabs [aria-selected="true"] { border: 1px solid #39FF14; color: #39FF14 !important; font-weight: bold; }
    .stButton>button { border: 1px solid #39FF14 !important; background: transparent !important; color: #39FF14 !important; width: 100%; border-radius: 5px; }
    .stButton>button:hover { background: #39FF14 !important; color: #000 !important; }
    
    /* 測驗區樣式 */
    .quiz-card { background: rgba(20, 30, 20, 0.9); border: 1px solid #39FF14; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .quiz-tag { background: #39FF14; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 ---
def get_html_card(item, type="word"):
    # 修正：針對 story_sentence 優化樣式，發音按鈕改為行內圖示
    style_block = """<style>
        body { background-color: transparent; color: #ECF0F1; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: 35px; overflow: hidden; }
        .interactive-word { position: relative; display: inline-block; border-bottom: 1px dashed #39FF14; cursor: pointer; margin: 0 3px; color: #EEE; transition: 0.3s; }
        .interactive-word .tooltip-text { visibility: hidden; min-width: 60px; background-color: #000; color: #39FF14; text-align: center; border: 1px solid #39FF14; border-radius: 6px; padding: 5px; position: absolute; z-index: 100; bottom: 135%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; }
        .interactive-word:hover .tooltip-text { visibility: visible; opacity: 1; }
        
        /* 單字卡樣式 */
        .word-card-static { background: rgba(20, 30, 20, 0.9); border: 1px solid #39FF14; border-left: 5px solid #39FF14; padding: 15px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; margin-top: -30px; height: 100px; box-sizing: border-box; }
        .wc-root-tag { font-size: 12px; background: #39FF14; color: #000; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
        .wc-amis { color: #39FF14; font-size: 24px; font-weight: bold; margin: 5px 0; }
        .wc-zh { color: #FFF; font-size: 16px; font-weight: bold; }
        .play-btn { background: transparent; border: 1px solid #39FF14; color: #39FF14; border-radius: 50%; width: 40px; height: 40px; cursor: pointer; font-size: 18px; }
        
        /* 句子發音按鈕 (小喇叭) */
        .sent-play-btn { 
            display: inline-flex; align-items: center; justify-content: center;
            background: rgba(57, 255, 20, 0.1); border: 1px solid #39FF14; color: #39FF14; 
            border-radius: 50%; width: 30px; height: 30px; cursor: pointer; margin-left: 10px; vertical-align: middle;
            transition: 0.3s;
        }
        .sent-play-btn:hover { background: #39FF14; color: #000; transform: scale(1.1); }
        
        /* 句子容器 */
        .sentence-container { font-size: 18px; line-height: 1.8; display: inline-block; }
    </style>
    <script>
        function speak(text) { window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }
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
            <button class="play-btn" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""
        
    elif type == "story_sentence": # 新增類型：課文句子
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
            
        # 結構：句子單詞 + 發音按鈕 (放在後面)
        full_text_js = s['amis'].replace("'", "\\'")
        body = f"""
        <div class="sentence-container">
            {' '.join(parts)}
            <button class="sent-play-btn" onclick="speak('{full_text_js}')" title="播放整句">🔊</button>
        </div>
        """

    elif type == "sentence": # 句型解析用的 (保留按鈕在下方)
        s = item
        parts = [f'<span class="interactive-word" onclick="speak(\'{re.sub(r"[^\\w\']", "", w).lower().replace("\'", "\\\'")}\')">{w}<span class="tooltip-text">{VOCAB_MAP.get(re.sub(r"[^\\w\']", "", w).lower(), "")}</span></span>' for w in s['amis'].split()]
        body = f'<div style="font-size: 18px; line-height: 1.6;">{" ".join(parts)}</div><button style="margin-top:15px; background:rgba(57,255,20,0.1); border:1px solid #39FF14; color:#39FF14; padding:8px 15px; border-radius:5px; cursor:pointer;" onclick="speak(`{s["amis"].replace("\'", "\\\'")}`)">▶ 播放完整句子</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 (Quiz Engine) ---
def generate_quiz():
    questions = []
    
    # Type 1: 聽力
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({
        "type": "listen",
        "tag": "🎧 聽音辨義",
        "text": "請聽語音，選擇正確的單字",
        "audio": q1['amis'],
        "correct": q1['amis'],
        "options": q1_opts
    })
    
    # Type 2: 翻譯
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({
        "type": "trans",
        "tag": "🧩 詞義連結",
        "text": f"請選擇「<span style='color:#39FF14'>{q2['zh']}</span>」的阿美語",
        "correct": q2['amis'],
        "options": q2_opts
    })
    
    # Type 3: 詞根
    root_candidates = [v for v in VOCABULARY if v['root'] != v['amis']]
    if not root_candidates: root_candidates = VOCABULARY
    q3 = random.choice(root_candidates)
    
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q3['root']]))
    if len(other_roots) < 2: other_roots = ["fake1", "fake2"]
    q3_opts = [q3['root']] + random.sample(other_roots, 2)
    random.shuffle(q3_opts)
    
    questions.append({
        "type": "root",
        "tag": "🧬 詞根偵探",
        "text": f"單字 <span style='color:#39FF14'>{q3['amis']}</span> ({q3['zh']}) 的 <span style='color:#FF00FF'>詞根 (Root)</span> 是？",
        "correct": q3['root'],
        "options": q3_opts,
        "note": f"詞根意思：{q3['root_zh']}"
    })
    
    # Type 4: 句型克漏字
    q4 = random.choice(SENTENCES)
    valid_words = [w for w in q4['amis'].split() if re.sub(r"[^\w']", "", w).lower() in [v['amis'] for v in VOCABULARY]]
    if valid_words:
        target_w = random.choice(valid_words)
        clean_target = re.sub(r"[^\w']", "", target_w).lower()
        q_str = q4['amis'].replace(target_w, "_______")
        
        q4_opts = [clean_target] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x['amis'] != clean_target], 2)]
        random.shuffle(q4_opts)
        
        questions.append({
            "type": "cloze",
            "tag": "🕳️ 句型克漏字",
            "text": f"請填空：<br><span style='color:#FFF; font-size:18px;'>{q_str}</span><br><span style='color:#BBB; font-size:14px;'>{q4['zh']}</span>",
            "correct": clean_target,
            "options": q4_opts
        })
    else:
        questions.append({
            "type": "listen_sent",
            "tag": "🔊 語感聽解",
            "text": "請聽句子，選擇正確的中文",
            "audio": q4['amis'],
            "correct": q4['zh'],
            "options": [q4['zh']] + [s['zh'] for s in random.sample([x for x in SENTENCES if x != q4], 2)]
        })

    random.shuffle(questions)
    return questions[:5] 

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except:
        pass

# --- 5. UI 呈現層 ---
st.markdown("""<div class="header-container"><h1 class="main-title">O KAKONAH</h1><div style="color: #39FF14; letter-spacing: 5px;">第 1 課：螞蟻</div><div style="font-size: 12px; margin-top:10px; color:#888;">講師：高生榮 | 教材：高生榮</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🐜 互動課文", "📖 核心單字", "🧬 句型解析", "⚔️ 實戰測驗"])

with tab1:
    st.markdown("### // 沉浸模式 (Interactive Immersion)")
    st.caption("👆 每一句都是獨立卡片，點擊單字查義，點擊右側🔊聽整句")
    
    # 這裡將 STORY_DATA 中的每一句獨立渲染
    for i, item in enumerate(STORY_DATA):
        st.markdown(f"""
        <div style="background:rgba(20,20,20,0.5); padding:10px; border-left:4px solid #39FF14; margin-bottom:15px; border-radius:5px;">
        """, unsafe_allow_html=True)
        
        # 1. 阿美語句子 + 發音按鈕 (在 iframe 內)
        # 使用新定義的 'story_sentence' 類型
        components.html(get_html_card(item, type="story_sentence"), height=80) # 高度設為80足夠單行顯示
        
        # 2. 中文翻譯 (在 iframe 外，Markdown 渲染)
        st.markdown(f"""
            <div style="color:#BBB; padding-left:8px; font-size:16px; border-top:1px solid #333; padding-top:5px; margin-top:-10px;">
                {item['zh']}
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 數據掃描：原子單字")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=140)

with tab3:
    st.markdown("### // 語法解碼：句型結構")
    for s in SENTENCES:
        st.markdown("""<div style="background:rgba(57,255,20,0.05); padding:15px; border:1px dashed #39FF14; border-radius: 5px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=140)
        st.markdown(f"""<div style="color:#FFF; margin-bottom:8px;">{s['zh']}</div><div style="color:#CCC; font-size:13px; border-top:1px dashed #555; padding-top:5px;"><span style="color:#39FF14; font-family:Orbitron;">NOTE:</span> {s.get('note', '')}</div></div>""", unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0
        st.session_state.quiz_score = 0

    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        
        st.markdown(f"""
        <div class="quiz-card">
            <div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#888;">Q{st.session_state.quiz_step + 1}</span></div>
            <div style="font-size:18px; color:#FFF; margin-bottom:10px;">{q['text']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if 'audio' in q:
            play_audio(q['audio'])

        opts = q['options']
        
        cols = st.columns(3)
        for i, opt in enumerate(opts):
            col_idx = i % 3
            with cols[col_idx]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower() or opt == q['correct']:
                        st.success("通過 (Access Granted)")
                        st.session_state.quiz_score += 1
                        time.sleep(1)
                    else:
                        st.error(f"錯誤 - 正解: {q['correct']}")
                        if 'note' in q: st.info(q['note'])
                        time.sleep(2.5)
                    
                    st.session_state.quiz_step += 1
                    st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:2px solid #39FF14; background:rgba(57,255,20,0.1);"><h2 style="color:#39FF14">MISSION COMPLETE</h2><p>最終得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("重新啟動系統 (Reboot)"):
            del st.session_state.quiz_questions
            st.rerun()

st.markdown("---")
st.caption("SYSTEM VER 7.7 | Layout Optimized: 7-Sentence Atomic Structure")
