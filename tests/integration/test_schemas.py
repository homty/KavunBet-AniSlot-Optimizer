import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas import (
    MoveWeights,
    OptimizationSettings,
)


def test_valid_move_weights() -> None:
    moves = MoveWeights(
        within_reel=0.55,
        cross_reel=0.45,
        composition=0.0,
    )

    assert moves.within_reel == 0.55
    assert moves.cross_reel == 0.45
    assert moves.composition == 0.0


def test_move_weights_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        MoveWeights(
            within_reel=-0.1,
            cross_reel=0.5,
            composition=0.6,
        )


def test_move_weights_cannot_all_be_zero() -> None:
    with pytest.raises(ValidationError):
        MoveWeights(
            within_reel=0.0,
            cross_reel=0.0,
            composition=0.0,
        )


def test_iterations_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        OptimizationSettings(
            iterations=0,
            seed=42,
            start_temperature=0.2,
            end_temperature=0.0001,
            report_every=5000,
            moves=MoveWeights(
                within_reel=0.55,
                cross_reel=0.45,
                composition=0.0,
            ),
        )


def test_report_every_can_be_zero() -> None:
    settings = OptimizationSettings(
        iterations=50_000,
        seed=42,
        start_temperature=0.2,
        end_temperature=0.0001,
        report_every=0,
        moves=MoveWeights(
            within_reel=0.55,
            cross_reel=0.45,
            composition=0.0,
        ),
    )

    assert settings.report_every == 0
