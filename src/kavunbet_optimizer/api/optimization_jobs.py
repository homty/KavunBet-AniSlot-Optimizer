from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from kavunbet_optimizer.application.optimization_job_service import (
    OptimizationJobService,
)
from kavunbet_optimizer.domain.exceptions import OptimizationJobErrors
from kavunbet_optimizer.schemas.optimization_jobs import (
    OptimizationJobCreateRequest,
    OptimizationJobResponse,
)

router = APIRouter(
    prefix="/optimization-jobs",
    tags=["optimization-jobs"],
)


def get_optimization_job_service(request: Request) -> OptimizationJobService:
    return request.app.state.optimization_job_service


OptimizationJobServiceDependency = Annotated[
    OptimizationJobService,
    Depends(get_optimization_job_service),
]
IdempotencyKeyHeader = Annotated[
    str,
    Header(alias="Idempotency-Key", min_length=1),
]


@router.post("", response_model=OptimizationJobResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_optimization_job(
    request: OptimizationJobCreateRequest,
    idempotency_key: IdempotencyKeyHeader,
    service: OptimizationJobServiceDependency,
) -> OptimizationJobResponse:
    try:
        job = service.submit(
            project_id=request.project_id,
            engine_id=request.engine_id,
            game_mode=request.game_mode,
            idempotency_key=idempotency_key,
        )
    except OptimizationJobErrors.IdempotencyKeyConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return OptimizationJobResponse.model_validate(job, from_attributes=True)


@router.get("/{job_id}", response_model=OptimizationJobResponse)
def get_optimization_job(
    job_id: UUID, service: OptimizationJobServiceDependency
) -> OptimizationJobResponse:
    try:
        job = service.get_job(job_id)
    except OptimizationJobErrors.OptimizationJobNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return OptimizationJobResponse.model_validate(job, from_attributes=True)


@router.post(
    "/{job_id}/cancel", response_model=OptimizationJobResponse, status_code=status.HTTP_202_ACCEPTED
)
def request_optimization_job_cancellation(
    job_id: UUID, service: OptimizationJobServiceDependency
) -> OptimizationJobResponse:
    try:
        job = service.request_cancellation(job_id)
    except OptimizationJobErrors.OptimizationJobNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except OptimizationJobErrors.InvalidJobStatusTransitionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return OptimizationJobResponse.model_validate(job, from_attributes=True)
