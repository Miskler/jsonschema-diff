from pathlib import Path

from jsonschema_diff import ConfigMaker, JsonSchemaDiff


def test_catalog_stress_example_renders_complex_diff():
    base = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "source"
        / "basic"
        / "how_read_it"
        / "jsons"
    )
    text, comparators = JsonSchemaDiff.fast_pipeline(
        ConfigMaker.make(),
        str(base / "catalog.old.schema.json"),
        str(base / "catalog.new.schema.json"),
        None,
    )

    assert "r .$id: urn:test:catalog:v1 -> urn:test:catalog:v2" in text
    assert "m [\"paymentMethods\"].oneOf:" in text
    assert "patternProperties[\"^x-\"].type: string" in text
    assert "r [\"price\"].range: [0 ... 1000) -> (0 ... 1500)" in text
    assert "m .$defs[\"address\"]:" in text
    assert {c.__name__ for c in comparators} == {
        "Compare",
        "CompareList",
        "CompareRange",
    }
