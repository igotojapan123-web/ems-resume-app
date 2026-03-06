import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title="응급구조사 자기소개서 작성 도우미",
    page_icon="🚑",
    layout="wide"
)

# Anthropic Claude API 설정
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

# API 키 (Streamlit secrets에서 로드)
def get_default_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except:
        return None

# 세션 상태 초기화
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'custom_items' not in st.session_state:
    st.session_state.custom_items = []
if 'item_contents' not in st.session_state:
    st.session_state.item_contents = {}
if 'item_limits' not in st.session_state:
    st.session_state.item_limits = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'draft' not in st.session_state:
    st.session_state.draft = {}
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

# 기본 자소서 항목
DEFAULT_ITEMS = [
    "성장과정",
    "성격의 장단점",
    "지원동기",
    "직무역량",
    "가치관"
]

# 지원처 목록
EMPLOYERS = [
    "소방청 (119구급대)",
    "대학병원 응급실",
    "종합병원 응급실",
    "권역외상센터",
    "응급의료센터",
    "산업체 의무실",
    "이벤트/행사 응급구조",
    "소방학교/교육기관",
    "기타 (직접입력)"
]

def get_ai_response(system_prompt, user_message, api_key):
    """Claude API를 사용하여 응답 생성"""
    if not CLAUDE_AVAILABLE:
        return "Anthropic 라이브러리가 설치되지 않았습니다. `pip install anthropic` 명령어로 설치해주세요."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    except Exception as e:
        return f"API 오류: {str(e)}"


def get_ai_response_with_history(system_prompt, messages, api_key):
    """Claude API를 사용하여 대화 히스토리 포함 응답 생성"""
    if not CLAUDE_AVAILABLE:
        return "Anthropic 라이브러리가 설치되지 않았습니다. `pip install anthropic` 명령어로 설치해주세요."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"API 오류: {str(e)}"

def create_system_prompt(employer, selected_items, item_contents):
    """시스템 프롬프트 생성"""
    return f"""당신은 응급구조사 자기소개서 작성을 돕는 전문 컨설턴트입니다.
10년 이상의 응급의료 분야 채용 경험과 심리학/행동경제학 전문 지식을 보유하고 있습니다.

지원처: {employer}

## 핵심 작성 원칙
1. 사용자가 입력한 사실만 사용 (창작·과장 절대 금지)
2. STAR 기법 적용 (Situation, Task, Action, Result)
3. 지원처 맞춤 역량 연결
4. 항목당 400~600자 (사용자가 글자수 지정 시 해당 글자수 준수)
5. 응급구조사 직무 특성 반영 (신속한 판단력, 체력, 팀워크, 스트레스 관리 등)

## 심리학/행동경제학 기반 설득 전략 (반드시 적용)

### 1. 프라이밍 효과 (Priming Effect)
- 첫 문장에서 강렬한 인상을 심어 면접관의 인식 프레임 설정
- 응급 상황 대응, 생명 구조 등 임팩트 있는 키워드로 시작
- 예: "심정지 환자의 4분, 그 골든타임이 제 직업관을 바꿨습니다"

### 2. 손실 회피 (Loss Aversion)
- "이 지원자를 채용하지 않으면 놓치게 될 것"을 암시
- 희소한 경험, 독특한 역량 강조
- 예: "현장 실습 300시간 중 직접 CPR을 수행한 3건의 경험"

### 3. 사회적 증거 (Social Proof)
- 타인의 인정, 수상, 팀원 평가 등 제3자 검증 활용
- 예: "실습 지도교수님이 '침착함이 인상적'이라고 평가해주셨습니다"

### 4. 구체성 효과 (Specificity Effect)
- 추상적 표현 → 구체적 숫자, 날짜, 장소로 변환
- "열심히" → "주 5회, 하루 2시간씩 3개월간"
- "다양한 경험" → "외상센터 100시간, 구급차 동승 50시간"

### 5. 피크-엔드 법칙 (Peak-End Rule)
- 가장 인상적인 순간(피크)과 마무리(엔드)를 강렬하게
- 자소서 마무리에 각오/다짐이 아닌 구체적 비전 제시

### 6. 넛지 (Nudge) 기법
- 면접관이 "이 사람을 더 알고 싶다"는 방향으로 유도
- 호기심을 자극하는 열린 결말, 후속 질문을 유발하는 장치

### 7. 스토리텔링 구조 (Hero's Journey)
- 평범한 일상 → 도전/위기 → 성장/깨달음 → 새로운 나
- 감정선을 따라가며 몰입감 극대화

## 응급구조사 핵심 역량 키워드
- 신속한 상황 판단력, 골든타임 인식
- 체력과 정신력, 스트레스 내성
- 팀워크와 명확한 커뮤니케이션
- 생명 존중, 윤리의식
- 지속적 학습 의지 (프로토콜 업데이트 등)

선택된 항목: {', '.join(selected_items)}

사용자 입력 내용:
{chr(10).join([f"- {item}: {content}" for item, content in item_contents.items() if content])}
"""

