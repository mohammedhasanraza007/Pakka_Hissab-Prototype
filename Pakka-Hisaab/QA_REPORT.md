# QA Report

Audit date: 2026-08-14

This report records only checks actually executed in the available audit environment. Windows-only launcher behavior, physical microphone capture, and live external TTS service availability were not marked as passed because they could not be executed here.

| Test | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Repository extracted and recursively inspected | PASS | ZIP extracted and every project file inspected | Source, scripts, docs, tests, frontend, backend, and configuration reviewed. |
| `run.bat` statically inspected | PASS | Launcher and `build.bat` reviewed | The launcher calls `build.bat`, starts FastAPI, health-checks it, opens the browser, and keeps the console open. |
| Windows `run.bat` actually executed | NOT VERIFIED | No Windows runtime available in the audit environment | Must be verified on a clean Windows machine. |
| Fixed Python version in Windows launcher | PASS (static) | `build.bat` pins Python `3.11.9` | Actual Windows installer execution was not available here. |
| Dependency installation from `requirements.txt` | NOT VERIFIED | Temporary clean venv install was attempted, but the audit environment had no package-network access | Requirements are pinned; actual first-run installation must be tested on Windows with network access. |
| Python syntax/import compilation | PASS | `python -m compileall -q backend` | No compilation errors. |
| Automated workflow tests | PASS | `python -m pytest -q` → 12 passed | Tests cover intent, carts, payments, inventory, reset, duplicate payment, and persistence. |
| JavaScript syntax | PASS | `node --check frontend/app.js` | No syntax errors. Node is not required by the application; it was used only for this audit check. |
| Backend startup | PASS | FastAPI started on local port 8767 | Application startup completed successfully. |
| `/api/health` | PASS | HTTP 200 | Reported SQLite and browser/optional edge-tts voice stack. |
| Frontend served by backend | PASS | `/` returned HTTP 200 | No separate frontend server is used. |
| Database initialization | PASS | Fresh runtime created SQLite data and returned state | SQLite is initialized by the backend. |
| Five carts / ten products seed | PASS | Fresh seed assertions | Cart count = 5; product count = 10. |
| Cart 1 total | PASS | SQLite assertion | ₹299. |
| Cart 2 total | PASS | SQLite assertion | ₹217. |
| Natural-language English paraphrase | PASS | Parser assertion | First-customer UPI paraphrase resolves to Cart 1 + UPI. |
| Hindi command parsing | PASS | Parser assertion | `कार्ट एक को यूपीआई से क्लियर करो` resolves to Cart 1 + UPI. |
| Tamil command parsing | PASS | Parser assertion | `கார்ட் 1-ன் கட்டணத்தை UPI மூலம் செலுத்துங்கள்.` resolves to Cart 1 + UPI. |
| Cart 1 success state transition | PASS | Direct workflow test + HTTP checkout | Pending → paid; inventory decremented; reconciliation transaction created. |
| Cart 2 failure state transition | PASS | Direct workflow test | Payment failed; order not paid; inventory unchanged. |
| Duplicate payment protection | PASS | Direct workflow test | Second confirmation is rejected and stock is not double-decremented. |
| Demo QR generation | PASS | Live API checkout returned a PNG data URL | Payload is a local `pakkahisaab://demo-payment/...` demo payload, not a UPI request. |
| TTS graceful fallback path | PASS | `/api/tts` returned controlled 503 when `edge-tts` was unavailable | Text workflow remained available. Actual `edge-tts` network synthesis was not tested. |
| ASR / microphone capture | NOT VERIFIED | Browser hardware/API unavailable in audit environment | Code path is present; real microphone capture requires a supported browser and permission. |
| TTS English/Hindi/Tamil live synthesis | NOT VERIFIED | External TTS dependency/network unavailable in audit environment | Code maps `en`, `hi`, and `ta` to the configured voices. |
| UI language switching | STATIC PASS | Frontend localization code inspected | Interactive browser click test was not available in this environment. |
| Judge Mode interactive flow | STATIC PASS | Judge Mode controls and workflow code inspected | Interactive browser click test was not available in this environment. |
| All visible buttons | NOT VERIFIED | Event handlers inspected, not clicked in a real browser | Requires browser interaction test. |
| 1366×768 layout | NOT VERIFIED | No browser rendering environment available | Requires visual browser test. |
| 1920×1080 layout | NOT VERIFIED | No browser rendering environment available | Requires visual browser test. |
| Security dangerous-call scan | PASS | Repository grep | No `eval`, `exec`, `os.system`, `shell=True`, `pickle.loads`, or `subprocess` usage found. |
| Secret-pattern scan | PASS | Repository grep | No matching API-key/token/private-key patterns found. |
| Runtime junk cleanup | PASS | Recursive file scan | No `.db`, `.sqlite`, `.pyc`, `.log`, `.bak`, `.old`, or `.tmp` files shipped. |
| Node dependency cleanup | PASS | `package.json` removed | The application does not use Node/npm. |
| Unused environment example cleanup | PASS | `.env.example` removed | The application does not read environment configuration. |
| Model cache cleanup | PASS | `models/` removed | No ASR/TTS/LLM model weights are used or bundled. |
| Hard-coded financial dashboard state | PASS | Backend/source inspection | Cart totals and inventory are read from SQLite. |
| Real payment capability | PASS | Source inspection | No payment SDK credentials or production payment endpoint exists. |

## Remaining verification

### BLOCKING for a literal clean-Windows acceptance test

- `run.bat` must still be executed on a clean Windows machine.
- The first-run Python 3.11.9 download and pinned dependency installation must be verified with internet access.
- Browser microphone behavior and the three-language speech path require a real supported browser and microphone.
- The live `edge-tts` network path requires an environment with network access.
- A real browser session should click every visible control and visually verify 1366×768 and 1920×1080.

These are not claims that the prototype is broken; they are checks that could not honestly be marked as passed in this Linux/headless audit environment.
