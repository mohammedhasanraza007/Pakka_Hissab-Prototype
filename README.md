# Pakka Hisaab — Prototype

Pakka Hisaab is a local hackathon prototype for an intent-driven merchant POS workflow.

The prototype demonstrates a concrete flow where a merchant can type or speak a command such as **"Clear Cart 1 with UPI."** The command is converted into a structured intent, the cart is loaded from SQLite, a simulated payment is created, and inventory/reconciliation are updated only after simulated payment confirmation.

> **Prototype limits:** product and cart data are synthetic, payments are simulated, QR codes are demo-only, and no real money is moved.

[![Python 3.11.9](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

---
<p align="center">
  <img src="https://github.com/user-attachments/assets/d1637e3e-6ce3-4c7b-bebe-16985d0772b0"
       alt="Pakka Hisaab Logo"
       width="140">
</p>

---

## ⚠️ Windows — Start Here

**On a fresh checkout, run `build.bat` before `run.bat`.**

### First-time setup

1. Double-click **`build.bat`**.
2. Wait for the build/setup process to finish.
3. Then double-click **`run.bat`**.
4. Wait for the application to start.
5. The local application should open in your browser.

```text
build.bat
   ↓
Environment + dependencies
   ↓
run.bat
   ↓
FastAPI application
   ↓
Browser
```

The first setup may require internet access to download Python and Python packages.

After the environment has been prepared, use **`run.bat`** to launch the application.

> **Important:** The repository does not use `run.bat` as the initial dependency-build step. `build.bat` is the first step on a fresh Windows environment.

---

## What Is Implemented

The current prototype includes:

- FastAPI backend serving the dashboard and JSON API.
- Vanilla HTML/CSS/JavaScript frontend.
- No Node.js runtime required.
- SQLite database.
- Deterministic synthetic products and carts.
- SQLite-backed orders, payments, transactions, inventory, and audit events.
- Five seeded carts.
- Ten seeded products.
- Deterministic multilingual intent parsing for supported English, Hindi, and Tamil examples.
- Text command input.
- Browser Speech Recognition integration when supported by the browser/device.
- English, Hindi, and Tamil language selection.
- Localized dashboard interface.
- Voice locale selection based on the selected language.
- Optional spoken feedback through `edge-tts`.
- Browser speech-synthesis fallback where supported.
- Simulated UPI payment workflow.
- Clearly labelled demo QR generation.
- Simulated cash workflow for supported demo cases.
- SQLite-backed payment state transitions.
- SQLite-backed inventory updates.
- Duplicate-payment protection.
- Judge Mode.
- Reset Demo.

---

## What Is Not Implemented

This is a prototype, not a production payment system.

The repository does **not** provide:

- Real UPI payment processing.
- Real Razorpay integration.
- Razorpay credentials.
- Bank credentials.
- Production webhook credentials.
- Production payment endpoints.
- Real money movement.
- Real cash-drawer hardware.
- Physical denomination sensing.
- Production authentication.
- Multi-store production deployment.
- A bundled ASR model.
- A bundled TTS model.
- An LLM.

Browser speech recognition depends on browser/device support and microphone permissions.

`edge-tts` is a network-based speech service. It is **not a multilingual TTS model bundled inside the repository**.

If speech functionality is unavailable, the core text-based prototype remains usable.

---

## Synthetic Demo Data

The application uses deterministic synthetic retail data.

The demo database contains five carts and ten products.

| Cart | Contents | Total | Demo Case |
| --- | --- | ---: | --- |
| Cart 1 | Britannia Biscuits ×2, Soap ×1 | ₹299 | UPI success |
| Cart 2 | Britannia Biscuits ×1, Soap ×2 | ₹217 | UPI failure |
| Cart 3 | Milk ×2, Bread ×1, Soap ×1 | ₹205 | Cash received |
| Cart 4 | Tea ×1, Sugar ×1 | ₹188 | Cash timeout |
| Cart 5 | Shampoo ×1, Toothpaste ×1, Soap ×1, Bread ×1 | ₹391 | Generality/manual case |

The application reads cart totals and inventory state from SQLite rather than relying on hard-coded dashboard totals.

---

## Windows Setup

### `build.bat`

The first step on Windows is:

```text
build.bat
```

The build process prepares the Python environment and installs the dependencies required by the application.

### `run.bat`

After the build has completed:

```text
run.bat
```

The launcher starts the local application.

The intended flow is:

```text
build.bat
    ↓
Python environment
    ↓
Python dependencies
    ↓
run.bat
    ↓
FastAPI backend
    ↓
Frontend
    ↓
Browser
```

### Python

The project uses the Python version specified by its Windows setup process.

If the required Python runtime is not available through the supported installation path, the setup process can obtain the required official Python installer.

Internet access may therefore be required during the initial setup.

### Frontend

The frontend is implemented using:

- HTML
- CSS
- JavaScript

No Node.js runtime or separate frontend build system is required by the current application.

### Database

The application uses SQLite.

No separate database server is required.

---

## Runtime Dependencies

The Python dependency set contains the packages required by the current implementation.

These include:

- FastAPI
- Uvicorn
- Pydantic
- qrcode
- edge-tts
- pytest

The authoritative dependency versions are defined in:

```text
requirements.txt
```

---

## Voice

### Speech-to-Text

The microphone interface uses the browser's Speech Recognition API when supported.

The selected application language maps to the following locales:

| Language | Locale |
| --- | --- |
| English | `en-IN` |
| Hindi | `hi-IN` |
| Tamil | `ta-IN` |

Speech recognition availability depends on:

- Browser support.
- Operating-system support.
- Microphone availability.
- Microphone permissions.
- The browser's speech-recognition implementation.

If speech recognition is unavailable, text input remains available.

### Spoken Feedback

When available, the backend can use `edge-tts` with these voices:

| Language | Voice |
| --- | --- |
| English | `en-IN-NeerjaNeural` |
| Hindi | `hi-IN-SwaraNeural` |
| Tamil | `ta-IN-PallaviNeural` |

If backend TTS is unavailable, the frontend can use browser speech synthesis where supported.

> **Important:** There is no downloaded multilingual TTS model included in the repository. `edge-tts` is an external network-based speech service.

---

## Language Switching

The dashboard contains a language selector.

The prototype supports language selection for:

- English
- Hindi
- Tamil

The selected language affects the supported localized UI and voice locale behavior.

### Hindi Example

```text
कार्ट एक को यूपीआई से क्लियर करो
```

### Tamil Example

```text
கார்ட் 1-ன் கட்டணத்தை UPI மூலம் செலுத்துங்கள்.
```

The natural-language intent engine is deterministic and does not use an LLM.

---

## Core Workflow

The main prototype architecture is:

```text
┌──────────────────────┐
│   Merchant Command   │
│  Text / Voice Input  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Deterministic Intent │
│       Parser         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Structured Intent  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ SQLite-backed        │
│ Workflow Engine      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Cart / Order /       │
│ Payment              │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Payment Confirmation │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Inventory Update     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Reconciliation +     │
│ Audit Event          │
└──────────────────────┘
```

The intent parser does not directly execute SQL or perform inventory mutations.

The workflow layer is responsible for the application state transitions.

---

## Demo Commands

### English

```text
Clear Cart 1 with UPI.
Can you let the first customer settle their bill using UPI?
Clear Cart 2 with UPI.
Clear Cart 3 with cash.
Check biscuit stock.
Reset demo.
```

### Hindi

```text
कार्ट एक को यूपीआई से क्लियर करो
कार्ट वन का यू पी आई पेमेंट करो
पहले कार्ट का भुगतान करो
```

### Tamil

```text
கார்ட் 1-ன் கட்டணத்தை UPI மூலம் செலுத்துங்கள்.
```

The prototype uses deterministic intent parsing rather than an LLM.

---

## Simulated Payment

Payment processing is deliberately simulated.

For UPI demonstration cases, the application generates a clearly labelled demo QR.

The QR payload uses a demo-specific format:

```text
pakkahisaab://demo-payment/...
```

This is **not a UPI payment request** and cannot be used to transfer real money.

### Simulated Success

```text
Payment Created
      ↓
Payment Pending
      ↓
Simulated Success
      ↓
Payment PAID
      ↓
Order PAID
      ↓
Inventory Updated
      ↓
Transaction Reconciled
```

### Simulated Failure

```text
Payment Created
      ↓
Payment Pending
      ↓
Simulated Failure
      ↓
Payment Not Confirmed
      ↓
Order Remains Unpaid
      ↓
Inventory Unchanged
```

The important prototype behavior is that inventory changes occur as part of the successful payment workflow rather than simply displaying a changed number.

---

## Judge Mode

The dashboard includes **Judge Mode** to guide a demonstration of the prototype.

The intended demonstration is:

1. Enter or speak a command.
2. Observe the detected intent.
3. Observe the selected cart.
4. Observe the order/payment workflow.
5. View the demo QR for UPI.
6. Simulate payment success or failure.
7. Observe the resulting inventory and reconciliation state.

### Example

```text
Clear Cart 1 with UPI.
```

The intended demonstration path is:

```text
INTENT
   ↓
CART
   ↓
ORDER
   ↓
PAYMENT
   ↓
INVENTORY
   ↓
RECONCILIATION
```

Judge Mode uses the prototype's local workflow and simulated payment state rather than representing a real financial transaction.

---

## Reset Demo

Use **Reset Demo** in the application to restore the deterministic demonstration state.

The reset operation restores the relevant demo database state, including:

- Products
- Carts
- Inventory
- Orders
- Payments
- Transactions
- Audit events

---

## Logs

Runtime logs are generated locally.

The expected log directory is:

```text
logs/
├── setup.log
├── backend.log
├── frontend.log
└── error.log
```

Runtime logs are generated during execution and are not intended to be committed to the repository.

---

## Project Structure

```text
Pakka_Hissab-Prototype/
│
├── Pakka Hisaab/
│   │
│   ├── backend/
│   │   ├── app.py
│   │   ├── db.py
│   │   ├── intent.py
│   │   └── workflow.py
│   │
│   ├── frontend/
│   │   ├── index.html
│   │   ├── app.js
│   │   ├── styles.css
│   │   └── payments.css
│   │
│   ├── tests/
│   │   └── test_workflow.py
│   │
│   ├── ARCHITECTURE.md
│   ├── DEMO_GUIDE.md
│   ├── QA_REPORT.md
│   ├── LICENSE
│   ├── requirements.txt
│   ├── build.bat
│   ├── run.bat
│   ├── build.sh
│   ├── run.sh
│   └── .gitignore
│
└── README.md
```

---

## Verification

The repository contains automated tests covering parts of the deterministic prototype workflow, including:

- Intent parsing.
- Demo cases.
- SQLite-backed workflow transitions.
- Inventory protection.
- Duplicate-payment handling.
- Reset behavior.
- Persistence behavior.

The repository's `QA_REPORT.md` records the checks that were actually executed.

Windows-specific launcher execution, physical microphone capture, browser speech recognition, and live external TTS availability depend on the execution environment.

These environment-dependent capabilities should not be interpreted as universally guaranteed by the repository.

---

## Security and Scope

This is a hackathon prototype.

It intentionally avoids real financial transactions and production payment credentials.

The prototype does not contain:

- Real payment credentials.
- Bank credentials.
- Production webhook credentials.
- Production payment endpoints.
- Real money movement.

Natural-language input is converted into structured intent and then processed by deterministic application logic.

The prototype is not intended for production financial use.

---

## Production Direction

A production implementation would require additional engineering and validation, including:

- Real payment-provider integration.
- Server-side verification of payment events.
- Production authentication and authorization.
- Stronger operational monitoring and auditing.
- Production deployment infrastructure.
- Merchant and hardware integration.
- Security review and penetration testing.
- Reliability and failure-recovery mechanisms.
- Real-world merchant validation.

These are **future production requirements, not current prototype capabilities**.

---

## License

This project is licensed under the **Apache License 2.0**.

See [`LICENSE`](LICENSE) for the full license text.
