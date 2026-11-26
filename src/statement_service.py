from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient


@dataclass
class PlayerAccount:
    player_id: str
    display_name: str
    assets: list[str]
    live_events: list[str]
    moderation_queue: list[str]


def render_statement(account: PlayerAccount, usage: dict[str, Any]) -> str:
    if not account.assets and not account.live_events and not account.moderation_queue:
        raise ValueError("a statement needs at least one account activity")
    sections = [
        f"# Account statement: {account.display_name}",
        f"Player ID: {account.player_id}",
        "## Player-generated assets",
        *[f"- {item}" for item in sorted(account.assets)],
        "## Live events",
        *[f"- {item}" for item in sorted(account.live_events)],
        "## Moderation queue",
        *[f"- {item}" for item in sorted(account.moderation_queue)],
        "## Metered usage",
        f"- {usage.get('data', usage)}",
    ]
    return "\n".join(sections)


def export_statement(account: PlayerAccount, client: InfraiClient, request_id: str) -> dict[str, Any]:
    usage = client.usage_timeseries({"player_id": account.player_id})
    markdown = render_statement(account, usage)
    pdf = client.generate_pdf(markdown, request_id)
    return {"pdf": pdf, "usage": usage, "markdown": markdown}