def analyze_and_question(employer, selected_items, item_contents, item_limits, api_key):
    """입력 내용 분석 및 추가 질문 생성"""
    system_prompt = create_system_prompt(employer, selected_items, item_contents)

    limits_info = ""
    if item_limits:
        limits_info = "\n글자수 제한: " + ", ".join([f"{k}: {v}자" for k, v in item_limits.items() if v])

    user_message = f"""입력된 내용을 분석하고, 더 좋은 자기소개서를 작성하기 위해 부족한 정보를 파악해주세요.
{limits_info}

다음 형식으로 응답해주세요:
1. "입력하신 내용을 분석했습니다." 로 시작
2. 각 항목별로 현재 입력된 내용의 강점 간단히 언급
3. STAR 구조에서 빠진 요소, 구체적 수치/기관명 부재, 지원처 연결성 등을 고려하여 2~3개의 추가 질문 제시
4. 질문은 번호를 붙여서 명확하게 제시"""

    return get_ai_response(system_prompt, user_message, api_key)

def generate_draft(employer, selected_items, item_contents, item_limits, chat_history, api_key):
    """초안 생성"""
    system_prompt = create_system_prompt(employer, selected_items, item_contents)

    limits_info = ""
    if item_limits:
        limits_info = "\n글자수 제한: " + ", ".join([f"{k}: {v}자" for k, v in item_limits.items() if v])

    # 대화 내역을 포함한 컨텍스트 구성
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    user_message = f"""이전 대화 내용:
{context}
{limits_info}

위 정보를 바탕으로 각 항목별 자기소개서 초안을 작성해주세요.

작성 기준:
- 입력된 사실만 사용 (창작·과장 절대 금지)
- STAR 기법 적용
- 지원처 맞춤 역량 연결
- 항목당 400~600자 (글자수 제한이 있는 경우 해당 글자수 준수)
- 각 항목은 【항목명】으로 구분

초안 작성 후 바로 이어서 첨삭도 제공해주세요:
✅ 잘된 점: (구체적으로)
⚠️ 보완할 점: (항목별 구체적으로)
💡 추가 제안: (더 넣으면 좋을 내용)
📊 종합 점수: XX/100 (직무연결성·구체성·차별성·논리성 각 25점)"""

    return get_ai_response(system_prompt, user_message, api_key)

def continue_conversation(user_input, chat_history, employer, selected_items, item_contents, api_key):
    """대화 계속하기"""
    system_prompt = create_system_prompt(employer, selected_items, item_contents)

    # Claude API 형식에 맞게 메시지 구성
    messages = []
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    return get_ai_response_with_history(system_prompt, messages, api_key)

# 메인 UI
st.title("🚑 응급구조사 자기소개서 작성 도우미")
st.markdown("---")

