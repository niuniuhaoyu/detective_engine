"""约束层：世界一致性 + 公平性。

这是把"随机"变成"可解故事"的关键。
"""

from __future__ import annotations

from .model import Plot, Trick, World


def premises_ok(trick: Trick, world: World) -> bool:
    """诡计的全部前提必须被世界事实满足。"""
    return trick.premises <= world.facts


def available_tricks(world: World, tricks: list[Trick]) -> list[Trick]:
    return [t for t in tricks if premises_ok(t, world)]


def has_conflict(tricks: list[Trick]) -> bool:
    """同一轴上互斥的两套把戏不能并存。"""
    ids = {t.id for t in tricks}
    for t in tricks:
        if t.conflicts_with & ids:
            return True
    return False


def fair_play(plot: Plot) -> tuple[bool, set[str]]:
    """公平性：揭晓前，读者应能追回全部 required 要素。

    返回 (是否公平, 缺失的要素集合)。
    """
    required = plot.trajectory.required_recovery()
    missing = required - plot.covered_truth()
    return (not missing), missing


def distinct_red_herring_suspects(plot: Plot) -> set[str]:
    """把嫌疑引向真凶以外角色的、不重复的红鲱鱼目标。"""
    killer = plot.trajectory.killer
    return {d.points_at for d in plot.false_leads if d.points_at and d.points_at != killer}


def alternative_support(plot: Plot) -> dict[str, int]:
    """每条红鲱鱼各自把嫌疑引向谁 -> 该嫌疑人获得的支持票数。"""
    support: dict[str, int] = {}
    for d in plot.false_leads:
        if d.points_at:
            support[d.points_at] = support.get(d.points_at, 0) + 1
    return support


def viable_alternatives(plot: Plot, threshold: int = 2) -> dict[str, int]:
    """"看似成立"的替代凶手。

    单条红鲱鱼只是疑点；一旦同一嫌疑人被 >= threshold 条线索支撑，
    读者就会真的看到一个"完整但错误"的案子 —— 唯一可解性被破坏。
    """
    killer = plot.trajectory.killer
    return {s: c for s, c in alternative_support(plot).items() if s != killer and c >= threshold}


def coherence(plot: Plot, world: World) -> float:
    """世界一致性分数：前提未满足或存在互斥则扣分。"""
    score = 1.0
    for t in plot.trajectory.tricks:
        if not premises_ok(t, world):
            score -= 0.3
    if has_conflict(plot.trajectory.tricks):
        score -= 0.4
    return max(0.0, score)
