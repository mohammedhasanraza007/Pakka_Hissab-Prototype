# Pakka Hisaab — Prototype

Pakka Hisaab is a local hackathon prototype for an intent-driven merchant POS workflow.

The prototype demonstrates one concrete flow: a merchant types or speaks a command such as **“Clear Cart 1 with UPI.”** The application parses that command into a structured intent, loads the cart from SQLite, creates a simulated payment, and only commits inventory/reconciliation after the simulated payment is confirmed.

> **Prototype limits:** product/cart data is synthetic, payments are simulated, QR codes are demo-only, and no real money is moved.

## What is actually implemented

- FastAPI backend serving the dashboard and JSON API.
- Vanilla HTML/CSS/JavaScript frontend; no Node.js runtime is required.
- SQLite database with deterministic synthetic products, carts, orders, payments, transactions, and audit events.
- Five seeded carts and ten products.
- Deterministic multilingual intent parsing for English, Hindi, and Tamil examples used by the prototype.
- Text command input.
- Browser Speech Recognition integration for English, Hindi, and Tamil when the browser/device supports it.
- Optional spoken feedback through `edge-tts`; the browser's speech synthesis is the fallback.
- A language selector that localizes the dashboard and selects the corresponding voice locale.
- Simulated UPI payment flow with a clearly marked demo QR.
- Simulated cash-drawer flow for the demo cases.
- Payment success/failure state transitions with SQLite-backed inventory changes.
- Duplicate-payment protection for already-paid payments/carts.
- Judge Mode.
- Reset Demo.

## What is NOT implemented

- No real UPI payment processing.
- No Razorpay credentials, bank credentials, webhook credentials, or production payment endpoint.
- No real cash-drawer hardware or denomination sensing.
- No production authentication or multi-store deployment.
- No bundled ASR or TTS model weights.
- No LLM is used by the prototype.
- Browser speech recognition is an adapter supplied by the browser; support depends on the browser and microphone permissions.
- `edge-tts` is a network-based speech service, not a model bundled in this repository. If it is unavailable, text mode and browser speech synthesis remain available.

## Synthetic demo data

The database is created automatically on first startup and seeded deterministically.

| Cart | Contents | Total | Demo case |
| --- | --- | ---: | --- |
| Cart 1 | Britannia Biscuits ×2, Soap ×1 | ₹299 | UPI success |
| Cart 2 | Britannia Biscuits ×1, Soap ×2 | ₹217 | UPI failure |
| Cart 3 | Milk ×2, Bread ×1, Soap ×1 | ₹205 | Cash received |
| Cart 4 | Tea ×1, Sugar ×1 | ₹188 | Cash timeout |
| Cart 5 | Shampoo ×1, Toothpaste ×1, Soap ×1, Bread ×1 | ₹391 | Generality/manual case |

The UI reads cart totals and inventory from SQLite rather than using hard-coded dashboard totals.

## One-click Windows launch

Double-click **`run.bat`**.

The launcher:

1. Creates `logs/`.
2. Uses the pinned Python version **3.11.9**; if that exact runtime is not available in the supported launcher path, it downloads the official Python installer and installs it under the user's local application directory.
3. Creates `.venv` with that Python runtime.
4. Installs the pinned Python dependencies from `requirements.txt`.
5. Initializes the SQLite database and deterministic seed data.
6. Finds an available port in the launcher's configured range.
7. Starts the FastAPI application, which also serves the frontend.
8. Checks the local health endpoint before opening the browser.
9. Opens the local application URL.

No Node.js installation or separate frontend build is required.

If Python 3.11.9 is not already available, the first run needs internet access to download the official Python installer and Python packages. The application itself is local once its dependencies are installed; `edge-tts` additionally needs network access when spoken feedback is requested.

### Runtime dependencies

The launcher installs:

- FastAPI
- Uvicorn
- Pydantic
- qrcode
- edge-tts
- pytest (kept for repository verification)

SQLite is provided by Python and does not require a separate database server.

## Voice behavior

### Speech-to-text

The microphone button uses the browser's Speech Recognition API. The selected UI language maps to these locales:

- English → `en-IN`
- Hindi → `hi-IN`
- Tamil → `ta-IN`

If Speech Recognition or microphone access is unavailable, the UI reports that voice is unavailable and keeps text mode usable.

### Spoken feedback

The backend exposes `/api/tts` and uses these `edge-tts` voices when the service is available:

- English → `en-IN-NeerjaNeural`
- Hindi → `hi-IN-SwaraNeural`
- Tamil → `ta-IN-PallaviNeural`

If that service is unavailable, the frontend falls back to browser speech synthesis. There is no downloaded multilingual model in the repository.

## Core workflow

```text
Merchant command
      ↓
Deterministic intent parser
      ↓
Structured intent
      ↓
SQLite-backed workflow
      ↓
Cart / Order / Payment
      ↓
Payment confirmation
      ↓
Inventory update
      ↓
Reconciliation + audit event
```

The intent parser does not execute SQL or mutate inventory. The workflow layer owns business-state changes.

## Demo commands

English:

```text
Clear Cart 1 with UPI.
Can you let the first customer settle their bill using UPI?
Clear Cart 2 with UPI.
Clear Cart 3 with cash.
Check biscuit stock.
Reset demo.
```

Hindi examples used by the prototype:

```text
कार्ट एक को यूपीआई से क्लियर करो
कार्ट वन का यू पी आई पेमेंट करो
पहले कार्ट का भुगतान करो
```

Tamil example used by the prototype:

```text
கார்ட் 1-ன் கட்டணத்தை UPI மூலம் செலுத்துங்கள்.
```

## Judge Mode

Open **Judge Mode** in the dashboard and use the example command. The intended demonstration is:

1. Intent is interpreted.
2. Cart and bill are loaded from SQLite.
3. A simulated payment is created.
4. The demo QR is displayed for UPI cases.
5. Simulated success commits inventory and reconciliation.
6. Simulated failure leaves inventory unchanged.

The QR payload is a `pakkahisaab://demo-payment/...` demo payload. It is not a UPI payment request.

## Resetting the demo

Use **Reset demo** in the UI to restore the deterministic products, carts, payments, orders, transactions, audit log, and inventory state.

## Logs

`run.bat` creates:

```text
logs/setup.log
logs/backend.log
logs/frontend.log
logs/error.log
```

The repository does not ship runtime logs. They are generated locally when the launcher runs.

## Project structure

```text
Pakka-Hisaab/
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── intent.py
│   └── workflow.py
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── payments.css
├── tests/
│   └── test_workflow.py
├── ARCHITECTURE.md
├── DEMO_GUIDE.md
├── QA_REPORT.md
├── LICENSE
├── requirements.txt
├── run.bat
├── build.bat
├── run.sh
├── build.sh
└── .gitignore
```

## Verification

The repository contains automated tests for parser behavior, deterministic demo cases, SQLite-backed workflow transitions, inventory protection, duplicate-payment handling, reset behavior, and persistence.

The release QA report records only checks that were actually executed in the audit environment. Windows-specific launcher execution, physical microphone capture, and live external TTS service availability are environment-dependent and are not represented as successful tests unless directly verified.

## Production direction

The prototype is intentionally limited to local deterministic state and simulated payments. A production implementation would require real payment-provider integration and verified server-side payment events, production authentication, stronger operational logging/auditing, deployment infrastructure, and real merchant validation. Those are roadmap items, not current prototype capabilities.
