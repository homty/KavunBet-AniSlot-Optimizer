import random

from kavunbet_optimizer.domain.optimization import CandidateMutator
from kavunbet_optimizer.domain.reel_set import ReelSet
from kavunbet_optimizer.schemas.optimization import MoveWeights


def test_within_reel_move_preserves_symbol_counts() -> None:
    candidate = ReelSet([["A", "B"] for _ in range(6)])
    original_reels = candidate.copy().reels
    original_counts = candidate.counts()
    mutator = CandidateMutator(
        MoveWeights(within_reel=1.0, cross_reel=0.0, composition=0.0),
        composition_symbols=[],
        random_source=random.Random(1),
    )

    changed = mutator.mutate(candidate)

    assert changed
    assert candidate.counts() == original_counts
    assert candidate.reels != original_reels


def test_cross_reel_move_preserves_global_symbol_counts() -> None:
    candidate = ReelSet([[f"S{reel_index}", f"S{reel_index}"] for reel_index in range(6)])
    original_reels = candidate.copy().reels
    original_counts = candidate.counts()
    mutator = CandidateMutator(
        MoveWeights(within_reel=0.0, cross_reel=1.0, composition=0.0),
        composition_symbols=[],
        random_source=random.Random(2),
    )

    changed = mutator.mutate(candidate)

    assert changed
    assert candidate.counts() == original_counts
    assert candidate.reels != original_reels


def test_composition_move_changes_an_allowed_symbol() -> None:
    candidate = ReelSet([["A", "X"] for _ in range(6)])
    original_a_count = candidate.counts()["A"]
    mutator = CandidateMutator(
        MoveWeights(within_reel=0.0, cross_reel=0.0, composition=1.0),
        composition_symbols=["A", "B"],
        random_source=random.Random(3),
    )

    changed = mutator.mutate(candidate)

    assert changed
    assert candidate.counts()["A"] == original_a_count - 1
    assert candidate.counts()["B"] == 1


def test_composition_move_requires_two_allowed_symbols() -> None:
    candidate = ReelSet([["A", "X"] for _ in range(6)])
    mutator = CandidateMutator(
        MoveWeights(within_reel=0.0, cross_reel=0.0, composition=1.0),
        composition_symbols=["A"],
        random_source=random.Random(4),
    )

    assert not mutator.mutate(candidate)
