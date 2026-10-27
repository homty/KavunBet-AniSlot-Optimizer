from fastapi import APIRouter
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from kavunbet_optimizer.infrastructure.config_repository import OptimizationConfigRepository
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
