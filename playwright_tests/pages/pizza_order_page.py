"""Page object for the Awesome Pizza single-page ordering app.

Follows https://playwright.dev/python/docs/pom: locators are defined once in
__init__, methods wrap user actions, and assertions stay in the tests.
"""

import re

from playwright.sync_api import Locator, Page, Response

ORDER_ID = re.compile(r"order-[\w-]+")


class PizzaOrderPage:
    TITLE = "Awesome Pizza - Order Online"

    def __init__(self, page: Page):
        self.page = page
        # Menu
        self.menu_items = page.locator("#menu-container .menu-item")
        # Cart
        self.cart_items = page.locator("#cart-items .cart-item")
        self.empty_cart = page.locator("#cart-items .empty-cart")
        self.total_items = page.locator("#total-items")
        # Checkout
        self.name_input = page.get_by_label("Your Name:")
        self.place_order_button = page.locator("#place-order-btn")
        # Confirmation
        self.notification = page.locator("#notification")
        self.order_details = page.locator("#order-details")
        self.order_contents = self.order_details.locator(".content-item")

    def navigate(self):
        self.page.goto("/")

    def menu_item(self, pizza: str) -> Locator:
        return self.menu_items.filter(
            has=self.page.get_by_role("heading", name=pizza, exact=True)
        )

    def quantity_display(self, pizza: str) -> Locator:
        return self.menu_item(pizza).locator(".quantity-display")

    def add_pizza(self, pizza: str, quantity: int = 1):
        for _ in range(quantity):
            self.menu_item(pizza).get_by_role("button", name="+").click()

    def enter_name(self, name: str):
        self.name_input.fill(name)

    def place_order(self) -> Response:
        """Click Place Order and return the POST /orders response."""
        with self.page.expect_response(
            lambda r: r.url.endswith("/orders") and r.request.method == "POST"
        ) as response_info:
            self.place_order_button.click()
        return response_info.value

    def order_id_from_notification(self) -> str:
        return ORDER_ID.search(self.notification.inner_text()).group(0)

    def order_info(self, label: str) -> Locator:
        return self.order_details.locator(".order-info-item").filter(
            has=self.page.locator(".order-info-label", has_text=label)
        ).locator(".order-info-value")
