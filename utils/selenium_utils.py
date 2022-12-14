from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


def get_driver(options=None, driver_path=r'D:\servers\chromedriver_win32_83\chromedriver.exe'):
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def open_chrome(driver, url):
    driver.get(url)


def get_html(driver):
    return driver.execute_script("return document.documentElement.outerHTML")





def close(driver):
    if driver:
        driver.close()
    if driver:
        driver.quit()
