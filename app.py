import streamlit as st
import math
import random

st.set_page_config(page_title="Master Duel 烙印展开助手", layout="wide", initial_sidebar_state="expanded")

st.title("🃏 Master Duel 烙印卡组展开与牌效提示器")

tab1, tab2, tab3 = st.tabs(["🔍 卡牌展开顺序提示", "📊 动点概率计算", "🎲 起手模拟抽牌"])

# --- TAB 1: 核心功能 - 输入卡牌提示展开步骤 ---
with tab1:
    st.subheader("📖 烙印手牌展开路线检索")
    st.caption("输入或选择你起手中的启动单卡，系统将按连锁和严格规则显示展开步骤：")

    # 严格符合游戏王规则与 MD 牌效机制的烙印展开库
    BRANDED_COMBOS = [
        {
            "card_names": ["阿鲁伯", "导圣者 阿鲁伯", "导圣者"],
            "title": "【阿鲁伯单卡起手】标准深渊之兽完全体展开（最稳主线）",
            "condition": "手牌：【导圣者 阿鲁伯】1 张 + 任意手牌 1 张 (作神炎龙 Cost)",
            "steps": [
                "步骤 1：通常召唤【导圣者 阿鲁伯】，发动效果从卡组检索【烙印融合】。",
                "步骤 2：发动【烙印融合】，从卡组将【阿不思的落胤】+【深渊之兽 鲁贝利乌斯】（8星·光属性）送入墓地，融合召唤【烙印龙 阿尔比昂】（8星·暗属性·龙族）。",
                "步骤 3：触发【烙印龙】效果（C1）：除外墓地的【阿不思的落胤】与场上的【导圣者 阿鲁伯】，融合召唤【神炎龙 赫界龙】（8星·光属性·龙族）。",
                "步骤 4：触发【神炎龙】效果（C1）：弃置 1 张手牌，将其自身与除外区的【阿不思的落胤】洗回卡组，融合召唤【冰剑龙 赫界龙】。",
                "步骤 5：发动墓地【深渊之兽 鲁贝利乌斯】效果：解放场上依然留存的【烙印龙 阿尔比昂】（8星·暗属性·龙族，满足祭品条件），将其特殊召唤到场上。",
                "步骤 6：发动场上【深渊之兽 鲁贝利乌斯】效果：从卡组将【失烙印】或【烙印之兽】表侧放置到魔陷区。",
                "步骤 7：进入结束阶段（End Phase）：被解放送墓的【烙印龙 阿尔比昂】效果发动，从卡组将【赫之烙印】盖放到场上（若场上贴了失烙印，可选择检索赫圣女）。",
                "🎯 最终终场：冰剑龙（二速非取对象除外） + 鲁贝利乌斯（2500打点） + 烙印之兽（炸1卡） + 盖放赫之烙印（对方回合二速奇美拉炸2抽1）。"
            ]
        },
        {
            "card_names": ["烙印融合", "Branded Fusion"],
            "title": "【烙印融合单卡起手】悲剧运转轴（单卡拉满牌效）",
            "condition": "手牌：【烙印融合】1 张 + 任意手牌 1 张 (作神炎龙 Cost)",
            "steps": [
                "步骤 1：发动【烙印融合】，从卡组将【阿不思的落胤】+【绝望之悲剧】（暗属性）送入墓地，融合召唤【神炎龙 赫界龙】。",
                "步骤 2：组成连锁：神炎龙 C1（弃 1 手牌作为 Cost），墓地悲剧 C2（除外自身）。",
                "步骤 3：逆结算：悲剧检索【导圣者 阿鲁伯】入手；神炎龙将墓地阿不思与自身洗回卡组，融合召唤【冰剑龙 赫界龙】。",
                "步骤 4：通常召唤检索上手的【导圣者 阿鲁伯】，发动阿鲁伯效果检索速攻魔法【赫之烙印】（或【烙印断罪】/【烙印失控】）。",
                "步骤 5：发动【冰剑龙】效果（Cost 堆墓额外卡组的【烙印龙 阿尔比昂】），除外场上的阿鲁伯（或者空发堆墓），为 EP 准备素材。",
                "步骤 6：进入结束阶段（End Phase）：墓地【烙印龙】效果触发，从卡组盖放【烙印开幕】或检索【赫圣女】补强手牌。",
                "🎯 最终终场：冰剑龙（二速除外） + 手牌/前场资源调度完毕 + 赫之烙印待机。"
            ]
        },
        {
            "card_names": ["烙印开幕", "开幕"],
            "title": "【烙印开幕】二速展开 / 防手坑动点",
            "condition": "手牌：【烙印开幕】1 张 + 任意手牌 1 张 (开幕 Cost)",
            "steps": [
                "步骤 1：发动速攻魔法【烙印开幕】，弃置 1 张手牌（若弃置悲剧可额外触发悲剧检索），从卡组守备表示特殊召唤【导圣者 阿鲁伯】。",
                "步骤 2：触发【导圣者 阿鲁伯】登场效果，从卡组检索【烙印融合】。",
                "步骤 3：此时通常召唤权仍未消耗，且墓地开幕常驻为融合怪兽提供一次战破/效破代破。",
                "步骤 4：发动检索到的【烙印融合】，依序接入【阿鲁伯单卡】或【深渊之兽标准轴】展开。"
            ]
        },
        {
            "card_names": ["姬特", "铁兽鸟 姬特", "铁兽鸟"],
            "title": "【铁兽鸟 姬特 / 气炎】黑衣龙调度牌效轴",
            "condition": "手牌：【铁兽鸟 姬特】1 张（或【烙印的气炎】+ 任意龙族怪兽）",
            "steps": [
                "步骤 1：场上有阿不思融合怪兽时（或通召姬特），发动效果从卡组检索【烙印融合】，随后选择 1 张手牌放回卡组最下方。",
                "步骤 2：若手牌有【黑衣龙 阿不思之落胤】，发动效果从卡组将【烙印断罪】送墓，黑衣龙将自身洗回卡组抽 1 张牌。",
                "步骤 3：发动墓地【烙印断罪】效果，将其自身除外，把墓地被使用过的【烙印融合】回收至手牌，实现无耗滤抽与核心运转循环。"
            ]
        },
        {
            "card_names": ["赫圣女", "卡尔特西亚", "赫圣女 卡尔特西亚"],
            "title": "【赫圣女 卡尔特西亚】二速融合与阻抗补点",
            "condition": "手牌：【赫圣女 卡尔特西亚】1 张 + 场上/墓地存在【阿不思的落胤】",
            "steps": [
                "步骤 1：若场上或墓地有【阿不思】，赫圣女可直接从手牌特殊召唤。",
                "步骤 2：主要阶段（自身或对方回合）发动赫圣女二速效果：将场上赫圣女与场上/手牌暗属性怪兽融合，召唤【赫焉龙 圣奎萨尔】。",
                "步骤 3：触发【赫焉龙】效果，从卡组精准堆墓【导圣之圣女 库埃姆】或【绝望之悲剧】。",
                "步骤 4：若本回合有融合怪兽送墓，结束阶段触发【赫圣女】墓地诱发效果，直接将其回收至手牌，提供无限循环牌效。"
            ]
        },
        {
            "card_names": ["增殖的G", "中G", "妥协", "Maxx C"],
            "title": "【防手坑妥协】中【增殖的 G】极小代价停牌路线",
            "condition": "场景：发动【烙印融合】时，对方连锁发动【增殖的 G】",
            "steps": [
                "步骤 1：【烙印融合】照常通过：从卡组送墓【阿不思】+【赫圣女】（或深兽），融合召唤【痕食龙 赫界龙】（对方仅抽 1 张牌）。",
                "步骤 2：不发动痕食龙后续任何特殊召唤效果，直接过牌进入结束阶段（End Phase）。",
                "步骤 3：阻抗评估：场上留存【痕食龙】（二速无效对方从额外卡组特召怪兽的效果并弹回手牌 1 只怪兽，且自身战斗力可观）。",
                "步骤 4：对方仅抽 1 张手牌，未能产生牌差压制，下回合轮到己方依然保有完整坟场资源。"
            ]
        }
    ]

    col_select, col_search = st.columns([1, 2])
    with col_select:
        selected_card = st.selectbox(
            "快捷点击卡牌：",
            ["导圣者 阿鲁伯", "烙印融合", "烙印开幕", "铁兽鸟 姬特", "赫圣女 卡尔特西亚", "中增殖的G妥协"]
        )
    with col_search:
        input_query = st.text_input("或者手动输入手牌关键词（例：阿鲁伯、烙融、开幕、赫圣女）：", value=selected_card)

    query = input_query.strip().lower()
    matched = False

    for combo in BRANDED_COMBOS:
        if any(name.lower() in query for name in combo["card_names"]):
            matched = True
            st.markdown(f"### 📍 {combo['title']}")
            st.markdown(f"**【前置条件】**：`{combo['condition']}`")
            st.write("---")
            for step in combo["steps"]:
                st.info(step)
            break

    if not matched:
        st.warning(f"未能直接匹配与 “{input_query}” 对应的固定起手。请尝试从下拉菜单选择标准动点！")

