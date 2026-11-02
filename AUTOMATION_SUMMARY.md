# Pizza Ordering Automation – Summary

## 1. What was built using AI

**Target app:** Awesome Pizza at `http://localhost:3000/` (no payment step)
Steps:

1. Install Node.js.
2. Open the terminal.
3. Navigate to the **Awesome Pizza** project directory and run `npm install`.
4. Start the application by running `npm start`.
5. Open the VS Code terminal and execute the Playwright tests using:

   ```bash
   pytest playwright_tests -v
   ```

**Happy path:** pick a pizza (Margherita, quantity 2) → enter your name → **Place Order** → success message with an order ID → order details show status `RECEIVED`.

### Files added

| File | Purpose |
|---|---|
| `playwright_tests/conftest.py` | pytest fixtures: Chromium browser, a fresh browser context per test, base URL from `PIZZA_BASE_URL`, `HEADLESS` setting, 10 s wait timeout. |
| `playwright_tests/test_pizza_order_happy_path.py` | The end-to-end happy path test. |

`.env` and `requirments.txt` were not changed.

### What the test checks
1. Page title, and the Margherita Pizza card appears once the menu loads
2. **Place Order** is disabled while the cart is empty
3. The card shows quantity `2`, the cart shows one line "Margherita Pizza / Quantity: 2", and the total is `2`
4. **Place Order** stays disabled until a name is entered, then becomes enabled
5. The order request (`POST /orders`) gets a successful response
6. The success message contains the order ID
7. Order details show that ID, customer `Test User`, status `RECEIVED`, and `Margherita Pizza ×2`
8. The cart is empty again and the total is back to `0`

Locators use element IDs, labels and roles. Waits rely on Playwright's built-in auto-waiting and on waiting for the order request. There are no sleep statements.

### Results
- 1st run: **1 passed** (2.63 s)
- 3 more runs: **1 passed** each time (~0.6 s)
- One extra order was placed during the MCP exploration (`order-1793221280681-540`). Every test run creates a real order in the local app.

## 3. How to run (current Python setup)

```bash
# Default run (conftest now defaults to a visible browser)
.venv/bin/python -m pytest playwright_tests -v

# Headless run
HEADLESS=true .venv/bin/python -m pytest playwright_tests -v

# Step through actions in the Playwright Inspector
PWDEBUG=1 .venv/bin/python -m pytest playwright_tests -s```

> `npx playwright test --ui` does **not** work here. It's the Node/TypeScript test runner and can't find Python tests. Python Playwright has no `--ui` mode; the closest is the Trace Viewer (`python -m playwright show-trace trace.zip`), which needs tracing turned on in `conftest.py`.

