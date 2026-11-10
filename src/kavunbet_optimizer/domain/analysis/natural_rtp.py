from collections.abc import Mapping

from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget


def group_natural_rtp_pct(
    target: GroupRtpTarget,
    expected_ways_matrix: dict[str, dict[int, float]],
    paytable: Mapping[tuple[int, str], float],
) -> float:
    natural_rtp_pct = 0.0
    for symbol in target.symbols:
        for kind in (3, 4, 5, 6):
            paytable_key = (kind, symbol)
            if paytable_key not in paytable:
                raise ValueError(f"missing paytable entry for {symbol} E{kind}")
            payout = float(paytable[paytable_key])
            if payout < 0:
                raise ValueError(f"paytable payout cannot be negative for {symbol} E{kind}")
            natural_rtp_pct += expected_ways_matrix[symbol][kind] * payout * 100.0
    return natural_rtp_pct
