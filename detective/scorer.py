"""评价函数 —— "选取最精妙的一段"那一步的核心（重构版）。

旧版有两个致命偏见：
    1. 惊异随红鲱鱼数量单调上升 —— 于是"最优解"永远是塞满线索的拥挤故事。
    2. 只看覆盖，不看唯一可解、误导时机、陈词滥调。

新版把"精妙"拆成三个必须同时成立的因子（乘法）：
        精妙 = 必然(公平) × 唯一可解 × 惊异
再加 经济 / 一致 / 时机 / 多样性 作为修正项。

关键改动：
    - 惊异：边际递减 + 拥挤惩罚，非单调，存在最优点；
    - 唯一可解：同一嫌疑人被多条红鲱鱼堆砌 => 破坏唯一性，扣分；
    - 时机：红鲱鱼前置、真相后置 => 误导曲线优雅；
    - 多样性：同类别诡计堆叠 => 陈词滥调，扣分。

所有权重与公式都可调：改 WEIGHTS / _INGENUITY_SHARE。
"""

from __future__ import annotations

from dataclasses import dataclass

from . import constraints
from .model import Plot, TraceKind, World

# 修正项权重（合计 1.0）
WEIGHTS: dict[str, float] = {
    "fair_play": 0.20,  # 可解性：揭晓前读者理论上能否推出
    "unique_solution": 0.20,  # 唯一可解：推出来的只能是真凶那一个解
    "surprise": 0.20,  # 反转强度：真凶偏离直觉有多远
    "economy": 0.12,  # 经济性：没有废笔
    "coherence": 0.12,  # 世界一致性
    "timing": 0.08,  # 误导时机：红鲱鱼前置、真相后置
    "diversity": 0.08,  # 反陈词滥调：同类诡计不堆叠
}

# three-factor 精妙分与其余修正项在总分中的占比
_INGENUITY_SHARE = 0.55

# 超过这个"负载"，故事开始显得拥挤，惊异被稀释
_LOAD_COMFORT = 3.0


@dataclass
class Score:
    fair_play: float
    unique_solution: float
    surprise: float
    economy: float
    coherence: float
    timing: float
    diversity: float
    ingenuity: float
    total: float


# ---------------------------------------------------------------------------
# 各维度
# ---------------------------------------------------------------------------
def _fair_play(plot: Plot) -> float:
    required = plot.trajectory.required_recovery()
    if not required:
        return 1.0
    return len(required & plot.covered_truth()) / len(required)


def _unique_solution(plot: Plot) -> float:
    """每出现一个"看似成立的替代凶手"，唯一性减半。"""
    viable = constraints.viable_alternatives(plot)
    return max(0.0, 1.0 - 0.5 * len(viable))


def _surprise(plot: Plot) -> float:
    """惊异 = 边际递减的落差 × 拥挤惩罚（非单调）。"""
    off_killer = constraints.distinct_red_herring_suspects(plot)
    n = min(len(off_killer), 3)
    raw = 0.30 + 0.50 * (1 - 0.5 ** n)  # n=0→0.30, 1→0.55, 2→0.675, 3→0.7375

    load = len(plot.trajectory.tricks) + 0.5 * len(plot.false_leads)
    penalty = max(0.60, 1.0 - max(0.0, load - _LOAD_COMFORT) * 0.10)
    return min(1.0, raw * penalty)


def _economy(plot: Plot) -> float:
    required_n = len(plot.trajectory.required_recovery())
    presented_n = len(plot.presented) or 1
    return min(1.0, required_n / presented_n)


def _timing(plot: Plot) -> float:
    """红鲱鱼是否比真相更早出现。前置误导、后置揭底 => 高分。"""
    n = len(plot.presented)
    if n <= 1:
        return 0.5
    true_pos = [i / (n - 1) for i, t in enumerate(plot.presented) if t.kind is TraceKind.TRUE_TELL]
    false_pos = [i / (n - 1) for i, t in enumerate(plot.presented) if t.kind is TraceKind.FALSE_LEAD]
    if not true_pos or not false_pos:
        return 0.5
    mt = sum(true_pos) / len(true_pos)
    mf = sum(false_pos) / len(false_pos)
    return max(0.0, min(1.0, 0.5 + (mt - mf)))


def _diversity(plot: Plot) -> float:
    """同类别的诡计堆叠 = 陈词滥调。"""
    cats = [t.category for t in plot.trajectory.tricks]
    if not cats:
        return 1.0
    repeats = len(cats) - len(set(cats))
    return max(0.0, 1.0 - repeats / len(cats))


# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------
def score_plot(plot: Plot, world: World) -> Score:
    fair = _fair_play(plot)
    unique = _unique_solution(plot)
    surprise = _surprise(plot)
    economy = _economy(plot)
    coh = constraints.coherence(plot, world)
    timing = _timing(plot)
    diversity = _diversity(plot)

    # 精妙 = 惊异 × 必然 × 唯一，缺一即崩
    ingenuity = fair * unique * surprise

    weighted = (
        WEIGHTS["fair_play"] * fair
        + WEIGHTS["unique_solution"] * unique
        + WEIGHTS["surprise"] * surprise
        + WEIGHTS["economy"] * economy
        + WEIGHTS["coherence"] * coh
        + WEIGHTS["timing"] * timing
        + WEIGHTS["diversity"] * diversity
    )
    total = _INGENUITY_SHARE * ingenuity + (1 - _INGENUITY_SHARE) * weighted

    return Score(fair, unique, surprise, economy, coh, timing, diversity, ingenuity, total)


def format_score(s: Score) -> str:
    return (
        f"综合 {s.total:.3f} | 精妙(必然×唯一×惊异) {s.ingenuity:.3f}\n"
        f"        必然 {s.fair_play:.2f} | 唯一 {s.unique_solution:.2f} | 惊异 {s.surprise:.2f} | "
        f"经济 {s.economy:.2f} | 一致 {s.coherence:.2f} | 时机 {s.timing:.2f} | 多样 {s.diversity:.2f}"
    )
