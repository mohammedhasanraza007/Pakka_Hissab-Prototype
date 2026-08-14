# Architecture

```text
Merchant
  ├── Typed command ─┐
  └── Browser speech ─┴──> deterministic intent parser
                              │
                              ▼
                      structured intent
                              │
                              ▼
                    deterministic workflow
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  Carts    Payments  Inventory
                    └─────────┼─────────┘
                              ▼
                            SQLite
                              ▼
                         Audit timeline
                              ▼
                           Dashboard
```

`backend/intent.py` converts supported English, Hindi, and Tamil command patterns into a small structured intent. It does not access SQLite or execute application actions.

`backend/workflow.py` validates the cart and payment state and performs SQLite-backed state transitions. Inventory is decremented only inside the successful payment-confirmation transaction.

`backend/db.py` owns the schema, deterministic synthetic seed, cart read model, inventory read model, transaction history, and audit events.

The browser microphone uses the browser Speech Recognition API. The selected UI language controls the browser recognition locale (`en-IN`, `hi-IN`, or `ta-IN`). Voice is optional; text mode and the local workflow remain available when speech recognition is unavailable.

Spoken feedback can use the `/api/tts` endpoint with `edge-tts` for English, Hindi, and Tamil. The frontend falls back to browser speech synthesis if that service is unavailable. No speech model weights are bundled or downloaded by the project.

All QR payloads are generated locally as `pakkahisaab://demo-payment/...` and are explicitly demo payloads. They are not UPI payment requests.
