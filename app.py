import streamlit as st
import math
import random

# 页面基本配置
st.set_page_config(page_title="Master Duel 卡组动点与展开助手", layout="wide", initial_sidebar_state="expanded")

st.title("🃏 Master Duel 动点概率与展开路线助手")

tab1, tab2, tab3 = st.tabs(["📊 动点概率计算", "🎲 起手模拟抽牌", "📖 Combo 展开路线"])

# --- TAB 1: 超几何分布动点概率计算 ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ 卡组构成参数")
        deck_size = st.number_input("卡组总张数 (N)", value=40, min_value=40, max_value=60, step=1)
        hand_size = st.radio("先手 / 后手抽牌数 (n)", [5, 6], format_func=lambda x: f"先手 ({x}张)" if x == 5 else f"后手 ({x}张)")
        starters = st.slider("初动点张数 (K1)", 1, 20, 6)
        handtraps = st.slider("手坑/拦截张数 (K2)", 0, 20, 9)
        bricks = st.slider("废件/卡手物 (K3)", 0, 10, 2)

    with col2:
        st.subheader("📈 概率分析结果")
        
        def calc_prob(k, n=hand_size, N=deck_size):
            if k <= 0: return 0.0
            if k > N: return 100.0
            prob_zero = math.comb(N - k, n) / math.comb(N, n)
            return (1 - prob_zero) * 100

        p_starter = calc_prob(starters)
        p_ht = calc_prob(handtraps)
        p_brick_only = (math.comb(bricks, hand_size) / math.comb(deck_size, hand_size) * 100) if bricks >= hand_size else 0.0

        st.metric("起手拿到【至少 1 张动点】概率", f"{p_starter:.2f}%")
        st.metric("起手拿到【至少 1 张手坑】概率", f"{p_ht:.2f}%")
        st.metric("理想起手 (动点 + 手坑同时上手)", f"{(p_starter / 100 * p_ht / 100) * 100:.2f}%")
        
        if bricks > 0:
            st.caption(f"⚠️ 极端卡手（起手全废件）概率: {p_brick_only:.4f}%")

# --- TAB 2: 手牌模拟试抽 ---
with tab2:
    st.subheader("🎲 5 张起手牌模拟抽样")
    if st.button("🎴 点击洗牌并抽取起手", type="primary"):
        # 构建卡组列表
        deck = (["动点"] * starters) + (["手坑"] * handtraps) + (["废件"] * bricks)
        remaining = max(0, deck_size - len(deck))
        deck += ["普通卡"] * remaining
        
        # 随机抽取
        hand = random.sample(deck, hand_size)
        cols = st.columns(hand_size)
        
        for i, card in enumerate(hand):
            if card == "动点":
                color_code, emoji = "🟢", "【初动】"
            elif card == "手坑":
                color_code, emoji = "🔵", "【手坑】"
            elif card == "废件":
                color_code, emoji = "🔴", "【废件】"
            else:
                color_code, emoji = "⚪", "【自由位】"
                
            cols[i].metric(f"卡牌 {i+1}", f"{color_code} {card}", delta=emoji)
            
        st.write("---")
        if "动点" in hand:
            st.success("✅ 手牌通过！具备展开动点。")
        else:
            st.error("❌ 发生事故！手牌无动点，建议妥协或过牌。")

# --- TAB 3: Combo 数据库 ---
with tab3:
    st.subheader("📚 卡组展开与妥协路线图")
    
    COMBO_DATA = {
        "烙印 (Branded)": {
            "单卡: 烙印融合": [
                "1. 发动【烙印融合】送墓【阿不思的落胤】+【深渊之兽 鲁贝利乌斯】融合召唤【神炎龙 鲁贝利乌斯】",
                "2. 发动【神炎龙】效果弃 1 手牌，将墓地【阿不思】与【神炎龙】洗回卡组，融合召唤【冰剑龙 赫界龙】",
                "3. 墓地【深渊之兽 鲁贝利乌斯】解放场上神炎龙特召，发动效果表侧置放卡组【烙印之兽】",
                "4. 结束阶段（End Phase）触发墓地烙印龙效果，盖放【赫之烙印】",
                "5. 终场：冰剑龙(非取对象除外) + 烙印之兽(解场/炸卡) + 盖放赫之烙印"
            ],
            "单卡: 阿鲁伯起手": [
                "1. 通常召唤【导圣者 阿鲁伯】，发动效果检索【烙印融合】",
                "2. 接【单卡: 烙印融合】主展开链..."
            ],
            "妥协: 烙印融合中 Maxx 'C' (妥协给对方抽 1-2 张)": [
                "1. 发动【烙印融合】送墓【阿不思】+【赫圣女】融合召唤【痕食龙】或【烙印龙】",
                "2. 场上留【痕食龙】/【冰剑龙】后立即过牌停手，避免给对手送过多手牌",
                "3. 结束阶段（End Phase）墓地烙印龙效果，直接在场上盖放【赫之烙印】或【烙印的追放】",
                "4. 对手回合发动【赫之烙印】，回收墓地资源融出【守护者·奇美拉】进行解场与抽牌"
            ]
        },
        "蛇眼 (Snake-Eye)": {
            "单卡: 篝火/蛇眼小火": [
                "1. 发动【篝火】检索【蛇眼小火】并通常召唤",
                "2. 发动小火效果将【原罪宝】置入魔陷区，小火送墓【原罪宝】特召【蛇眼大火】",
                "3. 大火效果拉墓地小火，两体拉【I:P伪装舞会】...",
                "4. 终场：神弓(3康) + I:P伪装舞会 + 墓地咎姬"
            ]
        },
        "白银城 (Labrynth)": {
            "两卡: 家具 + 任意手牌": [
                "1. 丢弃【白银城家具】与 1 张手牌，从卡组盖放【大欢迎白银城】",
                "2. 对方回合发动【大欢迎】，特召【大姐/白银城主】，弹回大姐或家具触发解场连锁"
            ]
        }
    }
    
    selected_deck = st.selectbox("选择卡组体系", list(COMBO_DATA.keys()))
    combos = COMBO_DATA[selected_deck]
    
    for combo_name, steps in combos.items():
        with st.expander(f"📌 {combo_name}", expanded=True):
            for step in steps:
                st.write(step)
