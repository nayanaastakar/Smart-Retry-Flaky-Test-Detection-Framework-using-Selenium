"""WebDriver factory for Chrome, Firefox, Edge."""
from __future__ import annotations
import logging
from config import settings

log = logging.getLogger(__name__)


def create_driver(browser: str | None = None, headless: bool | None = None):
    browser = (browser or settings.DEFAULT_BROWSER).lower()
    headless = settings.HEADLESS if headless is None else headless

    if browser == "chrome":
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
        except Exception:
            service = Service()
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=service, options=opts)

    elif browser == "firefox":
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            service = Service(GeckoDriverManager().install())
        except Exception:
            service = Service()
        opts = Options()
        if headless:
            opts.add_argument("--headless")
        driver = webdriver.Firefox(service=service, options=opts)

    elif browser == "edge":
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.edge.service import Service
        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            service = Service(EdgeChromiumDriverManager().install())
        except Exception:
            service = Service()
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Edge(service=service, options=opts)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    driver.set_page_load_timeout(settings.EXECUTION_TIMEOUT)
    log.info("Driver created: %s headless=%s", browser, headless)
    return driver
