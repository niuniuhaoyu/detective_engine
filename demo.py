"""演示：为每个世界生成大量候选，挑出最精妙的几个。

    cd detective_engine
    python demo.py

同时把结果写入 out/candidates.md（UTF-8），避免 Windows 控制台乱码。
"""

from __future__ import annotations

import sys
from pathlib import Path

from detective import generator, scorer
from detective.element_library import WORLDS
from detective.model import Plot, TraceKind

_CN_KIND = {TraceKind.TRUE_TELL: "真线索", TraceKind.FALSE_LEAD: "红鲱鱼"}


def render(rank_index: int, plot: Plot, score, world_name: str) -> str:
    traj = plot.trajectory
    lines: list[str] = []
    lines.append(f"## 候选 #{rank_index}　世界：{world_name}")
    lines.append("")
    lines.append("```")
    lines.append(scorer.format_score(score))
    lines.append("```")
    lines.append(
        f"**真相**：凶手是　{traj.killer}　|　动机 {traj.motive}　|　"
        f"凶器 {traj.weapon}　|　地点 {traj.location}　|　时间 {traj.time_window}"
    )
    tricks = "；".join(f"{t.name}（{t.category}）" for t in traj.tricks) or "无"
    lines.append(f"**诡计**：{tricks}")
    lines.append("")
    lines.append("**线索（呈现顺序）**")
    for i, tr in enumerate(plot.presented, 1):
        kind = _CN_KIND[tr.kind]
        if tr.kind is TraceKind.TRUE_TELL:
            hint = f"真相→{'/'.join(tr.truth_link)}"
        else:
            hint = f"引向→{tr.points_at}"
        lines.append(f"{i}. **[{kind}]** {tr.text}　——　读者读作：{tr.surface_reading}（{hint}）")
    lines.append("")
    lines.append("**揭晓**")
    for t in traj.tricks:
        lines.append(f"- {t.name}：{t.reveal}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    out_lines: list[str] = ["# 最精妙的候选（倒推 + 约束 + 多维度评分）", ""]
    for world in WORLDS:
        plots = generator.generate_candidates(world, n=600, seed=2026)
        top = generator.rank(plots, world, top=3)
        out_lines.append(f"# 世界【{world.name}】")
        out_lines.append("")
        out_lines.append(f"共生成 {len(plots)} 个候选，骨架去重后选出前 {len(top)} 个。")
        out_lines.append("")
        for i, (plot, score) in enumerate(top, 1):
            out_lines.append(render(i, plot, score, world.name))
            out_lines.append("---")
        # 同时打印到控制台
        print(f"世界【{world.name}】: {len(plots)} 候选，已选出前 {len(top)} 个")

    out_path = Path(__file__).parent / "out" / "candidates.md"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\n已写入 UTF-8 结果：{out_path}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
