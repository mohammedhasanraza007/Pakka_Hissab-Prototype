# Pakka Hisaab — Demo Guide

## 60-second path

1. Extract the project.
2. Double-click `run.bat` on Windows.
3. Wait for setup and browser launch.
4. Open **Judge Mode** or use the command center.
5. Type: `Clear Cart 1 with UPI.`
6. Confirm that the UI shows Cart 1 and **₹299** from the SQLite-backed cart.
7. Observe the clearly marked demo QR.
8. Use the simulated payment controls.
9. On success, the UI shows payment confirmation, order paid, inventory updated, and reconciliation.
10. Run `Clear Cart 2 with UPI.` and simulate failure. Inventory remains unchanged.
11. Switch the UI to Hindi or Tamil to demonstrate localized text and the corresponding voice locale.
12. Use **Reset demo** before repeating the presentation.

## What the demo proves

The important proof is the local state transition, not live payment processing:

```text
Intent → Cart → Order → Demo Payment → Inventory → Reconciliation
```

Cart 1 is the success case. Cart 2 is the failure case.

## Voice

Press **SPEAK** after selecting English, Hindi, or Tamil. Browser Speech Recognition must be available and microphone permission must be granted. If it is not available, use the text command field; the core workflow does not depend on voice.

Spoken feedback uses `edge-tts` when available and browser speech synthesis as fallback. No TTS/ASR model files are bundled.

## Demo boundaries

- All retail data is synthetic.
- Payments are simulated.
- QR codes are demo-only.
- No real money is moved.
- No physical cash drawer is controlled.
