"""原料库：真相核心线索、红鲱鱼、人物/地点池、世界设定。

这里的每一样都是"随机只用在最上层"的那层原料。
"""

from __future__ import annotations

from .model import Trace, TraceKind, World

_TRUE = TraceKind.TRUE_TELL
_FALSE = TraceKind.FALSE_LEAD

# ---------------------------------------------------------------------------
# 核心真相线索：任何一篇都必须能追回 killer / weapon / motive 三个要素
# ---------------------------------------------------------------------------
CORE_TELLS: tuple[Trace, ...] = (
    Trace(
        id="core_killer",
        text="凶手袖口残留的泥土，与花园土壤成分一致",
        kind=_TRUE,
        truth_link=("killer",),
        surface_reading="案发前在花园里走过而已",
        tags=("身份",),
    ),
    Trace(
        id="core_weapon",
        text="凶器与伤口角度、深度完全吻合，且刃口有新缺口",
        kind=_TRUE,
        truth_link=("weapon",),
        surface_reading="随手拿的一件工具",
        tags=("物理",),
    ),
    Trace(
        id="core_motive",
        text="死者书房夹着一张被撕开的股权转让书",
        kind=_TRUE,
        truth_link=("motive",),
        surface_reading="无关的旧文件",
        tags=("动机",),
    ),
)

# ---------------------------------------------------------------------------
# 红鲱鱼：与真相无关，只为把嫌疑引向别的角色
# ---------------------------------------------------------------------------
DECOYS: tuple[Trace, ...] = (
    Trace(
        id="decoy_affair",
        text="死者的配偶在案发当晚与他人有暧昧短信往来",
        kind=_FALSE,
        surface_reading="配偶有动机",
        points_at="配偶",
        tags=("红鲱鱼",),
    ),
    Trace(
        id="decoy_debt",
        text="死者的合伙人近期被催债，账户几乎清零",
        kind=_FALSE,
        surface_reading="合伙人为钱杀人",
        points_at="合伙人",
        tags=("红鲱鱼",),
    ),
    Trace(
        id="decoy_threat",
        text="门口收到匿名恐吓信，字迹被认出属于一名前雇员",
        kind=_FALSE,
        surface_reading="前雇员报复",
        points_at="前雇员",
        tags=("红鲱鱼",),
    ),
    Trace(
        id="decoy_will",
        text="遗嘱公证人透露，死者原计划下周修改遗嘱",
        kind=_FALSE,
        surface_reading="某个继承人在抢先动手",
        points_at="继承人",
        tags=("红鲱鱼",),
    ),
)

# ---------------------------------------------------------------------------
# 人物 / 地点 / 时间池
# ---------------------------------------------------------------------------
KILLERS: tuple[str, ...] = ("合伙人", "配偶", "私人医生", "司机", "弟弟")
MOTIVES: tuple[str, ...] = ("股权纠纷", "高额保险金", "婚外情败露", "继承权之争", "旧案被勒索")
WEAPONS: tuple[str, ...] = ("书房装饰剑", "青铜镇纸", "预先调换的药剂", "登山绳", "冰锥")
LOCATIONS: tuple[str, ...] = ("郊区别墅书房", "顶层复式公寓", "海边旅店房间", "地下车库")
TIME_WINDOWS: tuple[str, ...] = ("昨晚 21:00–23:00", "凌晨 1:00–3:00", "案发当日午后")

# ---------------------------------------------------------------------------
# 世界设定：决定"哪些诡计能用"
# ---------------------------------------------------------------------------
WORLDS: tuple[World, ...] = (
    World(
        name="郊区别墅",
        capabilities=frozenset({"预置机关", "掌握作息", "体力优势", "布置现场", "伪造文书"}),
        environment=frozenset({"低温环境", "可融冰介质", "复式公寓", "钟表", "录音设备", "双人身份"}),
    ),
    World(
        name="城市公寓",
        capabilities=frozenset({"预置机关", "医学知识", "化学知识", "伪造文书"}),
        environment=frozenset({"钟表", "录音设备", "药物", "低温环境"}),
    ),
    World(
        name="海边旅店",
        capabilities=frozenset({"体力优势", "布置现场", "掌握作息"}),
        environment=frozenset({"双人身份", "复式公寓", "钟表"}),
    ),
)

WORLD_BY_NAME: dict[str, World] = {w.name: w for w in WORLDS}
