import os
import time
import traceback

from selenium import webdriver
import dotenv
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import WebElement
import selenium.webdriver.support.expected_conditions as EC
from Bot.Modules.Actions.WebDriver import Configure
from bs4 import BeautifulSoup


def parse_sigaa_portal(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Student information
    student_info = {
        "name": soup.select_one("#info-usuario .usuario span").get_text(strip=True),
        "registration": soup.find("td", text=" Matrícula: ").find_next_sibling("td").get_text(strip=True),
        "course": soup.find("td", text=" Curso: ").find_next_sibling("td").get_text(strip=True),
        "status": soup.find("td", text=" Status: ").find_next_sibling("td").get_text(strip=True),
        "email": soup.find("td", text=" E-Mail: ").find_next_sibling("td").get_text(strip=True),
        "semester": soup.select_one(".periodo-atual strong").get_text(strip=True),
        "campus": soup.select_one(".unidade").get_text(strip=True).split('(')[0].strip()
    }

    disciplines = []
    for row in soup.select("#main-docente table.subFormulario + table tr:not(:first-child)"):
        if 'style' in row.attrs or row.find('td', colspan="5"):  # Skip header rows
            continue

        cols = row.find_all('td')
        if len(cols) >= 3:
            disciplines.append({
                "name": cols[0].get_text(strip=True),
                "location": cols[1].get_text(strip=True),
                "schedule": cols[2].get_text(strip=True)
            })

    # Upcoming assignments
    assignments = []
    for row in soup.select("#avaliacao-portal table tr"):
        if 'background' in row.get('style', '') or not row.find_all('td'):  # Skip header rows
            continue

        cols = row.find_all('td')
        if len(cols) >= 3:
            assignment_text = cols[2].get_text(strip=True, separator=' ')
            assignment_parts = assignment_text.split(' ', 1)

            assignments.append({
                "date": cols[1].get_text(strip=True),
                "course": assignment_parts[0],
                "type": assignment_parts[1].split(':', 1)[0].strip(),
                "description": assignment_parts[1].split(':', 1)[1].strip()
            })

    return {
        "student_info": student_info,
        "current_disciplines": disciplines,
        "upcoming_assignments": assignments
    }



def _find_element(driver: WebDriver, wait: WebDriverWait, by: By, locator: str, error_message: str) -> WebElement:
    """Encontra um único elemento, garantindo que ele seja clicável."""
    try:
        # Espera primeiro pela presença, depois por ser clicável, para ser mais robusto
        element = wait.until(EC.visibility_of_element_located((by, locator)))
        # Evita move out of bounds exception
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return element
    except TimeoutException:
        print(error_message)
        raise TimeoutException(error_message)

def _fill_text(driver: WebDriver, wait: WebDriverWait, id_input: str, text_to_send: str,
                      element_description: str):
    """ Preenche inputs de seleção com digitação com simulação (pausas)."""
    error_msg = f"[ ERRO ] O input de select '{element_description}' não foi encontrado ou não carregou."
    element = _find_element(driver, wait, By.NAME, id_input, error_msg)
    element.click()
    element.send_keys(text_to_send)

def _submit(driver: WebDriver, wait: WebDriverWait, value_input, element_description: str):
    """ Preenche inputs de seleção com digitação com simulação (pausas)."""
    error_msg = f"[ ERRO ] O input de select '{element_description}' não foi encontrado ou não carregou."
    element = _find_element(driver, wait, By.XPATH, value_input, error_msg)
    element.click()

# Sigaa scraping class
class Sigaa:
    def  __init__(self, console = None):
        self.console = console

    def getCurriculum(self):
        try:
            driver = Configure.create_driver(headless=True)
            url: str = "https://sigaa.uffs.edu.br"
            driver.get(url)
            time.sleep(3)

            # Login process
            wait = WebDriverWait(driver, 10)
            _find_element(driver, wait, By.XPATH, "//button[contains(text(), 'Ciente')]", "[Error dismissing consent button. ]").click()

            _fill_text(driver, wait, "user.login", os.getenv("SIGAA_USER"), "[ Error filling Sigaa user information. ]")
            _fill_text(driver, wait, "user.senha", os.getenv("SIGAA_PASS"), "[ Error filling Sigaa password information. ]")
            _submit(driver, wait, "//input[@type='submit' and contains(@value, 'Entrar')]", "[ Error submitting login form. ]")
            time.sleep(3)
            semester_information = parse_sigaa_portal(driver.page_source)
            print(semester_information)
            driver.quit()
            return semester_information

            while True:
                time.sleep(2)
        except Exception as err:
            traceback.print_exc()
            try:
                if driver is not None:
                    driver.quit()
                    return None
            except Exception:
                pass
        return None

