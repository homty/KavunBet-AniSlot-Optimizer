import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas import GroupRtpTarget, GroupRtpTargetPatch


def test_valid_group_rtp_target() -> None:
    target = GroupRtpTarget(
        name="premium",
        symbols=["H1", "H2"],
        min_natural_rtp_pct=0.3,
        max_natural_rtp_pct=1.6,
        weight=9,
    )

    assert target.name == "premium"
    assert target.symbols == ["H1", "H2"]
    assert target.min_natural_rtp_pct == 0.3
    assert target.max_natural_rtp_pct == 1.6
    assert target.weight == 9


def test_valid_group_rtp_target_patch() -> None:
    patch = GroupRtpTargetPatch(
        symbols=["L1", "L2"],
        weight=4,
    )

    assert patch.symbols == ["L1", "L2"]
    assert patch.weight == 4
    assert patch.min_natural_rtp_pct is None


@pytest.mark.parametrize(
    "payload",
    [
        {"symbols": []},
        {"symbols": ["H1", "H1"]},
        {"min_natural_rtp_pct": 0},
        {"max_natural_rtp_pct": 0},
        {"weight": 0},
        {"unknown": 1},
    ],
)
def test_invalid_group_rtp_target_patch_is_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        GroupRtpTargetPatch(**payload)


def test_invalid_group_rtp_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GroupRtpTarget(
            name="premium",
            symbols=["H1", "H2"],
            min_natural_rtp_pct=2,
            max_natural_rtp_pct=1,
        )
