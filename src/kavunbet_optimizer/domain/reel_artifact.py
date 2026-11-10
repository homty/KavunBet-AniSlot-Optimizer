from pydantic import BaseModel, ConfigDict, Field, field_validator


class StoredReelArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    storage_key: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    size_bytes: int = Field(gt=0)

    @field_validator("storage_key")
    @classmethod
    def validate_storage_key(cls, storage_key: str) -> str:
        if not storage_key.strip():
            raise ValueError("storage key cannot be blank")

        return storage_key
