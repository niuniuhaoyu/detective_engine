"""核心数据模型。

一条推理链在结构上是：真相轨迹(Trajectory) --造成--> 痕迹(Trace)。
"呈现"(Plot) 则是从痕迹里挑选若干条，按某个顺序交给读者。
创作的手艺发生在"挑选 + 排序"这一步，而不在随机撒痕迹那一步。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TraceKind(str, Enum):
    """痕迹的两种功能。"""

    TRUE_TELL = "true_tell"  # 真线索：它真实地由真相造成，但表面可被误读
    FALSE_LEAD = "false_lead"  # 红鲱鱼：与真相无关，只为把侦探引向别人


# 每篇都必须让读者能追回的"核心真相要素"
CORE_TOKENS: tuple[str, ...] = ("killer", "weapon", "motive")


@dataclass(frozen=True)
class Trace:
    """一条可被观察到的痕迹。

    text            中性描述：现场/物证上"看到的东西"
    truth_link      它真实指向的要素：诡计 id 或 CORE_TOKENS 之一
    surface_reading 侦探与读者的第一层误读（精妙感就藏在这里）
    points_at       FALSE_LEAD 专用：这条红鲱鱼把嫌疑引向谁（角色名）
    """

    id: str
    text: str
    kind: TraceKind
    truth_link: tuple[str, ...] = ()
    surface_reading: str = ""
    tags: tuple[str, ...] = ()
    points_at: str = ""


@dataclass(frozen=True)
class Trick:
    """一个诡计/机关，是"真相"与"痕迹"之间的转换器。

    premises       成立所需的世界事实（能力或环境），必须被 World 满足
    traces         该诡计必然留下的痕迹（含至少一条 TRUE_TELL 作签名）
    reveal         揭晓时它是如何被识破的
    conflicts_with 与之互斥的诡计 id（同一轴上的两套把戏不能并存）
    """

    id: str
    name: str
    category: str
    premises: frozenset[str]
    traces: tuple[Trace, ...]
    reveal: str
    conflicts_with: frozenset[str] = frozenset()


@dataclass
class World:
    """场景设定：给"哪些诡计能用"上枷锁。"""

    name: str
    capabilities: frozenset[str]  # 凶手具备的能力
    environment: frozenset[str]  # 环境中存在的东西

    @property
    def facts(self) -> frozenset[str]:
        return self.capabilities | self.environment


@dataclass
class Trajectory:
    """真相轨迹：谁、为什么、用什么、在哪、什么时候、用了哪些诡计。"""

    killer: str
    motive: str
    weapon: str
    location: str
    time_window: str
    tricks: list[Trick] = field(default_factory=list)

    def required_recovery(self) -> set[str]:
        """读者在揭晓前理论上应当能追回的要素集合。"""
        required = set(CORE_TOKENS)
        required.update(t.id for t in self.tricks)
        return required


@dataclass
class Plot:
    """一个候选故事：真相轨迹 + 按顺序呈现给读者的痕迹。"""

    trajectory: Trajectory
    presented: list[Trace]

    @property
    def true_tells(self) -> list[Trace]:
        return [t for t in self.presented if t.kind is TraceKind.TRUE_TELL]

    @property
    def false_leads(self) -> list[Trace]:
        return [t for t in self.presented if t.kind is TraceKind.FALSE_LEAD]

    def covered_truth(self) -> set[str]:
        """被呈现的真线索实际覆盖到的真相要素。"""
        covered: set[str] = set()
        for t in self.true_tells:
            covered.update(t.truth_link)
        return covered
