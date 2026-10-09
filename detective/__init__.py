"""detective —— 约束驱动的侦探推理小说生成引擎（地基版）。

分层：
    model      数据模型：Trace / Trick / World / Trajectory / Plot
    trick_library   诡计库（可扩展的规则原料）
    element_library 原料库：真相核心线索、红鲱鱼、人物池、世界设定
    constraints     约束：前提满足、诡计冲突、公平性
    scorer          评价函数：公平 / 惊异 / 红鲱鱼 / 经济 / 一致
    generator       倒推生成管线

设计原则（见 README）：
    随机只负责最上层原料，下面全部用约束与倒推。
"""

from .model import Trace, TraceKind, Trick, World, Trajectory, Plot
from . import trick_library, element_library, constraints, scorer, generator

__all__ = [
    "Trace",
    "TraceKind",
    "Trick",
    "World",
    "Trajectory",
    "Plot",
    "trick_library",
    "element_library",
    "constraints",
    "scorer",
    "generator",
]
