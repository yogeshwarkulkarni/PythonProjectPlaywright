"""Happy path: order a pizza on Awesome Pizza and verify the order is received.

Flow (discovered via Playwright MCP):
  menu -> "+" on a pizza -> enter name -> cart shows item -> Place Order
  -> success notification with order ID -> order details show status RECEIVED.
No payment step exists in this app.
"""

import re

from playwright.sync_api import Page, expect

PIZZA = "Margherita Pizza"
QUANTITY = 2
CUSTOMER = "Test User"
ORDER_ID = re.compile(r"order-[\w-]+")


def test_place_pizza_order_happy_path(page: Page):
    page.goto("/")
    expect(page).to_have_title("Awesome Pizza - Order Online")

    # Menu loads asynchronously from the API.
    menu_item = page.locator("#menu-container .menu-item").filter(
        has=page.get_by_role("heading", name=PIZZA, exact=True)
    )
    expect(menu_item).to_be_visible()

    # Select the pizza and quantity.
    place_order = page.locator("#place-order-btn")
    expect(place_order).to_be_disabled()
    for _ in range(QUANTITY):
        menu_item.get_by_role("button", name="+").click()
    expect(menu_item.locator(".quantity-display")).to_have_text(str(QUANTITY))

    # Cart contents.
    cart_item = page.locator("#cart-items .cart-item")
    expect(cart_item).to_have_count(1)
    expect(cart_item.locator(".cart-item-name")).to_have_text(PIZZA)
    expect(cart_item.locator(".cart-item-quantity")).to_have_text(f"Quantity: {QUANTITY}")
    expect(page.locator("#total-items")).to_have_text(str(QUANTITY))

    # Checkout details: button stays disabled until a name is entered.
    expect(place_order).to_be_disabled()
    page.get_by_label("Your Name:").fill(CUSTOMER)
    expect(place_order).to_be_enabled()

    with page.expect_response(
        lambda r: r.url.endswith("/orders") and r.request.method == "POST"
    ) as response_info:
        place_order.click()
    assert response_info.value.ok, f"Order API returned {response_info.value.status}"

    # Confirmation notification.
    notification = page.locator("#notification")
    expect(notification).to_contain_text("Order placed successfully! Order ID:")
    order_id = ORDER_ID.search(notification.inner_text()).group(0)

    # Order details are shown for the new order.
    details = page.locator("#order-details")
    expect(details).to_be_visible()

    def info(label: str):
        return details.locator(".order-info-item").filter(
            has=page.locator(".order-info-label", has_text=label)
        ).locator(".order-info-value")

    expect(info("Order ID")).to_have_text(order_id)
    expect(info("Customer")).to_have_text(CUSTOMER)
    expect(info("Status")).to_have_text("RECEIVED")
    expect(details.locator(".content-item")).to_contain_text(PIZZA)
    expect(details.locator(".content-item")).to_contain_text(f"×{QUANTITY}")

    # Cart is reset after a successful order.
    expect(page.locator("#cart-items .empty-cart")).to_have_text("Your cart is empty")
    expect(page.locator("#total-items")).to_have_text("0")