# --- TAB 2: 动点概率计算 ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        deck_size = st.number_input("卡组总张数", value=40, min_value=40, max_value=60)
        hand_size = st.radio("先后手抽牌数", [5, 6], format_func=lambda x: f"先手 ({x}张)" if x == 5 else f"后手 ({x}张)")
        starters = st.slider("初动点总数 (阿鲁伯+烙融+开幕等)", 1, 20, 8)
        handtraps = st.slider("手坑/阻抗数量", 0, 20, 9)
    with col2:
        def calc_prob(k, n=hand_size, N=deck_size):
            if k <= 0: return 0.0
            if k > N: return 100.0
            return (1 - math.comb(N - k, n) / math.comb(N, n)) * 100

        p_starter = calc_prob(starters)
        p_ht = calc_prob(handtraps)
        st.metric("起手抓到至少 1 张初动点的概率", f"{p_starter:.2f}%")
        st.metric("起手抓到至少 1 张手坑的概率", f"{p_ht:.2f}%")
        st.metric("理想起手 (初动 + 手坑并存)", f"{(p_starter * p_ht / 100):.2f}%")

# --- TAB 3: 手牌抽样模拟器 ---
with tab3:
    if st.button("🎴 模拟起手抽牌 (5张)", type="primary"):
        deck = (["动点"] * starters) + (["手坑"] * handtraps) + (["自由位/其他"] * max(0, deck_size - starters - handtraps))
        hand = random.sample(deck, hand_size)
        cols = st.columns(hand_size)
        for i, card in enumerate(hand):
            badge = "🟢 初动" if card == "动点" else ("🔵 阻抗" if card == "手坑" else "⚪ 资源")
            cols[i].metric(f"手牌 {i+1}", card, delta=badge)
        if "动点" in hand:
            st.success("✅ 手牌含有初动，可依照 TAB 1 步骤启动！")
        else:
            st.error("❌ 起手无初动点，需要借助手坑打断对手或过牌！")
