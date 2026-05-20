from pydantic import ValidationError
import pytest

from helix.schemas.common import Provenance


def test_schema_models_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Provenance(source_type="architecture", unexpected=True)


def test_provenance_requires_source_type() -> None:
    provenance = Provenance(source_type="architecture", source_path="E:/donwloads/HELIX_architecture_v7.md")

    assert provenance.source_type == "architecture"
    assert provenance.source_path == "E:/donwloads/HELIX_architecture_v7.md"