# 사이드바: API 키 입력
with st.sidebar:
    st.header("⚙️ 설정")

    # 기본 API 키 확인
    default_key = get_default_api_key()

    if default_key:
        use_default_key = st.checkbox("기본 API 키 사용", value=True, help="체크 해제 시 직접 API 키를 입력할 수 있습니다")
        if use_default_key:
            api_key = default_key
            st.success("기본 API 키 사용 중")
        else:
            api_key = st.text_input("Claude API Key", type="password", help="Claude 사용을 위한 Anthropic API 키를 입력하세요")
    else:
        api_key = st.text_input("Claude API Key", type="password", help="Claude 사용을 위한 Anthropic API 키를 입력하세요")

    st.markdown("---")
    st.header("📋 진행 단계")
    steps = ["1️⃣ 정보 입력", "2️⃣ AI 분석 & 초안", "3️⃣ 첨삭 & 수정"]
    for i, step_name in enumerate(steps, 1):
        if st.session_state.step == i:
            st.markdown(f"**→ {step_name}**")
        else:
            st.markdown(f"&nbsp;&nbsp;&nbsp;{step_name}")

    st.markdown("---")
    if st.button("🔄 처음부터 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# STEP 1: 정보 입력
if st.session_state.step == 1:
    st.header("📝 STEP 1: 정보 입력")

    # 지원처 선택
    col1, col2 = st.columns([2, 1])
    with col1:
        employer = st.selectbox("🏥 지원처 선택", EMPLOYERS)
    with col2:
        if employer == "기타 (직접입력)":
            custom_employer = st.text_input("지원처 직접 입력")
            employer = custom_employer if custom_employer else employer

    st.session_state.employer = employer

    st.markdown("---")
    st.subheader("📋 자소서 항목 선택")

    # 탭으로 기본 항목 / 커스텀 항목 구분
    tab1, tab2 = st.tabs(["기본 항목 선택", "➕ 항목 직접 추가"])

    with tab1:
        st.markdown("*필요한 항목을 체크하세요*")
        selected_default = []
        cols = st.columns(3)
        for i, item in enumerate(DEFAULT_ITEMS):
            with cols[i % 3]:
                if st.checkbox(item, key=f"default_{item}"):
                    selected_default.append(item)

    with tab2:
        st.markdown("*원하는 자소서 질문/항목을 직접 추가하세요*")

        # 새 항목 추가
        col1, col2 = st.columns([3, 1])
        with col1:
            new_item = st.text_input("새 항목 입력", placeholder="예: 본인이 가장 힘들었던 경험과 극복 과정")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ 추가"):
                if new_item and new_item not in st.session_state.custom_items:
                    if len(st.session_state.custom_items) < 10:
                        st.session_state.custom_items.append(new_item)
                        st.rerun()
                    else:
                        st.warning("최대 10개까지 추가할 수 있습니다.")

        # 추가된 커스텀 항목 표시
        if st.session_state.custom_items:
            st.markdown("**추가된 항목:**")
            for i, item in enumerate(st.session_state.custom_items):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"• {item}")
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.custom_items.pop(i)
                        st.rerun()

    # 전체 선택된 항목
    all_selected = selected_default + st.session_state.custom_items

    if all_selected:
        st.markdown("---")
        st.subheader("✏️ 항목별 내용 입력")
        st.markdown("*각 항목에 경험, 키워드, 에피소드를 자유롭게 입력하세요 (키워드만 써도 됨)*")

        for item in all_selected:
            with st.expander(f"📌 {item}", expanded=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    content = st.text_area(
                        "내용 입력",
                        key=f"content_{item}",
                        height=120,
                        placeholder="관련 경험, 에피소드, 키워드 등을 입력하세요...",
                        label_visibility="collapsed"
                    )
                    st.session_state.item_contents[item] = content
                with col2:
                    limit = st.number_input(
                        "글자수",
                        min_value=0,
                        max_value=3000,
                        value=0,
                        step=100,
                        key=f"limit_{item}",
                        help="0 = 제한없음"
                    )
                    if limit > 0:
                        st.session_state.item_limits[item] = limit
                    elif item in st.session_state.item_limits:
                        del st.session_state.item_limits[item]

        st.markdown("---")

        # 입력 내용 확인
        has_content = any(st.session_state.item_contents.get(item, "").strip() for item in all_selected)

        if has_content:
            if st.button("🚀 AI 분석 시작", type="primary", use_container_width=True):
                if not api_key:
                    st.error("사이드바에서 OpenAI API Key를 입력해주세요.")
                else:
                    st.session_state.selected_items = all_selected
                    st.session_state.step = 2
                    st.rerun()
        else:
            st.info("최소 하나의 항목에 내용을 입력해주세요.")
    else:
        st.info("자소서 항목을 선택하거나 직접 추가해주세요.")

# STEP 2: AI 분석 & 대화형 초안 생성
elif st.session_state.step == 2:
    st.header("🤖 STEP 2: AI 분석 & 초안 생성")

    # 입력칸 초기화용 카운터 (전송 후 새 key 생성)
    if 'input_key_counter' not in st.session_state:
        st.session_state.input_key_counter = 0

    # 초기 분석 수행
    if not st.session_state.chat_history:
        with st.spinner("입력하신 내용을 분석 중입니다..."):
            analysis = analyze_and_question(
                st.session_state.employer,
                st.session_state.selected_items,
                st.session_state.item_contents,
                st.session_state.item_limits,
                api_key
            )
            st.session_state.chat_history.append({"role": "assistant", "content": analysis})

    # 대화 내역 표시
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f"**🤖 AI:**\n{msg['content']}")
        else:
            st.markdown(f"**👤 나:**\n{msg['content']}")
        st.markdown("---")

    # 사용자 입력 (동적 key로 초기화 구현)
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_area(
            "답변 또는 추가 정보 입력",
            height=100,
            key=f"user_input_{st.session_state.input_key_counter}"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_btn = st.button("📤 전송", use_container_width=True)
        generate_btn = st.button("✨ 초안 생성", type="primary", use_container_width=True)

    if send_btn and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("응답 생성 중..."):
            response = continue_conversation(
                user_input,
                st.session_state.chat_history,
                st.session_state.employer,
                st.session_state.selected_items,
                st.session_state.item_contents,
                api_key
            )
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        # 입력칸 초기화 (key 변경)
        st.session_state.input_key_counter += 1
        st.rerun()

    if generate_btn:
        with st.spinner("초안 및 첨삭 생성 중..."):
            draft_and_feedback = generate_draft(
                st.session_state.employer,
                st.session_state.selected_items,
                st.session_state.item_contents,
                st.session_state.item_limits,
                st.session_state.chat_history,
                api_key
            )
            st.session_state.draft_result = draft_and_feedback
            st.session_state.step = 3
        st.rerun()

# STEP 3: 초안 & 첨삭 결과
elif st.session_state.step == 3:
    st.header("📄 STEP 3: 초안 & 첨삭 결과")

    # 결과 표시
    st.markdown(st.session_state.draft_result)

    st.markdown("---")
    st.subheader("💬 수정 요청")

    # 추가 대화
    if 'step3_chat' not in st.session_state:
        st.session_state.step3_chat = []

    for msg in st.session_state.step3_chat:
        if msg["role"] == "user":
            st.markdown(f"**👤 나:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI:** {msg['content']}")
        st.markdown("---")

    col1, col2 = st.columns([4, 1])
    with col1:
        revision_request = st.text_area(
            "수정 요청사항",
            height=100,
            placeholder="예: 지원동기 부분을 좀 더 열정적으로 수정해주세요 / 성장과정을 600자로 줄여주세요",
            key="revision"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📤 수정 요청", use_container_width=True):
            if revision_request:
                st.session_state.step3_chat.append({"role": "user", "content": revision_request})

                # 전체 컨텍스트 구성
                full_context = st.session_state.chat_history + [
                    {"role": "assistant", "content": st.session_state.draft_result}
                ] + st.session_state.step3_chat

                with st.spinner("수정 중..."):
                    response = continue_conversation(
                        revision_request,
                        full_context[:-1],  # 마지막 user 메시지 제외 (이미 포함됨)
                        st.session_state.employer,
                        st.session_state.selected_items,
                        st.session_state.item_contents,
                        api_key
                    )
                    st.session_state.step3_chat.append({"role": "assistant", "content": response})
                st.rerun()

    # 복사 기능
    st.markdown("---")
    if st.button("📋 전체 결과 복사용 텍스트 보기"):
        full_text = st.session_state.draft_result
        if st.session_state.step3_chat:
            full_text += "\n\n--- 수정 내역 ---\n"
            for msg in st.session_state.step3_chat:
                if msg["role"] == "assistant":
                    full_text += f"\n{msg['content']}\n"
        st.text_area("복사할 텍스트", full_text, height=400)

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "응급구조사 자기소개서 작성 도우미 | Powered by Claude"
    "</div>",
    unsafe_allow_html=True
)
