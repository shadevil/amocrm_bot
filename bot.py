import time, re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def params(query):
    with open('params', 'r') as file:
        for line in file:
            if query in line:
                tab_index = line.index('\t')
                return line[tab_index+1:].strip()

def reg_search(reg,query): return re.match(reg,query)

def start():

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(executable_path=r'chromedriver',chrome_options=chrome_options)

    driver.get(params('site'))
    driver.implicitly_wait(0.5)

    login = driver.find_element(by=By.ID, value="session_end_login")
    password = driver.find_element(by=By.ID, value="password")
    submit_button = driver.find_element(by=By.CLASS_NAME, value="auth_form__submit")

    login.send_keys(params('login'))
    password.send_keys(params('pass'))

    submit_button.click()
    main(driver)

def search(driver,cards):
    for card in cards:
        # card.click()
        wait = WebDriverWait(driver, 10)
        card.click()
        time.sleep(5)
        context = driver.find_element(by=By.CLASS_NAME, 
            value=params('context')).get_attribute("innerHTML")
        if(not reg_search(params('reg'),context) & reg_search(params('city'),context)):
        #     accept = driver.find_element(by=By.ID, value="card_unsorted_accept")
            time.sleep(5)
            print('MATCH')
            back = driver.find_elements(by=By.CLASS_NAME, 
                value="svg-icon svg-common--arrow-left-dims")
        #     accept.click()
            back.click()
            print(context)

def main(driver):
    wait = WebDriverWait(driver, 10)
    leads = wait.until(EC.element_to_be_clickable((By.XPATH, params('leads'))))
    leads.click()


    element_to_hover_over = driver.find_element(by=By.XPATH, value='//*[@id="list_page_holder"]/div')
    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()

    search(driver,driver.find_elements(by=By.CLASS_NAME, value="pipeline-unsorted__item-from"))
    # search(driver,driver.find_elements(by=By.CLASS_NAME, value="pipeline-unsorted__item-from"))

    driver.quit()

if __name__ == '__main__':
    start()