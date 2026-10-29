import pytest
from pydantic import ValidationError

from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget, GroupRtpTargetPatch


def test_valid_group_target_rtp() -> None:
    target = GroupRtpTarget(
        name="symbols"
        symbols=["H1", "R2"]
        min_natural_rtp_pct=0.3
        max_natural_rtp_pct=1.6
        weight=9
    )
    assert target.name == "symbols"
    assert target.symbols == ["H1", "R2"]
    assert target.min_natural_rtp_pct == 0.3
    assert target.max_natural_rtp_pct == 1.6
    assert target.weight == 9