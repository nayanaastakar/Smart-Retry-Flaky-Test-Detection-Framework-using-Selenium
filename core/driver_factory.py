"""WebDriver factory for Chrome, Firefox, Edge."""
from __future__ import annotations
import logging
from config import settings

log = logging.getLogger(__name__)

# Cache the chromedriver path globally so we don't query webdriver_manager on every retry
_CACHED_CHROMEDRIVER_PATH = None


def create_driver(browser: str | None = None, headless: bool | None = None):
    global _CACHED_CHROMEDRIVER_PATH
    browser = (browser or settings.DEFAULT_BROWSER).lower()
    headless = settings.HEADLESS if headless is None else headless

    if browser == "chrome":
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        import os, struct

        def _is_valid_exe(path):
            """Return True only if the exe is a valid 64-bit PE binary."""
            try:
                with open(path, "rb") as f:
                    magic = f.read(2)
                    if magic != b"MZ":
                        return False
                    f.seek(0x3C)
                    pe_offset = struct.unpack("<I", f.read(4))[0]
                    f.seek(pe_offset + 4)
                    machine = struct.unpack("<H", f.read(2))[0]
                    return machine == 0x8664
            except Exception:
                return False

        service = None

        # Re-use cached executable path if available
        if _CACHED_CHROMEDRIVER_PATH and os.path.isfile(_CACHED_CHROMEDRIVER_PATH):
            service = Service(_CACHED_CHROMEDRIVER_PATH)
        else:
            # 1. Check for our manually downloaded 64-bit chromedriver first
            local_drivers = [
                r"C:\Users\HP\Downloads\smartretry_screenshots_final\chromedriver_bin\chromedriver-win64\chromedriver.exe",
            ]
            for p in local_drivers:
                if os.path.isfile(p) and _is_valid_exe(p):
                    log.info("Using local 64-bit chromedriver: %s", p)
                    _CACHED_CHROMEDRIVER_PATH = p
                    service = Service(p)
                    break

            # 2. Fallback: try webdriver_manager but validate the binary
            if service is None:
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    wdm_path = ChromeDriverManager().install()
                    if _is_valid_exe(wdm_path):
                        log.info("Using wdm chromedriver: %s", wdm_path)
                        _CACHED_CHROMEDRIVER_PATH = wdm_path
                        service = Service(wdm_path)
                    else:
                        log.warning("wdm returned a 32-bit binary at %s, skipping.", wdm_path)
                except Exception as e:
                    log.warning("webdriver_manager failed: %s", e)

            # 3. Last resort: let Selenium find chromedriver on PATH
            if service is None:
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
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        # CRITICAL: "none" means Selenium does NOT wait for page to finish loading
        # after a navigation. This allows assert_text to run WHILE the page is
        # still loading → it will fail on Attempt 1 and pass on Attempt 2 = FLAKY
        opts.page_load_strategy = "none"

        driver = webdriver.Chrome(service=service, options=opts)
        
        # Additional anti-bot evasion
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

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
            opts.add_argument("-headless")
        driver = webdriver.Firefox(service=service, options=opts)
        return driver

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
            opts.add_argument("--headless")
        driver = webdriver.Edge(service=service, options=opts)
        return driver

    raise ValueError(f"Unsupported browser: {browser}")
