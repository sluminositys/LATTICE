from lattice.graph_health import MemoryHealthCompiler
from lattice.schemas import GraphPatch, Provenance


def test_memory_health_compiler_skips_empty_patch_set() -> None:
    report = MemoryHealthCompiler().compile([])

    assert report.status == "skipped"
    assert report.materialized_l1 is False


def test_memory_health_compiler_reports_compiled_l0_patches() -> None:
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        provenance=Provenance(source_type="test"),
    )

    report = MemoryHealthCompiler().compile([patch])

    assert report.status == "completed"
    assert report.compiled_patch_ids == ["patch-1"]
    assert report.materialized_l1 is True
