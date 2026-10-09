"""倒推生成管线。

    1. 从世界事实筛出可用诡计
    2. 采样一组互不冲突的诡计 -> 真相轨迹
    3. 由轨迹推导痕迹（核心线索 + 各诡计签名线索）
    4. 注入红鲱鱼并决定呈现顺序
    5. 交给 scorer 打分、排序（可选去重，避免选出一堆克隆）

随机只发生在第 2、4 步的"选原料 / 选顺序"上；
痕迹由真相推导，绝不随机撒。
"""

from __future__ import annotations

import random

from . import constraints
from .element_library import (
    CORE_TELLS,
    DECOYS,
    KILLERS,
    LOCATIONS,
    MOTIVES,
    TIME_WINDOWS,
    WEAPONS,
)
from .model import Plot, Trace, TraceKind, Trajectory, Trick, World
from .scorer import Score, score_plot
from .trick_library import ALL_TRICKS


def _sample_tricks(available: list[Trick], k: int, rng: random.Random, tries: int = 60) -> list[Trick]:
    """采样 k 个前提满足且互不冲突的诡计。"""
    if not available:
        return []
    k = max(1, min(k, len(available)))
    for _ in range(tries):
        pick = rng.sample(available, k)
        if not constraints.has_conflict(pick):
            return pick
    for t in rng.sample(available, len(available)):
        return [t]
    return []


def _make_trajectory(rng: random.Random, tricks: list[Trick]) -> Trajectory:
    return Trajectory(
        killer=rng.choice(KILLERS),
        motive=rng.choice(MOTIVES),
        weapon=rng.choice(WEAPONS),
        location=rng.choice(LOCATIONS),
        time_window=rng.choice(TIME_WINDOWS),
        tricks=list(tricks),
    )


def _assemble(pool: list[Trace], rng: random.Random, front_load_prob: float = 0.7) -> list[Trace]:
    """注入红鲱鱼并决定呈现顺序。

    front_load 时把红鲱鱼整体前置、真相整体后置（优雅的误导曲线）；
    否则完全打乱。两种都生成，交给评价函数去挑。
    """
    truths = list(pool)
    n_decoys = rng.randint(0, 3)
    decoys = rng.sample(list(DECOYS), min(n_decoys, len(DECOYS)))
    rng.shuffle(truths)
    rng.shuffle(decoys)

    if decoys and rng.random() < front_load_prob:
        return decoys + truths

    combined = truths + decoys
    rng.shuffle(combined)
    return combined


def generate_candidates(
    world: World,
    n: int = 300,
    seed: int = 0,
    drop_rate: float = 0.15,
    tricks: list[Trick] | None = None,
) -> list[Plot]:
    """生成 n 个候选故事（未经打分）。

    drop_rate: 以一定概率漏掉一条真线索，制造"不公平"的候选，
               让打分真正发挥作用。
    """
    rng = random.Random(seed)
    all_tricks = tricks if tricks is not None else ALL_TRICKS
    available = constraints.available_tricks(world, all_tricks)

    plots: list[Plot] = []
    for _ in range(n):
        chosen = _sample_tricks(available, rng.randint(1, 3), rng)
        if not chosen:
            continue
        traj = _make_trajectory(rng, chosen)

        pool: list[Trace] = list(CORE_TELLS)
        for t in chosen:
            pool.extend(x for x in t.traces if x.kind is TraceKind.TRUE_TELL)

        if rng.random() < drop_rate and pool:
            pool.pop(rng.randrange(len(pool)))

        plots.append(Plot(trajectory=traj, presented=_assemble(pool, rng)))
    return plots


def plot_signature(plot: Plot) -> tuple[str, ...]:
    """一个故事的"骨架指纹"：用了哪些诡计、哪些红鲱鱼。

    用于去重 —— 指纹相同的候选视为克隆，不重复入选。
    """
    tricks = tuple(sorted(t.id for t in plot.trajectory.tricks))
    decoys = tuple(sorted(d.id for d in plot.false_leads))
    return tricks + ("|",) + decoys


def rank(
    plots: list[Plot],
    world: World,
    top: int = 5,
    diverse: bool = True,
) -> list[tuple[Plot, Score]]:
    """按评价函数排序。

    diverse=True 时做骨架去重，保证前 top 名是真正不同的故事，
    而不是同一模板换名字的克隆。
    """
    scored = [(p, score_plot(p, world)) for p in plots]
    scored.sort(key=lambda ps: ps[1].total, reverse=True)

    if not diverse:
        return scored[:top]

    out: list[tuple[Plot, Score]] = []
    seen: set[tuple[str, ...]] = set()
    for plot, score in scored:
        sig = plot_signature(plot)
        if sig in seen:
            continue
        seen.add(sig)
        out.append((plot, score))
        if len(out) >= top:
            break
    return out
