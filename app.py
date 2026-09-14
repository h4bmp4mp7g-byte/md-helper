import streamlit as st
import math
import random

st.set_page_config(page_title="MD 烙印展开助手", layout="wide", initial_sidebar_state="expanded")

st.title("🃏 Master Duel 烙印精准动点与展开助手")

tab1, tab2, tab3 = st.tabs(["📊 动点概率计算", "🎲 起手模拟抽牌", "🔍 烙印 Combo 动态检索器"])

# --- TAB 1: 概率计算器 ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ 卡组参数配置")
        deck_size = st.number_input("卡组总张数", value=40, min_value=40, max_value=60, step=1)
        hand_size = st.radio("先后手", [5, 6], format_func=lambda x: f"先手 ({x}张)" if x == 5 else f"后手 ({x}张)")
        starters = st.slider("初动点张数 (烙融/阿鲁伯/开幕等)", 1, 20, 8)
        handtraps = st.slider("手坑/拦截张数", 0, 20, 9)
        bricks = st.slider("废件/上手难受卡牌", 0, 10, 2)

    with col2:
        st.subheader("📈 起手概率分析")
        def calc_prob(k, n=hand_size, N=deck_size):
            if k <= 0: return 0.0
            if k > N: return 100.0
            prob_zero = math.comb(N - k, n) / math.comb(N, n)
            return (1 - prob_zero) * 100

        p_starter = calc_prob(starters)
        p_ht = calc_prob(handtraps)

        st.metric("起手【至少 1 张初动】概率", f"{p_starter:.2f}%")
        st.metric("起手【至少 1 张手坑】概率", f"{p_ht:.2f}%")
        st.metric("理想起手 (动点 + 手坑同时上手)", f"{(p_starter / 100 * p_ht / 100) * 100:.2f}%")

# --- TAB 2: 起手抽牌模拟 ---
with tab2:
    st.subheader("🎲 5 张起手模拟抽样")
    if st.button("🎴 点击洗牌并抽取起手", type="primary"):
        deck = (["动点"] * starters) + (["手坑"] * handtraps) + (["废件"] * bricks)
        remaining = max(0, deck_size - len(deck))
        deck += ["普通卡"] * remaining
        
        hand = random.sample(deck, hand_size)
        cols = st.columns(hand_size)
        
        for i, card in enumerate(hand):
            if card == "动点": color_code, emoji = "🟢", "【初动】"
            elif card == "手坑": color_code, emoji = "🔵", "【手坑】"
            elif card == "废件": color_code, emoji = "🔴", "【废件】"
            else: color_code, emoji = "⚪", "【自由位】"
                
            cols[i].metric(f"卡牌 {i+1}", f"{color_code} {card}", delta=emoji)
            
        st.write("---")
        if "动点" in hand:
            st.success("✅ 手牌通过！具备展开动点。")
        else:
            st.error("❌ 发生事故！手牌无动点。")

