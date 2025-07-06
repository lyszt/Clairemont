import logging
import os
import random
import signal
import tempfile
import datetime
import zipfile
import dotenv
import signal
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import rich
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium_stealth import stealth
import undetected_chromedriver as webdriver
import distutils

class Configure:
    def __init__(self, console = None):
        self.console = console

    @staticmethod
    def create_driver(headless: bool = True):

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('selenium')
        logger.setLevel(logging.INFO)

        options = Options()
        dotenv.load_dotenv(".env")

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
            # Opera
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0',
        ]

        ua = UserAgent(os="win", platforms="pc",
                       fallback=random.choice(user_agents))
        user_agent_string = ua.random
        platform_string = "Win32"

        options.add_argument(f'--user-agent={user_agent_string}')
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})


        def start_driver_proxyless(service, options):
            driver = webdriver.Chrome(service=service, options=options)
            return driver

        print("Rodando em ambiente local. Selenium irá gerenciar o chromedriver.")
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920x1080")

        service = Service(service_args=["--verbose"])
        driver = start_driver_proxyless(service, options)

        print("Driver do Selenium está pronto.")

        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent_string,
            "acceptLanguage": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "platform": platform_string
        })
        js_shield = f"""
                Object.defineProperty(navigator, 'platform', {{
                  get: () => '{platform_string}'
                }});
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => [
                        {{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }},
                        {{ name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' }},
                        {{ name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }}
                    ]
                }});
                // Spoof screen properties to match a common desktop
                Object.defineProperty(screen, 'availWidth', {{ get: () => 1920 }});
                Object.defineProperty(screen, 'availHeight', {{ get: () => 1040 }});
                Object.defineProperty(screen, 'width', {{ get: () => 1920 }});
                Object.defineProperty(screen, 'height', {{ get: () => 1080 }});
            """
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': js_shield
        })
        driver.maximize_window()
        stealth(driver,
                languages=["pt-BR", "pt"],
                vendor="Google Inc.",
                platform="Win32",
                fix_hairline=True,
                run_on_insecure_origins=False,
                )
        return driver