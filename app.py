import streamlit as st
import plotly.express as px
from pathlib import Path
from data import QUESTIONS, TYPE_DATA, TYPE_ORDER

# -------------------------------------
# Page setup
# -------------------------------------
st.set_page_config(
    page_title="サッカータイプ診断",
    page_icon="⚽",
    layout="centered",
)

ROOT = Path(__file__).parent
QUESTION_IMAGE_DIR = ROOT / "assets" / "questions"
TYPE_IMAGE_DIR = ROOT / "assets" / "types"

TYPE_EMOJI = {
    "A": "🔥",  # striker
    "B": "🧠",  # playmaker
    "C": "🌀",  # dribbler
    "D": "🤝",  # volante
    "E": "🛡️",  # defender
    "F": "🧤",  # goalkeeper
}

TYPE_IMAGE = {
    "A": "A_striker.jpg",
    "B": "B_playmaker.jpg",
    "C": "C_dribbler.jpg",
    "D": "D_volante.jpg",
    "E": "E_defender.jpg",
    "F": "F_goalkeeper.jpg",
}

# -------------------------------------
# Session state
# -------------------------------------
defaults = {
    "started": False,
    "finished": False,
    "nickname": "",
    "current_question": 0,
    "answers": {},
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------------
# CSS
# -------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700;900&display=swap');

:root {
    --orange: #f07824;
    --orange-dark: #d85f12;
    --cream: #fff7eb;
    --ink: #34271f;
    --muted: #806d5c;
    --line: #f3d6b8;
}
.stApp {
    background:
      radial-gradient(circle at 8% 8%, rgba(255,190,105,.18) 0 2px, transparent 3px),
      radial-gradient(circle at 92% 24%, rgba(240,120,36,.12) 0 3px, transparent 4px),
      linear-gradient(145deg, #fffaf2 0%, #fff1df 55%, #fff8ef 100%);
    color: var(--ink);
    font-family: 'Zen Maru Gothic', sans-serif;
}
.main .block-container {
    max-width: 820px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label, [data-testid="stMarkdownContainer"] {
    font-family: 'Zen Maru Gothic', sans-serif;
}
h1, h2, h3 { color: var(--orange-dark); letter-spacing: .02em; }
p, label { color: var(--ink); }
[data-testid="stCaptionContainer"] { color: var(--muted); }
div.stButton > button {
    background: linear-gradient(135deg, #ff9b3f, #ed6b1c);
    color: white;
    border: 0;
    border-radius: 16px;
    min-height: 3.1rem;
    font-weight: 900;
    box-shadow: 0 5px 0 #c95712, 0 10px 22px rgba(190,92,22,.14);
    transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}
div.stButton > button:hover {
    color: white;
    filter: brightness(1.04);
    transform: translateY(-3px);
    box-shadow: 0 8px 0 #c95712, 0 14px 24px rgba(190,92,22,.18);
}
div.stButton > button:active {
    transform: translateY(2px);
    box-shadow: 0 2px 0 #c95712;
}
div[data-testid="stTextInput"] input {
    border: 2px solid #f2c99f;
    border-radius: 14px;
    background: #fffdf9;
}
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #ffb04f, #e96b1c);
    border-radius: 99px;
}
div[data-testid="stProgressBar"] > div {
    background: #f8dfc4;
    border-radius: 99px;
    height: .7rem;
}
.question-shell {
    background: rgba(255,255,255,.88);
    border: 2px solid #f4d2ae;
    border-radius: 26px;
    padding: 1.15rem 1.25rem;
    margin: .8rem 0 1rem;
    box-shadow: 0 12px 30px rgba(119,70,28,.08);
    animation: questionEnter .48s cubic-bezier(.2,.8,.2,1) both;
}
@keyframes questionEnter {
    from { opacity: 0; transform: translateY(18px) translateX(8px) scale(.985); }
    to   { opacity: 1; transform: translateY(0) translateX(0) scale(1); }
}
.eyebrow {
    color: #b8662b;
    font-size: .78rem;
    font-weight: 900;
    letter-spacing: .13em;
    margin-bottom: .35rem;
}
.question-title {
    color: #3a2a20;
    font-size: clamp(1.2rem, 3vw, 1.75rem);
    font-weight: 900;
    line-height: 1.55;
    margin: .25rem 0 .75rem;
}
.question-note {
    color: #8a725e;
    font-size: .86rem;
    font-weight: 700;
}
.result-shell {
    background: linear-gradient(145deg, #fff 0%, #fff4e5 100%);
    border: 2px solid #f1bd86;
    border-radius: 28px;
    padding: 1.3rem;
    text-align: center;
    box-shadow: 0 14px 34px rgba(119,70,28,.10);
    animation: resultPop .65s cubic-bezier(.16,1,.3,1) both;
}
@keyframes resultPop {
    from { opacity: 0; transform: translateY(24px) scale(.94); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
.result-kicker {
    color: #b96b2f;
    font-weight: 900;
    letter-spacing: .15em;
    font-size: .78rem;
}
.result-name {
    color: #e46d1d;
    font-weight: 900;
    font-size: clamp(1.6rem, 4vw, 2.2rem);
    margin: .2rem 0;
}
.info-card {
    background: rgba(255,255,255,.86);
    border: 1px solid #f2d8bd;
    border-radius: 18px;
    padding: .9rem 1rem;
    margin: .55rem 0;
}
.stRadio [role="radiogroup"] {
    gap: .55rem;
}
.stRadio [role="radiogroup"] > label {
    background: rgba(255,255,255,.88);
    border: 1.5px solid #f0d5b9;
    border-radius: 15px;
    padding: .72rem .85rem;
    transition: transform .16s ease, border-color .16s ease, background .16s ease, box-shadow .16s ease;
}
.stRadio [role="radiogroup"] > label:hover {
    border-color: #f39a4c;
    background: #fff8ef;
    transform: translateX(4px);
    box-shadow: 0 5px 14px rgba(150,88,35,.08);
}
.stRadio [role="radiogroup"] > label:has(input:checked) {
    border: 2px solid #ef812c;
    background: #fff0dd;
    box-shadow: 0 4px 14px rgba(220,112,33,.12);
}
div[data-testid="stExpander"] {
    border: 1px solid #f0d5b9;
    border-radius: 16px;
    background: rgba(255,255,255,.7);
}
hr { border-color: #f1d9c0; }
@media (max-width: 600px) {
    .main .block-container { padding-left: 1rem; padding-right: 1rem; }
    .question-shell { padding: .9rem; border-radius: 20px; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------
# Header
# -------------------------------------
st.markdown("""
<div style="text-align:center; padding:.2rem 0 .6rem;">
  <div style="font-size:2.2rem;">⚽ ✏️ 🟠</div>
  <div style="font-size:clamp(1.65rem,5vw,2.35rem);font-weight:900;color:#df681c;letter-spacing:.04em;">
    サッカータイプ診断
  </div>
  <div style="font-size:.9rem;color:#8a725e;font-weight:700;">
    あなたの性格、ピッチに出てます。
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------
# Start screen
# -------------------------------------
if not st.session_state.started:
    st.markdown("""
    <div class="question-shell">
      <div class="eyebrow">WELCOME TO THE PITCH</div>
      <div class="question-title">あなたはどのポジションタイプ？</div>
      <div class="question-note">15問でわかる、あなたのサッカー性格。</div>
    </div>
    """, unsafe_allow_html=True)

    cover = QUESTION_IMAGE_DIR / "q01.jpg"
    if cover.exists():
        st.image(str(cover), use_container_width=True)

    st.markdown('<div class="info-card">サッカー経験がなくても大丈夫！直感で選んでね。正解・不正解はありません。</div>', unsafe_allow_html=True)
    nickname = st.text_input("ニックネーム", placeholder="例：週末だけエース")
    if st.button("キックオフ！ 診断スタート", use_container_width=True):
        if not nickname.strip():
            st.warning("ニックネームを入力してね！")
        else:
            st.session_state.nickname = nickname.strip()
            st.session_state.started = True
            st.session_state.finished = False
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.rerun()

# -------------------------------------
# Questions
# -------------------------------------
elif not st.session_state.finished:
    q_index = st.session_state.current_question
    question = QUESTIONS[q_index]
    total = len(QUESTIONS)

    st.progress((q_index + 1) / total, text=f"QUESTION {q_index + 1:02d} / {total:02d}")

    st.markdown(f"""
    <div class="question-shell">
      <div class="eyebrow">MATCH DAY PERSONALITY TEST　・　Q{q_index + 1:02d}</div>
      <div class="question-title">{question["question"]}</div>
      <div class="question-note">深く考えすぎず、いちばん自分っぽいものを選ぼう。</div>
    </div>
    """, unsafe_allow_html=True)

    q_img = QUESTION_IMAGE_DIR / f"q{q_index + 1:02d}.jpg"
    if q_img.exists():
        st.image(str(q_img), use_container_width=True)

    options = question["options"]
    st.markdown("#### あなたならどうする？")

    # 回答カードはイラストなしで、テキストと選択ボタンのみ表示
    option_cols = st.columns(2)

    for i, option in enumerate(options):
        with option_cols[i % 2]:
            st.markdown(
                f"""
                <div style="
                    background:rgba(255,255,255,.88);
                    border:2px solid #f0d5b9;
                    border-radius:16px;padding:.65rem .7rem .45rem;
                    min-height:7.3rem;margin-bottom:.25rem;
                ">
                  <div style="font-size:.72rem;font-weight:900;color:#b96b2f;">
                    OPTION {i + 1:02d} 
                  </div>
                  <div style="font-size:.94rem;font-weight:700;color:#3a2a20;line-height:1.55;">
                    {option['text']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            if st.button("この回答にする", key=f"pick_{q_index}_{i}", use_container_width=True):
                st.session_state.answers[q_index] = i

                if q_index == total - 1:
                    st.session_state.finished = True
                else:
                    st.session_state.current_question += 1

                st.rerun()

    
    if q_index > 0:
        if st.button(
            "← 前の質問",
            use_container_width=True,
            key=f"back_question_{q_index}"
        ):
            st.session_state.current_question -= 1
            st.rerun()

# -------------------------------------
# Results
# -------------------------------------
else:
    scores = {type_id: 0 for type_id in TYPE_ORDER}
    for q_index, selected_index in st.session_state.answers.items():
        option = QUESTIONS[q_index]["options"][selected_index]
        main_type = option["main"]
        sub_type = option["sub"]
        if main_type is not None:
            scores[main_type] += 2
        if sub_type is not None:
            scores[sub_type] += 1

    st.balloons()
    st.markdown(f"""
    <div class="result-shell">
      <div class="result-kicker">YOUR PERSONALITY RESULT</div>
      <div style="font-size:1rem;color:#806d5c;font-weight:700;">{st.session_state.nickname} さんの診断結果</div>
    </div>
    """, unsafe_allow_html=True)

    max_score = max(scores.values())
    if max_score == 0:
        st.warning("今回はタイプを判定できなかったみたい！もう一度やってみよう！")
    else:
        winners = [type_id for type_id, score in scores.items() if score == max_score]
        if len(winners) == 1:
            winner = winners[0]
            result = TYPE_DATA[winner]
            result_img = TYPE_IMAGE_DIR / TYPE_IMAGE[winner]

            st.markdown(f"""
            <div class="result-shell">
              <div class="result-kicker">{result["position"]}　・　YOUR SOCCER PERSONALITY</div>
              <div class="result-name">{result["name"]}</div>
              <div style="font-size:1.1rem;font-weight:900;color:#6e4a32;">「{result["nickname"]}」</div>
              <div style="color:#6f5c4b;line-height:1.8;margin-top:.65rem;">{result["description"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if result_img.exists():
                st.image(str(result_img), use_container_width=True)

            st.markdown('<div class="info-card"><b>✨ あなたの強み</b></div>', unsafe_allow_html=True)
            for item in result["strengths"]:
                st.markdown(f"- {item}")
            st.markdown('<div class="info-card"><b>🌀 ちょっとした弱点</b></div>', unsafe_allow_html=True)
            for item in result["weaknesses"]:
                st.markdown(f"- {item}")

            compatible_id = result["compatible"]
            compatible = TYPE_DATA[compatible_id]
            st.markdown(f'<div class="info-card"><b>🤝 相性のいいタイプ</b><br>{compatible["name"]}（{compatible["position"]}）</div>', unsafe_allow_html=True)
            compatible_img = TYPE_IMAGE_DIR / TYPE_IMAGE[compatible_id]
            if compatible_img.exists():
                st.image(str(compatible_img), use_container_width=True)

            st.markdown('<div class="info-card"><b>😂 あなたへの偏見・あるある</b></div>', unsafe_allow_html=True)
            st.info(result["bias"])
        else:
            st.markdown('<div class="result-shell"><div class="result-name">今回は接戦！！</div><div>あなたには複数タイプの特徴があるみたい。</div></div>', unsafe_allow_html=True)
            for type_id in winners:
                tied = TYPE_DATA[type_id]
                st.markdown(f"### {TYPE_EMOJI[type_id]} {tied['name']}")
                img = TYPE_IMAGE_DIR / TYPE_IMAGE[type_id]
                if img.exists():
                    st.image(str(img), use_container_width=True)

    st.divider()
    st.subheader("📊 6タイプの得点バランス")
    chart_data = {
        "タイプ": [TYPE_DATA[t]["name"] for t in TYPE_ORDER],
        "得点": [scores[t] for t in TYPE_ORDER],
    }
    if sum(scores.values()) > 0:
        fig = px.pie(chart_data, names="タイプ", values="得点", hole=0.48)
        fig.update_traces(textposition="inside", textinfo="label+percent")
        fig.update_layout(
            margin=dict(t=15, b=15, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Zen Maru Gothic", color="#4b382a"),
            legend=dict(orientation="h", y=-0.12),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("今回は得点がありませんでした。")

    with st.expander("各タイプの得点を見る"):
        for type_id in TYPE_ORDER:
            st.write(f"{TYPE_EMOJI[type_id]} {TYPE_DATA[type_id]['name']}：{scores[type_id]}点")

    st.divider()
    if st.button("↻ もう一度診断する", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("answer_"):
                del st.session_state[key]
        st.session_state.started = False
        st.session_state.finished = False
        st.session_state.current_question = 0
        st.session_state.answers = {}
        st.session_state.nickname = ""
        st.rerun()
