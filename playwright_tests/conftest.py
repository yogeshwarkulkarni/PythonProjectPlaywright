import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import expect, sync_playwright

load_dotenv()

BASE_URL = os.getenv("PIZZA_BASE_URL", "http://localhost:3000/")
HEADLESS = os.getenv("HEADLESS", "false").lower() != "false"

expect.set_options(timeout=10_000)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(base_url=BASE_URL)
    page = context.new_page()
    yield page
    context.close()
