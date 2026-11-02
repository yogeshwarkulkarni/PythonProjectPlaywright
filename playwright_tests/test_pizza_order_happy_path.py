"""Happy path: order a pizza on Awesome Pizza and verify the order is received.

Flow (discovered via Playwright MCP):
  menu -> "+" on a pizza -> enter name -> cart shows item -> Place Order
  -> success notification with order ID -> order details show status RECEIVED.
No payment step exists in this app.
"""

from playwright.sync_api import Page, expect

from pages.pizza_order_page import PizzaOrderPage

PIZZA = "Margherita Pizza"
QUANTITY = 2
CUSTOMER = "Test User"


def test_place_pizza_order_happy_path(page: Page):
    pizza_page = PizzaOrderPage(page)
    pizza_page.navigate()
    expect(page).to_have_title(PizzaOrderPage.TITLE)

    # Menu loads asynchronously from the API.
    expect(pizza_page.menu_item(PIZZA)).to_be_visible()

    # Select the pizza and quantity.
    expect(pizza_page.place_order_button).to_be_disabled()
    pizza_page.add_pizza(PIZZA, QUANTITY)
    expect(pizza_page.quantity_display(PIZZA)).to_have_text(str(QUANTITY))

    # Cart contents.
    cart_item = pizza_page.cart_items
    expect(cart_item).to_have_count(1)
    expect(cart_item.locator(".cart-item-name")).to_have_text(PIZZA)
    expect(cart_item.locator(".cart-item-quantity")).to_have_text(f"Quantity: {QUANTITY}")
    expect(pizza_page.total_items).to_have_text(str(QUANTITY))

    # Checkout details: button stays disabled until a name is entered.
    expect(pizza_page.place_order_button).to_be_disabled()
    pizza_page.enter_name(CUSTOMER)
    expect(pizza_page.place_order_button).to_be_enabled()

    response = pizza_page.place_order()
    assert response.ok, f"Order API returned {response.status}"

    # Confirmation notification.
    expect(pizza_page.notification).to_contain_text("Order placed successfully! Order ID:")
    order_id = pizza_page.order_id_from_notification()

    # Order details are shown for the new order.
    expect(pizza_page.order_details).to_be_visible()
    expect(pizza_page.order_info("Order ID")).to_have_text(order_id)
    expect(pizza_page.order_info("Customer")).to_have_text(CUSTOMER)
    expect(pizza_page.order_info("Status")).to_have_text("RECEIVED")
    expect(pizza_page.order_contents).to_contain_text(PIZZA)
    expect(pizza_page.order_contents).to_contain_text(f"×{QUANTITY}")

    # Cart is reset after a successful order.
    expect(pizza_page.empty_cart).to_have_text("Your cart is empty")
    expect(pizza_page.total_items).to_have_text("0")
