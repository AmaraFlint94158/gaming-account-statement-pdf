from infrai_client import InfraiClient
from run_statement import DemoTransport
from statement_service import PlayerAccount, export_statement


def test_export_includes_moderation_and_shared_client_usage():
    account = PlayerAccount("p1", "Mina", ["skin"], ["arena"], ["review-7"])
    result = export_statement(account, InfraiClient(key="test-key", transport=DemoTransport()), "req-p1")
    assert "review-7" in result["markdown"]
    assert result["usage"]["data"]["minutes"] == 42
    assert result["pdf"]["data"]["pdf"] == "generated"
