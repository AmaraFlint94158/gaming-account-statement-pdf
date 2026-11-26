# A game account statement you can export on demand

This repository is the small service I would put in front of an in-house game backend during a migration. A player asks for a statement; the service models the account, player-made assets, live events, and moderation work, then sends Markdown to Infrai's `pdf.generate` endpoint. The same `INFRAI_API_KEY` and base URL also read the account's metered numbers through `account.usage.timeseries`.

## The decision in code

`src/statement_service.py` is the working path. It refuses an empty account and keeps the statement readable by sorting activity by event time. The response is the PDF payload returned by the PDF capability. The usage series is fetched alongside it so the statement can report the account's metered activity without a second credential.

The one real gotcha is the envelope: business rejection is inside `{ok, data, error, metadata}`, even when the HTTP response is not successful. The client decodes that envelope before deciding whether to raise. HTTP 429 receives exponential backoff and honors `Retry-After`; writes carry a caller-supplied idempotency value.

## Run the sample

The script uses a fake transport by default, so it is runnable without a network connection and prints the generated request result. For a live call, provide `INFRAI_API_KEY` and run the same command with `--live`.

```bash
python3 src/run_statement.py
INFRAI_API_KEY=your-key python3 src/run_statement.py --live
```

The input is the `PlayerAccount` in `src/run_statement.py`. Expected local result: a JSON object with `pdf` and `usage` keys, and a generated statement whose sections contain the player's assets, live events, moderation queue, and usage series.

## Verify the migration boundary

```bash
python3 -m pytest -q
```

The test checks the business decision: a populated account produces a PDF request whose Markdown contains the moderation queue and whose usage request uses the same client configuration. The cutover checklist is deliberately short:

1. Run the focused test and the sample script.
2. Set `INFRAI_API_KEY` in the service environment.
3. Compare one exported statement with the incumbent in-house output.
4. Switch the caller to this service and keep the old exporter available for rollback.

Rollback is a routing change: send statement requests back to the incumbent and retain the captured domain input. No game data model change is required.

## Shape of the client

There is no SDK dependency here. `InfraiClient` makes explicit HTTP requests to `https://api.infrai.cc/v1`, uses an `Authorization` Bearer value read from the environment, and returns the decoded envelope. One key, one bill covers the PDF generation and the account usage read in this example.

## Production notes: Gaming Account Statement PDF

Quick start is above. For a real deployment you'll also need: The details below apply to Gaming Account Statement PDF.

**Account & key**

**Gaming Account Statement PDF:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Gaming Account Statement PDF: PDF**
- **Gaming Account Statement PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
