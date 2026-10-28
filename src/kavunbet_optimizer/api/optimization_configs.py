from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from kavunbet_optimizer.infrastructure.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.schemas.constraints import Constraints, ConstraintsPatch
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
from kavunbet_optimizer.schemas.expected_ways_targets import (
    ExpectedWaysTarget,
    ExpectedWaysTargetPatch,
)
from kavunbet_optimizer.schemas.group_rtp_targets import (
    GroupRtpTarget,
    GroupRtpTargetPatch
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

@router.get("/{mode}/targets")
def get_targets_settings(mode: GameMode) -> IntervalTarget:
    return config_repository.get_targets(mode)

@router.patch("/{mode}/target/{symbol}/{value}") 
def patch_targets_settings(
    mode: GameMode,
    patch: IntervalTargetPatch,
) -> IntervalTargetPatch:
    try:
        return config_repository.patch_target(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error
"""
@router.delete("/{mode}/target/{symbol}/{value}")
def delete_target_settings(mode: GameMode) -> IntervalTarget:
    return 
"""

@router.get("/{mode}/expected_ways")
def get_expected_ways(mode: GameMode) -> ExpectedWaysTarget:
    return config_repository.get_expected_ways_targets(mode)

@router.patch("/{model}/expected_ways/{symbol}/{value}")
def patch_expected_ways(
    mode: GameMode,
    patch: ExpectedWaysTargetPatch
) -> ExpectedWaysTarget:
    try:
        return config_repository.patch_expected_ways_targets(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error

@router.get("/{model}/grouped_rtp")
def get_group_rtp_targets(mode: GameMode) -> GroupRtpTarget:
    return config_repository.get_group_rtp_targets(mode)

@router.patch("/{model}/grouped_rtp/{symbols}")
def patch_grouped_rtp(
    mode: GameMode,
    patch: GroupRtpTargetPatch,
) -> GroupRtpTarget:
    try:
        return config_repository.patch_group_rtp_target(mode, patch)
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
