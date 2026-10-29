from kavunbet_optimizer.schemas.configuration import OptimizationConfig
from kavunbet_optimizer.schemas.constraints import Constraints
from kavunbet_optimizer.schemas.expected_ways_targets import ExpectedWaysTarget
from kavunbet_optimizer.schemas.group_rtp_targets import GroupRtpTarget
from kavunbet_optimizer.schemas.objectives import ObjectiveSettings
from kavunbet_optimizer.schemas.optimization import (
    GameMode,
    MoveWeights,
    OptimizationSettings,
)
from kavunbet_optimizer.schemas.targets import IntervalTarget

DEFAULT_SYMBOLS = ["H1", "H2", "H3", "H4", "H5", "L1", "L2", "L3", "L4", "L5", "L6"]


def create_default_optimization_settings() -> dict[GameMode, OptimizationSettings]:
    return {
        GameMode.BASE: OptimizationSettings(
            iterations=50_000,
            seed=42,
            start_temperature=0.2,
            end_temperature=0.0001,
            report_every=5_000,
            moves=MoveWeights(
                within_reel=0.55,
                cross_reel=0.45,
                composition=0.0,
            ),
        ),
        GameMode.FREE: OptimizationSettings(
            iterations=50_000,
            seed=42,
            start_temperature=0.2,
            end_temperature=0.0001,
            report_every=5_000,
            moves=MoveWeights(
                within_reel=0.15,
                cross_reel=0.10,
                composition=0.75,
            ),
        ),
    }


def create_default_objectives() -> dict[GameMode, ObjectiveSettings]:
    return {
        GameMode.BASE: ObjectiveSettings(
            progression_weight=1.0,
            symbol_order_weight=1.0,
            preserve_untargeted_weight=0.25,
            preserve_untargeted_tolerance=0.20,
            preserve_untargeted_ways_weight=4.0,
            preserve_untargeted_ways_tolerance=0.10,
            frequency_orders=[
                ["H1", "H2", "H3", "H4", "H5"],
            ],
        ),
        GameMode.FREE: ObjectiveSettings(
            progression_weight=1.0,
            symbol_order_weight=1.0,
            preserve_untargeted_weight=0.0,
            preserve_untargeted_tolerance=0.20,
            preserve_untargeted_ways_weight=0.0,
            preserve_untargeted_ways_tolerance=0.10,
            frequency_orders=[
                ["H1", "H2", "H3", "H4", "H5"],
            ],
        ),
    }


def create_default_targets() -> dict[GameMode, list[IntervalTarget]]:
    return {
        GameMode.BASE: [
            IntervalTarget(
                symbol="H1",
                kind=3,
                min_interval=25,
                max_interval=35,
                weight=4.0,
            ),
            IntervalTarget(
                symbol="H2",
                kind=3,
                min_interval=38,
                max_interval=48,
                weight=4.0,
            ),
            IntervalTarget(
                symbol="H3",
                kind=3,
                min_interval=90,
                max_interval=110,
                weight=4.0,
            ),
            IntervalTarget(
                symbol="L1",
                kind=6,
                min_interval=90,
                max_interval=100,
                weight=4.0,
            ),
            IntervalTarget(
                symbol="L2",
                kind=6,
                min_interval=28,
                max_interval=35,
                weight=4.0,
            ),
            IntervalTarget(
                symbol="L3",
                kind=6,
                min_interval=55,
                max_interval=70,
                weight=4.0,
            ),
        ],
        # Have their own grouped RTP targets.
        # TODO: Must redesign optimizer logic.
        GameMode.FREE: [],
    }


def create_default_expected_ways_targets() -> dict[GameMode, list[ExpectedWaysTarget]]:
    return {
        GameMode.BASE: [
            ExpectedWaysTarget(
                symbol="L1",
                kind=5,
                min_ways=2.15,
                max_ways=2.30,
                weight=16.0,
            ),
            ExpectedWaysTarget(
                symbol="L2",
                kind=6,
                min_ways=1.02,
                max_ways=1.12,
                weight=16.0,
            ),
        ],
        # Have their own grouped RTP targets.
        # TODO: Must redesign optimizer logic.
        GameMode.FREE: [],
    }


def create_default_group_rtp_targets() -> dict[GameMode, list[GroupRtpTarget]]:
    return {
        GameMode.BASE: [],
        GameMode.FREE: [
            GroupRtpTarget(
                name="default",
                symbols=[
                    "L1",
                    "L2",
                    "L3",
                    "L4",
                    "L5",
                    "L6",
                ],
                min_natural_rtp_pct=10.5,
                max_natural_rtp_pct=11.5,
                weight=8.0,
            ),
            GroupRtpTarget(
                name="premium",
                symbols=[
                    "H1",
                    "H2",
                    "H3",
                    "H4",
                    "H5",
                ],
                min_natural_rtp_pct=11.8,
                max_natural_rtp_pct=12.8,
                weight=8.0,
            ),
        ],
    }


def create_default_constraints() -> dict[GameMode, Constraints]:
    return {
        GameMode.BASE: Constraints(
            last_allowed_reel={"H4": 3, "H5": 2},
            max_consecutive={},
            global_count_ranges={},
            composition_symbols=["L1", "L2", "L3", "L4", "L5", "L6"],
        ),
        GameMode.FREE: Constraints(
            last_allowed_reel={"H4": 3, "H5": 2},
            max_consecutive={},
            global_count_ranges={},
            composition_symbols=[
                "L1",
                "L2",
                "L3",
                "L4",
                "L5",
                "L6",
                "H1",
                "H2",
                "H3",
            ],
        ),
    }


def create_default_configs() -> dict[GameMode, OptimizationConfig]:
    optimization = create_default_optimization_settings()
    objectives = create_default_objectives()
    targets = create_default_targets()
    expected_ways_targets = create_default_expected_ways_targets()
    group_rtp_targets = create_default_group_rtp_targets()
    constraints = create_default_constraints()

    return {
        mode: OptimizationConfig(
            symbols=DEFAULT_SYMBOLS,
            optimization=optimization[mode],
            objective=objectives[mode],
            targets=targets[mode],
            expected_ways_targets=expected_ways_targets[mode],
            group_rtp_targets=group_rtp_targets[mode],
            constraints=constraints[mode],
        )
        for mode in GameMode
    }
