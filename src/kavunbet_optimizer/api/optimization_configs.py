from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from kavunbet_optimizer.domain.config_repository import OptimizationConfigRepository
from kavunbet_optimizer.domain.exceptions import (
    ConfigResourceAlreadyExistsError,
    ConfigResourceIdentityMismatchError,
    ConfigResourceNotFoundError,
)
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

TargetKindPath = Annotated[int, Path(ge=3, le=6)]


def get_config_repository(request: Request) -> OptimizationConfigRepository:
    return request.app.state.config_repository


ConfigRepositoryDependency = Annotated[
    OptimizationConfigRepository,
    Depends(get_config_repository),
]


def resource_not_found(error: ConfigResourceNotFoundError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(error),
    )


def resource_conflict(
    error: ConfigResourceAlreadyExistsError | ConfigResourceIdentityMismatchError,
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(error),
    )


@router.get("/{mode}/optimization", response_model=OptimizationSettings)
def get_optimization_settings(
    mode: GameMode,
    repository: ConfigRepositoryDependency,
) -> OptimizationSettings:
    return repository.get_optimization_settings(mode)


@router.patch("/{mode}/optimization", response_model=OptimizationSettings)
def patch_optimization_settings(
    mode: GameMode,
    patch: OptimizationSettingsPatch,
    repository: ConfigRepositoryDependency,
) -> OptimizationSettings:
    try:
        return repository.patch_optimization_settings(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/objective", response_model=ObjectiveSettings)
def get_objective_settings(
    mode: GameMode,
    repository: ConfigRepositoryDependency,
) -> ObjectiveSettings:
    return repository.get_objective_settings(mode)


@router.patch("/{mode}/objective", response_model=ObjectiveSettings)
def patch_objective_settings(
    mode: GameMode,
    patch: ObjectiveSettingsPatch,
    repository: ConfigRepositoryDependency,
) -> ObjectiveSettings:
    try:
        return repository.patch_objective_settings(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.get("/{mode}/targets", response_model=list[IntervalTarget])
def get_targets(
    mode: GameMode,
    repository: ConfigRepositoryDependency,
) -> list[IntervalTarget]:
    return repository.get_targets(mode)


@router.post(
    "/{mode}/targets",
    response_model=IntervalTarget,
    status_code=status.HTTP_201_CREATED,
)
def add_target(
    mode: GameMode,
    target: IntervalTarget,
    repository: ConfigRepositoryDependency,
) -> IntervalTarget:
    try:
        return repository.add_target(mode, target)
    except ConfigResourceAlreadyExistsError as error:
        raise resource_conflict(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.put("/{mode}/targets/{symbol}/{kind}", response_model=IntervalTarget)
def replace_target(
    mode: GameMode,
    symbol: str,
    kind: TargetKindPath,
    target: IntervalTarget,
    repository: ConfigRepositoryDependency,
) -> IntervalTarget:
    try:
        return repository.replace_target(mode, symbol, kind, target)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error
    except ConfigResourceIdentityMismatchError as error:
        raise resource_conflict(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.patch("/{mode}/targets/{symbol}/{kind}", response_model=IntervalTarget)
def patch_target(
    mode: GameMode,
    symbol: str,
    kind: TargetKindPath,
    patch: IntervalTargetPatch,
    repository: ConfigRepositoryDependency,
) -> IntervalTarget:
    try:
        return repository.patch_target(mode, symbol, kind, patch)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.delete(
    "/{mode}/targets/{symbol}/{kind}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_target(
    mode: GameMode,
    symbol: str,
    kind: TargetKindPath,
    repository: ConfigRepositoryDependency,
) -> None:
    try:
        repository.delete_target(mode, symbol, kind)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error


@router.get("/{mode}/expected-ways-targets", response_model=list[ExpectedWaysTarget])
def get_expected_ways_targets(
    mode: GameMode,
    repository: ConfigRepositoryDependency,
) -> list[ExpectedWaysTarget]:
    return repository.get_expected_ways_targets(mode)


@router.post(
    "/{mode}/expected-ways-targets",
    response_model=ExpectedWaysTarget,
    status_code=status.HTTP_201_CREATED,
)
def add_expected_ways_target(
    mode: GameMode,
    target: ExpectedWaysTarget,
    repository: ConfigRepositoryDependency,
) -> ExpectedWaysTarget:
    try:
        return repository.add_expected_ways_target(mode, target)
    except ConfigResourceAlreadyExistsError as error:
        raise resource_conflict(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.put(
    "/{mode}/expected-ways-targets/{symbol}/{kind}",
    response_model=ExpectedWaysTarget,
)
def replace_expected_ways_target(
    mode: GameMode,
    symbol: str,
    kind: TargetKindPath,
    target: ExpectedWaysTarget,
    repository: ConfigRepositoryDependency,
) -> ExpectedWaysTarget:
    try:
        return repository.replace_expected_ways_target(mode, symbol, kind, target)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error
    except ConfigResourceIdentityMismatchError as error:
        raise resource_conflict(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.patch("/{mode}/expected-ways-targets/{symbol}/{kind}", response_model=ExpectedWaysTarget)
def patch_expected_ways_target(
    mode: GameMode,
    symbol: str,
    kind: TargetKindPath,
    patch: ExpectedWaysTargetPatch,
    repository: ConfigRepositoryDependency,
) -> ExpectedWaysTarget:
    try:
        return repository.patch_expected_ways_target(mode, symbol, kind, patch)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.delete(
    "/{mode}/expected-ways-targets/{symbol}/{kind}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expected_ways_target(
    mode: GameMode,
    symbol: str,
    kind: TargetKindPath,
    repository: ConfigRepositoryDependency,
) -> None:
    try:
        repository.delete_expected_ways_target(mode, symbol, kind)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error


@router.get("/{mode}/group-rtp-targets", response_model=list[GroupRtpTarget])
def get_group_rtp_targets(
    mode: GameMode,
    repository: ConfigRepositoryDependency,
) -> list[GroupRtpTarget]:
    return repository.get_group_rtp_targets(mode)


@router.post(
    "/{mode}/group-rtp-targets",
    response_model=GroupRtpTarget,
    status_code=status.HTTP_201_CREATED,
)
def add_group_rtp_target(
    mode: GameMode,
    target: GroupRtpTarget,
    repository: ConfigRepositoryDependency,
) -> GroupRtpTarget:
    try:
        return repository.add_group_rtp_target(mode, target)
    except ConfigResourceAlreadyExistsError as error:
        raise resource_conflict(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.put("/{mode}/group-rtp-targets/{name}", response_model=GroupRtpTarget)
def replace_group_rtp_target(
    mode: GameMode,
    name: str,
    target: GroupRtpTarget,
    repository: ConfigRepositoryDependency,
) -> GroupRtpTarget:
    try:
        return repository.replace_group_rtp_target(mode, name, target)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error
    except ConfigResourceIdentityMismatchError as error:
        raise resource_conflict(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.patch("/{mode}/group-rtp-targets/{name}", response_model=GroupRtpTarget)
def patch_group_rtp_target(
    mode: GameMode,
    name: str,
    patch: GroupRtpTargetPatch,
    repository: ConfigRepositoryDependency,
) -> GroupRtpTarget:
    try:
        return repository.patch_group_rtp_target(mode, name, patch)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error


@router.delete(
    "/{mode}/group-rtp-targets/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_group_rtp_target(
    mode: GameMode,
    name: str,
    repository: ConfigRepositoryDependency,
) -> None:
    try:
        repository.delete_group_rtp_target(mode, name)
    except ConfigResourceNotFoundError as error:
        raise resource_not_found(error) from error


@router.get("/{mode}/constraints", response_model=Constraints)
def get_constraints(
    mode: GameMode,
    repository: ConfigRepositoryDependency,
) -> Constraints:
    return repository.get_constraints(mode)


@router.patch("/{mode}/constraints", response_model=Constraints)
def patch_constraints(
    mode: GameMode,
    patch: ConstraintsPatch,
    repository: ConfigRepositoryDependency,
) -> Constraints:
    try:
        return repository.patch_constraints(mode, patch)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors) from error
