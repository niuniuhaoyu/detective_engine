"""地基自检 —— 用标准库 unittest，无需额外依赖。

运行：
    cd detective_engine
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from detective import constraints, generator, scorer  # noqa: E402
from detective.element_library import DECOYS, WORLDS  # noqa: E402
from detective.model import Plot, Trace, TraceKind, Trajectory  # noqa: E402
from detective.trick_library import ALL_TRICKS, BY_ID  # noqa: E402

WORLD = WORLDS[0]


# ---------------------------------------------------------------------------
# 手工构造 Plot 的小工具（用于精确测试评分行为）
# ---------------------------------------------------------------------------
def _plot(killer: str, trick_ids: list[str], presented: list[Trace]) -> Plot:
    traj = Trajectory(
        killer=killer, motive="m", weapon="w", location="l", time_window="t",
        tricks=[BY_ID[i] for i in trick_ids],
    )
    return Plot(trajectory=traj, presented=list(presented))


def _true(tid: str, links: tuple[str, ...]) -> Trace:
    return Trace(id=tid, text=tid, kind=TraceKind.TRUE_TELL, truth_link=links)


def _false(tid: str, at: str) -> Trace:
    return Trace(id=tid, text=tid, kind=TraceKind.FALSE_LEAD, points_at=at)


# ---------------------------------------------------------------------------
# 库完整性
# ---------------------------------------------------------------------------
class TestLibraryIntegrity(unittest.TestCase):
    def test_every_trick_is_usable_in_some_world(self):
        all_facts = frozenset().union(*(w.facts for w in WORLDS))
        for t in ALL_TRICKS:
            self.assertTrue(
                t.premises <= all_facts,
                f"诡计 {t.id} 的前提在任何世界都无法满足：{t.premises - all_facts}",
            )

    def test_every_trick_has_a_signature_tell(self):
        for t in ALL_TRICKS:
            tells = [x for x in t.traces if x.kind is TraceKind.TRUE_TELL]
            self.assertTrue(tells, f"诡计 {t.id} 缺少签名真线索")
            self.assertTrue(
                any(t.id in x.truth_link for x in tells),
                f"诡计 {t.id} 的签名线索没有指回自己",
            )

    def test_ids_unique(self):
        ids = [t.id for t in ALL_TRICKS] + [d.id for d in DECOYS]
        self.assertEqual(len(ids), len(set(ids)), "存在重复 id")


# ---------------------------------------------------------------------------
# 生成器 + 评分器（集成）
# ---------------------------------------------------------------------------
class TestGeneratorAndScorer(unittest.TestCase):
    def test_premises_respected(self):
        for w in WORLDS:
            for p in generator.generate_candidates(w, n=30, seed=1):
                for t in p.trajectory.tricks:
                    self.assertTrue(constraints.premises_ok(t, w))

    def test_no_conflicting_tricks(self):
        for w in WORLDS:
            for p in generator.generate_candidates(w, n=30, seed=2):
                self.assertFalse(constraints.has_conflict(p.trajectory.tricks))

    def test_scores_in_range(self):
        fields = ("fair_play", "unique_solution", "surprise", "economy",
                  "coherence", "timing", "diversity", "ingenuity", "total")
        for w in WORLDS:
            for p in generator.generate_candidates(w, n=30, seed=3):
                s = scorer.score_plot(p, w)
                for f in fields:
                    v = getattr(s, f)
                    self.assertGreaterEqual(v, 0.0)
                    self.assertLessEqual(v, 1.0 + 1e-9, f"{f}={v}")

    def test_ingenuity_is_three_factor_product(self):
        for w in WORLDS:
            for p in generator.generate_candidates(w, n=20, seed=4):
                s = scorer.score_plot(p, w)
                self.assertAlmostEqual(
                    s.ingenuity, s.fair_play * s.unique_solution * s.surprise, places=9
                )

    def test_deterministic_with_seed(self):
        a = generator.generate_candidates(WORLD, n=50, seed=42)
        b = generator.generate_candidates(WORLD, n=50, seed=42)
        self.assertEqual(len(a), len(b))
        for pa, pb in zip(a, b):
            self.assertEqual(pa.trajectory.killer, pb.trajectory.killer)
            self.assertEqual([t.id for t in pa.presented], [t.id for t in pb.presented])

    def test_ranked_are_fair_when_possible(self):
        plots = generator.generate_candidates(WORLD, n=300, seed=7)
        best_plot, _ = generator.rank(plots, WORLD, top=1)[0]
        ok, missing = constraints.fair_play(best_plot)
        self.assertTrue(ok, f"头名竟然不公平，缺失：{missing}")

    def test_rank_suppresses_clones(self):
        plots = generator.generate_candidates(WORLD, n=400, seed=2026)
        top = generator.rank(plots, WORLD, top=8)
        sigs = [generator.plot_signature(p) for p, _ in top]
        self.assertEqual(len(sigs), len(set(sigs)), "rank 输出了骨架重复的克隆")


# ---------------------------------------------------------------------------
# 重构后的评分行为：真的能区分"精妙"
# ---------------------------------------------------------------------------
class TestScorerBehaviour(unittest.TestCase):
    def test_piling_herrings_on_one_suspect_breaks_uniqueness(self):
        piled = _plot("真凶", ["ice_timer"],
                      [_false("d1", "A"), _false("d2", "A"), _false("d3", "A")])
        spread = _plot("真凶", ["ice_timer"],
                       [_false("d1", "A"), _false("d2", "B"), _false("d3", "C")])
        self.assertLess(
            scorer.score_plot(piled, WORLD).unique_solution,
            scorer.score_plot(spread, WORLD).unique_solution,
        )

    def test_surprise_is_non_monotonic(self):
        """惊异不是越多越好：塞太多红鲱鱼会因拥挤而被惩罚。"""
        few = _plot("真凶", ["ice_timer"], [_false("d1", "A"), _false("d2", "B")])
        overloaded = _plot(
            "真凶", ["ice_timer", "key_return", "self_lock"],
            [_false("d1", "A"), _false("d2", "B"), _false("d3", "C")],
        )
        self.assertGreater(
            scorer.score_plot(few, WORLD).surprise,
            scorer.score_plot(overloaded, WORLD).surprise,
        )

    def test_early_decoys_beat_late_decoys_on_timing(self):
        early = _plot("真凶", ["ice_timer"],
                      [_false("d1", "A"), _false("d2", "B"), _true("t1", ("killer",)), _true("t2", ("weapon",))])
        late = _plot("真凶", ["ice_timer"],
                     [_true("t1", ("killer",)), _true("t2", ("weapon",)), _false("d1", "A"), _false("d2", "B")])
        self.assertGreater(
            scorer.score_plot(early, WORLD).timing,
            scorer.score_plot(late, WORLD).timing,
        )

    def test_stacking_same_category_tricks_is_cliche(self):
        stacked = _plot("真凶", ["ice_timer", "key_return", "self_lock"], [])  # 三个都是"密室"
        varied = _plot("真凶", ["ice_timer", "clock_tamper", "forged_note"], [])
        self.assertLess(
            scorer.score_plot(stacked, WORLD).diversity,
            scorer.score_plot(varied, WORLD).diversity,
        )

    def test_dropping_a_tell_lowers_fair_play(self):
        full = _plot("真凶", ["ice_timer"],
                     [_true("k", ("killer",)), _true("w", ("weapon",)),
                      _true("m", ("motive",)), _true("i", ("ice_timer",))])
        broken = _plot("真凶", ["ice_timer"],
                       [_true("k", ("killer",)), _true("w", ("weapon",)), _true("m", ("motive",))])
        self.assertLess(
            scorer.score_plot(broken, WORLD).fair_play,
            scorer.score_plot(full, WORLD).fair_play,
        )


if __name__ == "__main__":
    unittest.main()
