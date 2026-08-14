# Pakka Hisaab — Demo Guide

## 60-Second Path

### First-time Windows setup

1. Extract the project.
2. Double-click `build.bat`.
3. Wait for the build/setup process to finish.
4. After the build completes, double-click `run.bat`.
5. Wait for the application to start and open in the browser.

> **Important:** On a fresh Windows checkout, use `build.bat` first. Do not start with `run.bat`.

### Demo

1. Open **Judge Mode** or use the command center.
2. Type:
   `Clear Cart 1 with UPI.`
3. Confirm that the UI shows **Cart 1** and **₹299** from the SQLite-backed cart.
4. Observe the clearly marked demo QR.
5. Use the simulated payment controls.
6. On success, the UI shows payment confirmation, order paid, inventory updated, and reconciliation.
7. Run:
   `Clear Cart 2 with UPI.`
8. Simulate payment failure.
9. Confirm that the order remains unpaid and inventory remains unchanged.
10. Switch the UI to Hindi or Tamil to demonstrate localized text and the corresponding voice locale.
11. Use **Reset Demo** before repeating the presentation.

## What the Demo Proves

The important proof is the local state transition, not live payment processing:

```text
Intent
   ↓
Cart
   ↓
Order
   ↓
Demo Payment
   ↓
Inventory
   ↓
Reconciliation
