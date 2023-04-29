from pathlib import Path
from pydantic import BaseModel


class HashedFile(BaseModel):
    file_path: Path
    file_hash: str
    hash_method: str

    @classmethod
    def factory(cls, file_path: Path, file_hash: str, hash_method: str) -> "HashedFile":
        return cls(file_path=file_path, file_hash=file_hash, hash_method=hash_method)
