from kavunbet_optimizer.domain.analysis.probability import (
    FixedProfiles,
    PresenceProfile,
    reel_presence,
)
from kavunbet_optimizer.domain.optimization_input import ReelSetComponent
from kavunbet_optimizer.domain.reel_set import ReelSet


def component_expected_exact_ways_matrix(
    reels: ReelSet,
    window_size: int,
    substitutes: tuple[str, ...],
    symbol: str,
    presence: tuple[float, ...] | None = None,
) -> dict[int, float]:
    accepted_symbols = {symbol, *substitutes}
    if presence is None:
        presence = tuple(
            reel_presence(reel, symbol, window_size, substitutes) for reel in reels.reels
        )

    # Each matching stop appears in exactly window_size cyclic windows.
    # Mean multiplicity determines the number of ways, while presence on
    # the following reel determines where the exact combination ends.
    mean_multiplicities = tuple(
        window_size * sum(stop in accepted_symbols for stop in reel) / len(reel)
        for reel in reels.reels
    )

    result = {}
    prefix_ways = 1.0
    for kind in range(1, reels.reel_count + 1):
        prefix_ways *= mean_multiplicities[kind - 1]
        if kind < 3:
            continue
        terminator_probability = 1.0 - presence[kind] if kind < reels.reel_count else 1.0
        result[kind] = prefix_ways * terminator_probability
    return result


def expected_ways_matrix(
    candidate: ReelSet,
    symbols: list[str],
    window_size: int,
    source_weight: float,
    source_substitutes: tuple[str, ...],
    fixed_components: tuple[ReelSetComponent, ...],
    fixed_profiles: FixedProfiles,
    candidate_profile: PresenceProfile,
) -> dict[str, dict[int, float]]:
    result = {}
    for symbol in symbols:
        source_ways = component_expected_exact_ways_matrix(
            candidate,
            window_size,
            source_substitutes,
            symbol,
            candidate_profile[symbol],
        )
        weighted = {kind: source_weight * source_ways[kind] for kind in (3, 4, 5, 6)}
        for component, (_, fixed_profile) in zip(
            fixed_components,
            fixed_profiles,
            strict=True,
        ):
            component_ways = component_expected_exact_ways_matrix(
                component.reels,
                window_size,
                component.substitutes,
                symbol,
                fixed_profile[symbol],
            )
            for kind in (3, 4, 5, 6):
                weighted[kind] += component.weight * component_ways[kind]
        result[symbol] = weighted
    return result
