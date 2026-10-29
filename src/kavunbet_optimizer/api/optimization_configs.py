from typing import Literal

from fastapi import APIRouter, HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from kavunbet_optimizer.infrastructure.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.schemas.constraints import Constraints, ConstraintsPatch
from kavunbet_optimizer.schemas.expected_ways_targets import (
    ExpectedWaysTarget,
    ExpectedWaysTargetPatch,
)
from kavunbet_optimizer.schemas.group_rtp_targets import (
    GroupRtpTarget,
    GroupRtpTargetPatch,
)
from kavunbet_optimizer.schemas.objectives import (
    ObjectiveSettings,
    ObjectiveSettingsPatch,
)
from kavunbet_optimizer.schemas.optimization import (
    GameMode,
    OptimizationSettings,
    OptimizationSettingsPatch,
)
from kavunbet_optimizer.schemas.targets import (
    IntervalTarget,
    IntervalTargetPatch,
)

router = APIRouter(
    prefix="/optimization-configs",
    tags=["optimization-configs"],
)

config_repository = OptimizationConfigRepository()


@router.get("/{mode}/optimization", response_model=OptimizationSettings)
def get_optimization_settings(mode: GameMode) -> OptimizationSettings:
    return config_repository.get_optimization_settings(mode)


@router.patch("/{mode}/optimization", response_model=OptimizationSettings)
def patch_optimization_settings(
    mode: GameMode,
    patch: OptimizationSettingsPatch,
) -> OptimizationSettings:
    try:
        return config_repository.patch_optimization_settings(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/objective", response_model=ObjectiveSettings)
def get_objective_settings(mode: GameMode) -> ObjectiveSettings:
    return config_repository.get_objective_settings(mode)


@router.patch("/{mode}/objective", response_model=ObjectiveSettings)
def patch_objective_settings(
    mode: GameMode,
    patch: ObjectiveSettingsPatch,
) -> ObjectiveSettings:
    try:
        return config_repository.patch_objective_settings(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/targets", response_model=list[IntervalTarget])
def get_targets(mode: GameMode) -> list[IntervalTarget]:
    return config_repository.get_targets(mode)


@router.patch("/{mode}/targets/{symbol}/{kind}", response_model=IntervalTarget)
def patch_target(
    mode: GameMode,
    symbol: str,
    kind: Literal[3, 4, 5, 6],
    patch: IntervalTargetPatch,
) -> IntervalTarget:
    try:
        return config_repository.patch_target(mode, symbol, kind, patch)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.args[0],
        ) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/expected-ways-targets", response_model=list[ExpectedWaysTarget])
def get_expected_ways_targets(mode: GameMode) -> list[ExpectedWaysTarget]:
    return config_repository.get_expected_ways_targets(mode)


@router.patch("/{mode}/expected-ways-targets/{symbol}/{kind}", response_model=ExpectedWaysTarget)
def patch_expected_ways_target(
    mode: GameMode,
    symbol: str,
    kind: Literal[3, 4, 5, 6],
    patch: ExpectedWaysTargetPatch,
) -> ExpectedWaysTarget:
    try:
        return config_repository.patch_expected_ways_target(mode, symbol, kind, patch)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.args[0],
        ) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/group-rtp-targets", response_model=list[GroupRtpTarget])
def get_group_rtp_targets(mode: GameMode) -> list[GroupRtpTarget]:
    return config_repository.get_group_rtp_targets(mode)


@router.patch("/{mode}/group-rtp-targets/{name}", response_model=GroupRtpTarget)
def patch_group_rtp_target(
    mode: GameMode,
    name: str,
    patch: GroupRtpTargetPatch,
) -> GroupRtpTarget:
    try:
        return config_repository.patch_group_rtp_target(mode, name, patch)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.args[0],
        ) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/constraints", response_model=Constraints)
def get_constraints(mode: GameMode) -> Constraints:
    return config_repository.get_constraints(mode)


@router.patch("/{mode}/constraints", response_model=Constraints)
def patch_constraints(
    mode: GameMode,
    patch: ConstraintsPatch,
) -> Constraints:
    try:
        return config_repository.patch_constraints(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error
