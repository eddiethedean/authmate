from examples.report_consumer import build_app
from fastapi.testclient import TestClient


def test_report_example_keeps_resource_lookup_in_host_dependency() -> None:
    with TestClient(build_app()) as client:
        allowed = client.get("/reports/11111111-1111-1111-1111-111111111111")
        unknown = client.get("/reports/00000000-0000-0000-0000-000000000000")
    assert allowed.status_code == 200
    assert unknown.status_code == 404
