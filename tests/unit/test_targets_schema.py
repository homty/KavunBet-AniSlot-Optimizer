from kavunbet_optimizer.schemas.targets import IntervalTarget, IntervalTargetPatch


def test_valid_interval() -> None:
    target = IntervalTarget(
        symbol="H1",
        kind=3,
        min_interval=25,
        max_interval=35,
        weight=4.0,
    )
    assert target.min_interval == 25
    assert target.max_interval == 35


def test_valid_interval_target_patch() -> None:
    patch = IntervalTargetPatch(weight=2)

    assert patch.weight == 2.0
    assert patch.model_dump(exclude_unset=True) == {
        "weight": 2.0,
    }
