import allure
import pytest
import os

from playwright.sync_api import BrowserContext, Page, sync_playwright
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(find_dotenv())

# Parameters for storing the session cookies in a file
STORAGE_DIR = Path(__file__).parent.parent / "config"
STORAGE_PATH = STORAGE_DIR / "state.json"


@pytest.fixture(scope="function")
def browser_context_args(request, browser_context_args):
    """
    Desktop resolution and SSL certificate errors ignoring
    """
    extra_args = {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True
    }

    # Check if this specific test execution thread has a 'user_state' parameter
    if "user_state" in request.fixturenames:
        current_state = request.getfixturevalue("user_state")

        # If the user_state == 'logged_in', get the cookies from the file
        if current_state == "logged_in" and STORAGE_PATH.exists():
            extra_args["storage_state"] = str(STORAGE_PATH)

    return {**browser_context_args, **extra_args}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    If a test fails, this hook will flag it
    """
    outcome = yield
    rep = outcome.get_result()
    # Set a attribute on the test item indicating its success/failure status
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session", autouse=True)
def global_authentication_setup(pytestconfig):
    """
    Writing the cookies for the logged in user
    """
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    configured_base_url = pytestconfig.getoption("base_url")

    if not username or not password:
        raise ValueError(
            "USERNAME or PASSWORD environment variables are missing!")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            base_url=configured_base_url,
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True
        )

        page = context.new_page()
        page.goto("/index.php?rt=account/login", wait_until="domcontentloaded")

        page.locator("#loginFrm_loginname").fill(username)
        page.locator("#loginFrm_password").fill(password)
        page.locator("button[title='Login']").click()

        page.wait_for_url("**/index.php?rt=account/account")

        context.storage_state(path=str(STORAGE_PATH))
        browser.close()


@pytest.fixture(scope="function", autouse=True)
def state_logging_checkpoint(request):
    """
    Terminal visual reporter hook
    """
    if "user_state" in request.fixturenames:
        state = request.getfixturevalue("user_state")
        yield
        print(
            f" -> Execution complete: [{state.upper()}]")
    else:
        yield

# Allure reporting


def pytest_exception_interact(node, call, report):
    """
    Attach the screenshot inside the main Allure Test Body block
    """
    # Look for the built-in Playwright page fixture inside the failing test node
    if "page" in node.funcargs:
        page = node.funcargs["page"]

        # Sanitize the name of the failing test execution thread
        test_name = node.name.replace("[", "_").replace("]", "_")
        screenshot_path = f"screenshots/FAIL_{test_name}.png"

        # Capture the live state binary of the DOM at the exact moment of failure
        screenshot_bytes = page.screenshot(
            path=screenshot_path, full_page=True)

        # Attach the binary directly onto the core Test Body level block inside Allure
        allure.attach(
            screenshot_bytes,
            name=f"FAIL_screenshot_{test_name}",
            attachment_type=allure.attachment_type.PNG
        )
