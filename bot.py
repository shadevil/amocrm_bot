import time, re, getpass, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

global site, login, password

def read_value(query,file):
    with open(file, 'r') as file:
        for line in file:
            if query in line:
                tab_index = line.index('\t')
                return line[tab_index+1:].strip()

def auth_data():
    if not os.path.exists('auth'):
        site = input("Введите сайт(без https://): ")
        set_auth_data('site','https://' + site)

        login = input("Введите логин: ")
        set_auth_data('login',login)

        password = getpass.getpass("Введите пароль: ")
        set_auth_data('password',password)

def reg_search(reg,query): return re.match(reg,query)

def set_auth_data(type,data):
    with open("auth", "a") as f:
        f.write(type + '\t' + data + "\n")

def start():
    auth_data()
    site = read_value('site','auth')
    login = read_value('login','auth')
    password = read_value('password','auth')

    if(site != '' and login != '' and password != ''):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(executable_path=r'chromedriver',options=chrome_options)

        driver.get(site)
        driver.implicitly_wait(0.5)

        login_el = driver.find_element(by=By.ID, value="session_end_login")
        password_el = driver.find_element(by=By.ID, value="password")
        submit_button = driver.find_element(by=By.CLASS_NAME, value="auth_form__submit")

        login_el.send_keys(login)
        password_el.send_keys(password)

        submit_button.click()
        main(driver)
    else: print('DATA WAS NOT FOUND')

def search(driver,cards):
    # FIXME: enable loop, time.sleep, accept button
    # white True:
    for card in cards:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, read_value('purchases','params'))))
        card.click()

        contents = driver.find_elements(by=By.XPATH, value=read_value('contents','params'))
        for x in contents:
            content = x.innerHTML()
            print(content)
            if(not reg_search(read_value('reg','params'),content) & reg_search(read_value('city','params'),content)):
        #     accept = driver.find_element(by=By.ID, value="card_unsorted_accept")
                print('MATCH')
                back = driver.find_elements(by=By.CLASS_NAME, value=read_value('back','params'))
        #     accept.click()
                back.click()
            # time.sleep(600)

def main(driver):
    wait = WebDriverWait(driver, 10)
    leads = wait.until(EC.element_to_be_clickable((By.XPATH, read_value('leads','params'))))
    leads.click()

    left_menu_overlay = wait.until(EC.element_to_be_clickable((By.ID, "left-menu-overlay")))
    left_menu_overlay.click()

    links = driver.find_elements(by=By.XPATH, value=read_value('purchases','params'))
    search(driver,links)
    # links = wait.until(EC.element_to_be_clickable((By.XPATH, read_value('purchase','params'))))
    # search(driver,links)
    # element_to_hover_over = driver.find_element(by=By.XPATH, 
    #     value='//*[@id="list_page_holder"]/div')
    # hover = ActionChains(driver).move_to_element(element_to_hover_over)
    # hover.perform()

    # search(driver,driver.find_elements(by=By.CLASS_NAME, value="pipeline-unsorted__item-from"))
    # links = driver.find_elements(by=By.XPATH, value=read_value('purchase','params'))
    # search(driver,links)

    driver.quit()

if __name__ == '__main__':
    start()