# --- TAB 3: 输入卡牌精准提示展开链 ---
with tab3:
    st.subheader("🎴 烙印卡组按卡提示展开流程")
    st.caption("输入或选择你手牌中的启动卡，下方将按顺序提示严格的展开步骤：")

    # 经典烙印卡组精准展开数据库
    BRANDED_DATABASE = [
        {
            "card_names": ["烙印融合", "Branded Fusion"],
            "title": "【单卡动点】烙印融合 (标准深渊之兽轴主线)",
            "required_hand": "【烙印融合】1 张 + 任意手牌 1 张 (作神炎龙 cost)",
            "steps": [
                "步骤 1：发动【烙印融合】，从卡组将【阿不思的落胤】与【深渊之兽 鲁贝利乌斯】作为素材送去墓地，融合召唤【神炎龙 鲁贝利乌斯】。",
                "步骤 2：触发【神炎龙】效果，弃置 1 张手牌，将其自身与墓地的【阿不思的落胤】洗回卡组，融合召唤【冰剑龙 赫界龙】。",
                "步骤 3：发动墓地【深渊之兽 鲁贝利乌斯】效果，解放场上的【神炎龙】将其特殊召唤到场上。",
                "步骤 4：发动场上【深渊之兽 鲁贝利乌斯】效果，从卡组将【烙印之兽】表侧放置到魔陷区。",
                "步骤 5：进入结束阶段（End Phase），触发墓地【烙印龙 阿尔比昂】（或冰剑龙堆墓的烙印龙）效果，在场上盖放【赫之烙印】。",
                "🎯 最终终场：冰剑龙（二速非取对象除外） + 烙印之兽（解放场上龙族解场） + 盖放赫之烙印（对方回合融奇美拉/赫焉龙）。"
            ]
        },
        {
            "card_names": ["阿鲁伯", "导圣者 阿鲁伯", "导圣者"],
            "title": "【单卡动点】导圣者 阿鲁伯 (通召起手)",
            "required_hand": "【导圣者 阿鲁伯】1 张",
            "steps": [
                "步骤 1：通常召唤【导圣者 阿鲁伯】，发动效果从卡组检索【烙印融合】。",
                "步骤 2：发动【烙印融合】，从卡组将【阿不思的落胤】与【深渊之兽 鲁贝利乌斯】送墓融合【神炎龙】。",
                "步骤 3：【神炎龙】弃 1 手牌洗回阿不思与自身，融合召唤【冰剑龙 赫界龙】。",
                "步骤 4：墓地【深渊之兽 鲁贝利乌斯】解放场上的【阿鲁伯】特殊召唤，卡组表侧置放【烙印之兽】。",
                "步骤 5：结束阶段（End Phase）墓地烙印龙效果，盖放【赫之烙印】。",
                "🎯 最终终场：冰剑龙 + 烙印之兽 + 盖放赫之烙印。"
            ]
        },
        {
            "card_names": ["烙印开幕", "开幕"],
            "title": "【单卡动点】烙印开幕 (二速/防手坑起手)",
            "required_hand": "【烙印开幕】1 张 + 任意手牌 1 张 (开幕 cost)",
            "steps": [
                "步骤 1：发动速攻魔法【烙印开幕】，弃置 1 张手牌，从卡组守备表示特殊召唤【导圣者 阿鲁伯】。",
                "步骤 2：触发【阿鲁伯】效果，从卡组检索【烙印融合】。",
                "步骤 3：发动【烙印融合】，后续顺次接入【烙印融合标准主线】展开流程。"
            ]
        },
        {
            "card_names": ["绝望之悲剧", "悲剧"],
            "title": "【配合动点】绝望之悲剧 (被送墓/弃置检索)",
            "required_hand": "【绝望之悲剧】（作为烙印开幕/神炎龙/愚蠢的副葬等效果 cost 送墓时）",
            "steps": [
                "步骤 1：【绝望之悲剧】被效果送去墓地或被除外时，触发 C1 强制/诱发效果。",
                "步骤 2：从卡组检索【导圣者 阿鲁伯】或【绝望之大剧场】到手牌。",
                "步骤 3：若尚未通召，通常召唤检索到的【阿鲁伯】继续检索【烙印融合】进行展开。"
            ]
        },
        {
            "card_names": ["赫圣女", "卡尔特西亚", "赫圣女 卡尔特西亚"],
            "title": "【补点/展开】赫圣女 卡尔特西亚",
            "required_hand": "【赫圣女 卡尔特西亚】1 张 + 场上/墓地有【阿不思的落胤】",
            "steps": [
                "步骤 1：若墓地或场上有【阿不思】，发动【赫圣女】手牌效果将其特殊召唤。",
                "步骤 2：主要阶段发动【赫圣女】二速效果，将场上的赫圣女与手牌/场上的【阿不思】（或暗属性怪兽）融合召唤【赫焉龙 圣奎萨尔】。",
                "步骤 3：发动【赫焉龙】效果，从卡组将【导圣之圣女 库埃姆】或【黑衣龙】送去墓地。",
                "步骤 4：结束阶段（End Phase）触发【赫圣女】墓地效果，回收至手牌。"
            ]
        }
    ]

    # 下拉框 + 文本输入双重快捷选择
    quick_select = st.selectbox(
        "快捷选择手牌动点：", 
        ["烙印融合", "导圣者 阿鲁伯", "烙印开幕", "绝望之悲剧", "赫圣女 卡尔特西亚"]
    )
    user_input = st.text_input("或手动输入手牌卡名进行精准搜索：", value=quick_select)

    query = user_input.strip()
    matched = False

    for combo in BRANDED_DATABASE:
        if any(name.lower() in query.lower() for name in combo["card_names"]):
            matched = True
            st.markdown(f"### 📌 {combo['title']}")
            st.caption(f"🔑 **手牌要求**：{combo['required_hand']}")
            st.write("---")
            
            # 按顺序提示展开流程
            for step in combo["steps"]:
                st.info(step)

    if not matched:
        st.warning(f"未找到与 “{query}” 匹配的烙印展开链。请尝试输入：烙印融合、阿鲁伯、开幕、悲剧 或 赫圣女。")
