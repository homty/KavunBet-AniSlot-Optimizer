import math

from kavunbet_optimizer.domain.analysis.models import CombinationMetric
from kavunbet_optimizer.domain.reel_set import ReelSet

PresenceProfile = dict[str, tuple[float, ...]]
FixedProfiles = tuple[tuple[float, PresenceProfile], ...]


def reel_multiplicity(
    reel: list[str],
    symbol: str,
    window_size: int,
    substitutes: tuple[str, ...] = (),
) -> tuple[int, ...]:
    accepted_symbols = {symbol, *substitutes}
    reel_length = len(reel)

    return tuple(
        sum(
            reel[(start + offset) % reel_length] in accepted_symbols
            for offset in range(window_size)
        )
        for start in range(reel_length)
    )


def reel_presence(
    reel: list[str],
    symbol: str,
    window_size: int,
    substitutes: tuple[str, ...] = (),
) -> float:
    multiplicities = reel_multiplicity(reel, symbol, window_size, substitutes)
    covered_stops = sum(multiplicity > 0 for multiplicity in multiplicities)
    return covered_stops / len(multiplicities)


def presence_profile(
    reels: ReelSet,
    symbols: list[str],
    window_size: int,
    substitutes: tuple[str, ...] = (),
) -> PresenceProfile:
    return {
        symbol: tuple(reel_presence(reel, symbol, window_size, substitutes) for reel in reels.reels)
        for symbol in symbols
    }


def exact_from_presence(presence: tuple[float, ...], kind: int) -> float:
    probability = math.prod(presence[:kind])
    if kind < len(presence):
        probability *= 1.0 - presence[kind]
    return probability


def metric_from_profiles(
    candidate_profile: PresenceProfile,
    fixed_profiles: FixedProfiles,
    source_weight: float,
    symbol: str,
    kind: int,
) -> CombinationMetric:
    probability = source_weight * exact_from_presence(candidate_profile[symbol], kind)
    for weight, profile in fixed_profiles:
        probability += weight * exact_from_presence(profile[symbol], kind)
    return CombinationMetric(symbol=symbol, kind=kind, probability=probability)


def probability_matrix(
    candidate_profile: PresenceProfile,
    fixed_profiles: FixedProfiles,
    source_weight: float,
    symbols: list[str],
) -> dict[str, dict[int, CombinationMetric]]:
    return {
        symbol: {
            kind: metric_from_profiles(
                candidate_profile,
                fixed_profiles,
                source_weight,
                symbol,
                kind,
            )
            for kind in (3, 4, 5, 6)
        }
        for symbol in symbols
    }
