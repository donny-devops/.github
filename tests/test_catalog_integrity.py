import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_service_skus_are_complete() -> None:
    data = json.loads((ROOT / "catalog" / "services.json").read_text(encoding="utf-8"))
    assert data["skus"], "catalog must not be empty"
    for sku in data["skus"]:
        assert sku["id"].startswith("mesh.")
        assert sku["price_usd"] > 0
        assert sku["repo"].startswith("https://github.com/donny-devops/")


def test_repo_catalog_does_not_advertise_missing_repos() -> None:
    text = (ROOT / "catalog" / "repos.yaml").read_text(encoding="utf-8")
    for missing in (
        "pqc-sdk",
        "jenkins-pipeline-library",
        "fastapi-starter-kit",
        "cloudflare-workers-templates",
    ):
        assert f"name: {missing}" not in text
