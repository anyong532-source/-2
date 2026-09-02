import random
import time
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🎰 카지노 & 로또 확률 시뮬레이터",
    page_icon="🎰",
    layout="wide"
)

# 2. 커스텀 CSS (카지노 느낌의 테마)
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFD700;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.1rem;
        color: #CCCCCC;
        margin-bottom: 25px;
    }
    .lotto-ball {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        color: white;
        margin: 2px;
    }
    .yellow { background-color: #fbc02d; color: black; }
    .blue { background-color: #1e88e5; }
    .red { background-color: #e53935; }
    .gray { background-color: #8e8e8e; }
    .green { background-color: #43a047; }
</style>
""", unsafe_allow_html=True)

# 3. Session State 초기화
if "balance" not in st.session_state:
    st.session_state.balance = 100_000  # 초기 자본금 $100,000
if "initial_balance" not in st.session_state:
    st.session_state.initial_balance = 100_000
if "total_spent" not in st.session_state:
    st.session_state.total_spent = 0
if "total_won" not in st.session_state:
    st.session_state.total_won = 0

# 4. 타이틀 및 헤더
st.markdown("<div class='main-title'>🎰 CASINO & LOTTO SIMULATOR</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>확률의 매운맛을 시각적으로 체험해보는 시뮬레이션 게임</div>", unsafe_allow_html=True)

# 5. 상단 실시간 자산 현황판
col_asset1, col_asset2, col_asset3, col_asset4 = st.columns(4)

roi = ((st.session_state.balance - st.session_state.initial_balance) / st.session_state.initial_balance) * 100

col_asset1.metric("현재 잔액", f"${st.session_state.balance:,}")
col_asset2.metric("총 투입 금액", f"${st.session_state.total_spent:,}")
col_asset3.metric("총 획득 상금", f"${st.session_state.total_won:,}")
col_asset4.metric("수익률 (ROI)", f"{roi:+.2f}%", delta=f"{roi:+.2f}%")

st.markdown("---")

# 6. 사이드바 (초기화 및 충전)
with st.sidebar:
    st.header("⚙️ 게임 설정 및 관리")
    
    if st.button("🔄 잔액 및 기록 초기화", use_container_width=True):
        st.session_state.balance = 100_000
        st.session_state.initial_balance = 100_000
        st.session_state.total_spent = 0
        st.session_state.total_won = 0
        st.rerun()

    st.markdown("---")
    st.subheader("💳 비상 자금 충전")
    recharge_amount = st.number_input("충전 금액 ($)", min_value=1_000, max_value=1_000_000, value=50_000, step=10_000)
    if st.button("💰 충전하기", use_container_width=True):
        st.session_state.balance += recharge_amount
        st.session_state.initial_balance += recharge_amount
        st.success(f"${recharge_amount:,} 충전 완료!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📌 확률 정보 안내")
    st.caption("- **로또 1등 확률:** 1 / 8,145,060")
    st.caption("- **슬롯머신 잭팟:** 약 0.8%")
    st.caption("- **룰렛 단일 번호:** 1 / 37 (약 2.7%)")

# 7. 로또 공 디자인 생성 함수
def get_ball_class(num):
    if num <= 10: return "yellow"
    elif num <= 20: return "blue"
    elif num <= 30: return "red"
    elif num <= 40: return "gray"
    else: return "green"

def render_lotto_numbers(numbers, bonus=None):
    html = ""
    for n in numbers:
        cls = get_ball_class(n)
        html += f"<span class='lotto-ball {cls}'>{n}</span>"
    if bonus is not None:
        html += " <span style='font-size: 18px; font-weight: bold;'>+</span> "
        cls = get_ball_class(bonus)
        html += f"<span class='lotto-ball {cls}'>{bonus}</span>"
    return html

# 8. 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["🎫 로또 6/45 시뮬레이터", "🎰 3-릴 슬롯머신", "🎡 룰렛 시뮬레이터"])

# ==========================================
# TAB 1: 로또 시뮬레이터
# ==========================================
with tab1:
    st.subheader("🎫 로또 6/45 대량 구매 시뮬레이터")
    st.write("1게임당 **$1**입니다. 대량 구매 시 1등 당첨이 얼마나 어려운지 체감해보세요!")

    col_lotto_ctrl1, col_lotto_ctrl2 = st.columns([1, 2])

    with col_lotto_ctrl1:
        buy_count = st.radio(
            "구매할 로또 매수 선택:",
            [1, 10, 100, 1000, 5000, 10000],
            index=2,
            horizontal=True
        )

        mode = st.radio("번호 선택 방식:", ["자동 번호 구매", "수동 번호 지정"])

        user_numbers = []
        if mode == "수동 번호 지정":
            st.caption("6개 번호를 선택하세요 (중복 불가):")
            user_numbers = st.multiselect("내 로또 번호", list(range(1, 46)), max_selections=6)

        buy_button = st.button("🚀 로또 구매 및 추첨", use_container_width=True)

    with col_lotto_ctrl2:
        if buy_button:
            cost = buy_count * 1
            if st.session_state.balance < cost:
                st.error("잔액이 부족합니다! 사이드바에서 충전해주세요.")
            elif mode == "수동 번호 지정" and len(user_numbers) < 6:
                st.warning("수동 번호 6개를 모두 선택해야 합니다.")
            else:
                # 당첨 번호 추첨 (6개 + 보너스 1개)
                winning_all = random.sample(range(1, 46), 7)
                winning_numbers = sorted(winning_all[:6])
                bonus_number = winning_all[6]

                st.session_state.balance -= cost
                st.session_state.total_spent += cost

                # 당첨 집계 설정
                results = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 0: 0}
                prizes = {1: 2_000_000_000, 2: 50_000_000, 3: 1_500_000, 4: 50_000, 5: 5_000, 0: 0}

                # 대량 대조 시뮬레이션
                for _ in range(buy_count):
                    my_nums = set(user_numbers) if mode == "수동 번호 지정" else set(random.sample(range(1, 46), 6))
                    match_count = len(my_nums.intersection(set(winning_numbers)))
                    
                    if match_count == 6: results[1] += 1
                    elif match_count == 5 and bonus_number in my_nums: results[2] += 1
                    elif match_count == 5: results[3] += 1
                    elif match_count == 4: results[4] += 1
                    elif match_count == 3: results[5] += 1
                    else: results[0] += 1

                total_win = sum(results[rank] * prizes[rank] for rank in results)
                st.session_state.balance += total_win
                st.session_state.total_won += total_win

                # 당첨 결과 화면 출력
                st.markdown("### 🎯 이번 회차 당첨 번호")
                st.markdown(render_lotto_numbers(winning_numbers, bonus_number), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("#### 📊 시뮬레이션 결과")
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.write(f"- 🥇 **1등 (6개 일치):** {results[1]}회 (${results[1]*prizes[1]:,})")
                    st.write(f"- 🥈 **2등 (5개+보너스):** {results[2]}회 (${results[2]*prizes[2]:,})")
                    st.write(f"- 🥉 **3등 (5개 일치):** {results[3]}회 (${results[3]*prizes[3]:,})")
                with res_col2:
                    st.write(f"- 🏅 **4등 (4개 일치):** {results[4]}회 (${results[4]*prizes[4]:,})")
                    st.write(f"- 🏅 **5등 (3개 일치):** {results[5]}회 (${results[5]*prizes[5]:,})")
                    st.write(f"- ❌ **낙첨 (꽝):** {results[0]}회")

                batch_roi = ((total_win - cost) / cost) * 100
                if total_win > cost:
                    st.success(f"🎉 **이득 발생!** 총 ${total_win:,} 획득 (수익률: +{batch_roi:.2f}%)")
                else:
                    st.error(f"💸 **손실 발생!** 총 ${total_win:,} 획득 (수익률: {batch_roi:.2f}%)")

# ==========================================
# TAB 2: 슬롯머신 시뮬레이터
# ==========================================
with tab2:
    st.subheader("🎰 클래식 3-릴 슬롯머신")
    st.write("버튼을 눌러 릴을 돌려보세요! 3개의 기호가 모두 맞으면 대박 잭팟입니다.")

    slot_col1, slot_col2 = st.columns([1, 1])

    symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
    payouts = {"7️⃣": 50, "💎": 20, "🔔": 10, "🍒": 5, "🍋": 3}

    with slot_col1:
        bet_slot = st.number_input("배팅 금액 ($)", min_value=10, max_value=10_000, value=100, step=50, key="slot_bet")
        spin_button = st.button("🎰 SPIN!", use_container_width=True)

        st.markdown("#### 📜 배당표 (3개 일치 시)")
        for sym, mult in payouts.items():
            st.write(f"- {sym} {sym} {sym} : **{mult}배**")
        st.caption("* 2개 기호만 맞을 경우 배팅금의 **1.5배** 지급")

    with slot_col2:
        if spin_button:
            if st.session_state.balance < bet_slot:
                st.error("잔액이 부족합니다!")
            else:
                st.session_state.balance -= bet_slot
                st.session_state.total_spent += bet_slot

                # 릴 회전 연출
                placeholder = st.empty()
                for _ in range(5):
                    temp_res = [random.choice(symbols) for _ in range(3)]
                    placeholder.markdown(f"# [ {' | '.join(temp_res)} ]")
                    time.sleep(0.08)

                # 최종 결과 확정
                final_res = [random.choice(symbols) for _ in range(3)]
                placeholder.markdown(f"# [ {' | '.join(final_res)} ]")

                # 결과 판정
                if final_res[0] == final_res[1] == final_res[2]:
                    win_multiplier = payouts[final_res[0]]
                    win_amt = bet_slot * win_multiplier
                    st.session_state.balance += win_amt
                    st.session_state.total_won += win_amt
                    st.balloons()
                    st.success(f"🎊 **JACKPOT!!** {final_res[0]} 3개 적중! ${win_amt:,} 획득! ({win_multiplier}배)")
                elif final_res[0] == final_res[1] or final_res[1] == final_res[2] or final_res[0] == final_res[2]:
                    win_amt = int(bet_slot * 1.5)
                    st.session_state.balance += win_amt
                    st.session_state.total_won += win_amt
                    st.info(f"✨ 2개 일치! ${win_amt:,} 획득 (1.5배)")
                else:
                    st.error("❌ 아쉽게도 꽝입니다!")

# ==========================================
# TAB 3: 룰렛 시뮬레이터
# ==========================================
with tab3:
    st.subheader("🎡 유러피언 룰렛 (European Roulette)")
    st.write("숫자(0~36) 또는 색상(RED/BLACK)에 배팅해보세요.")

    col_r1, col_r2 = st.columns([1, 1])
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

    with col_r1:
        bet_roulette = st.number_input("배팅 금액 ($)", min_value=10, max_value=50_000, value=100, step=50, key="roulette_bet")
        bet_type = st.radio("배팅 유형 선택:", ["색상 (RED / BLACK) - 2배", "단일 번호 (0~36) - 36배"])

        if bet_type == "색상 (RED / BLACK) - 2배":
            color_choice = st.radio("색상 선택:", ["🔴 RED", "⚫ BLACK"])
        else:
            number_choice = st.number_input("번호 선택 (0~36):", min_value=0, max_value=36, value=7)

        spin_roulette = st.button("🎡 룰렛 돌리기", use_container_width=True)

    with col_r2:
        if spin_roulette:
            if st.session_state.balance < bet_roulette:
                st.error("잔액이 부족합니다!")
            else:
                st.session_state.balance -= bet_roulette
                st.session_state.total_spent += bet_roulette

                # 휠 회전 연출
                r_placeholder = st.empty()
                for _ in range(6):
                    tmp_num = random.randint(0, 36)
                    r_placeholder.markdown(f"### 🎡 룰렛 회전 중... [ {tmp_num} ]")
                    time.sleep(0.1)

                winning_num = random.randint(0, 36)
                win_color = "🟢 GREEN" if winning_num == 0 else ("🔴 RED" if winning_num in red_numbers else "⚫ BLACK")
                r_placeholder.markdown(f"## 🎯 당첨 결과: {winning_num} ({win_color})")

                # 승패 판정
                win = False
                payout_rate = 0

                if bet_type == "색상 (RED / BLACK) - 2배":
                    if (color_choice == "🔴 RED" and win_color == "🔴 RED") or (color_choice == "⚫ BLACK" and win_color == "⚫ BLACK"):
                        win = True
                        payout_rate = 2
                else:
                    if number_choice == winning_num:
                        win = True
                        payout_rate = 36

                if win:
                    win_amount = bet_roulette * payout_rate
                    st.session_state.balance += win_amount
                    st.session_state.total_won += win_amount
                    st.success(f"🎉 **축하합니다!** ${win_amount:,} 획득!")
                else:
                    st.error("❌ 낙첨되었습니다.")
