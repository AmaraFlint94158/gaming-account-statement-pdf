from __future__ import annotations

import argparse
import json

from infrai_client import InfraiClient
from statement_service import PlayerAccount, export_statement


class DemoTransport:
    def __call__(self, request):
        class Response:
            status = 200

            def read(self):
                if request.full_url.endswith("timeseries"):
                    return b'{"ok": true, "data": {"minutes": 42}, "error": null, "metadata": {}}'
                return b'{"ok": true, "data": {"pdf": "generated"}, "error": null, "metadata": {}}'

        return Response()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    account = PlayerAccount("player-17", "Mina", ["castle-skin"], ["spring-arena"], ["asset-review"])
    client = InfraiClient(transport=None if args.live else DemoTransport())
    print(json.dumps(export_statement(account, client, "statement-player-17"), indent=2, default=str))


if __name__ == "__main__":
    main()
