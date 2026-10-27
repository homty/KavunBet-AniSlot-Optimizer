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
