import time, re, getpass, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

xpath_dict = {
    "leads": "//a[@href='/leads/']",

    "overlay": "left-menu-overlay",

    "datetime": "//*[@class='feed-note  feed-note-system-common'] /*/*/*/*/*[@class='feed-note__date']",

    "purchases_main": "//div[1]/div/div/div/div/a[@class='pipeline_leads__title-text h-text-overflow js-navigate-link']",

    "purchases_partner": "//div[@class='pipeline-unsorted__item-from']",

    "purchase_link": ".//div[1]/div[1]",

    "purchase_info": ".//div[2]/div[2]",

    "info": "//div[contains(@title,'Город')]",

    "content_main": "//div[@class='note--body--content-not-sliced__scroll-wrapper custom-scroll']/p",

    "content_partner": "//*[@id='card_holder']/div[3]/div/div[1]/div/div[2]/div[5]/div/div/div[2]/div[2]/div[2]/div/p",

    "back": "//div[@class='js-back-button card-fields__top-back']"
}

reg_dict = {    
    "reg": "(?i)(?:\w*)?(?:вебхук|api|cайты24|php|разработать|help[ -]?desk|интернет[ -]?магазин|маркет|бесплатн|розничн(?:ая|ой|ые|ых|ую) торговл(?:е|я|и|ей|ю))(?:\w*)",

    "city": "(?i)(?:\w*)?(?:уфа|москва|санкт-петербург)(?:\w*)"
}
def match_log(matches):
    if matches:
        for match in matches:
            print("#LOG         Match found: " + match)

def auth_data():
    if not os.path.exists('auth'):
        site = input("Введите сайт(без https://): ")
        set_auth_data('site','https://' + site)

        login = input("Введите логин: ")
        set_auth_data('login',login)

        password = getpass.getpass("Введите пароль: ")
        set_auth_data('password',password)

def get_auth_data(query):
    file = 'auth'
    with open(file, 'r') as file:
        for line in file:
            if query in line:
                tab_index = line.index('\t')
                return line[tab_index+1:].strip()

def set_auth_data(type,data):
    with open("auth", "a") as f:
        f.write(type + '\t' + data + "\n")

def reg_search(reg,query): return re.findall(reg, query)

def start():
    auth_data()
    site = get_auth_data('site')
    login = get_auth_data('login')
    password = get_auth_data('password')

    if(site != '' and login != '' and password != ''):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(executable_path=r'chromedriver.exe',options=chrome_options)

        driver.get(site)
        driver.implicitly_wait(0.5)

        login_el = driver.find_element(by=By.ID, value="session_end_login")
        password_el = driver.find_element(by=By.ID, value="password")
        submit_button = driver.find_element(by=By.CLASS_NAME, value="auth_form__submit")

        login_el.send_keys(login)
        password_el.send_keys(password)

        submit_button.click()
        move_to_purchases(driver)
    else: print('DATA WAS NOT FOUND')    

def search(driver,type):    
    # FIXME: accept button, time sleep, enable loop
    # while True:
    wait = WebDriverWait(driver, 10)
    print("====================================")
    print('PURCHASES TYPE ' + 'purchases_'+type)
    print("====================================")
    cards = driver.find_elements(by=By.XPATH, value=xpath_dict['purchases_'+type])
    print('LEN ' + str(len(cards)))      
    print(type.upper())
    time.sleep(3)
    for card in cards:
        print(card.get_attribute('innerHTML'))
        wait.until(EC.element_to_be_clickable(card)).click()
        print("====================================")
        print('CONTENT TYPE ' + 'content_'+type)
        print("====================================")
        elements = wait.until(EC.visibility_of_any_elements_located((By.XPATH, xpath_dict['content_'+type]))) 
        print("LEN " + str(len(elements)))
        back = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dict['back'])))
        print("====================================")
        for x in elements:
            print(str(x.get_attribute('innerHTML')))
            
            
            
        # #     #//////////////////////
        # #     print(str(i) + " " + content)
        # #     i = i + 1
        # #     #//////////////////////
        # #     reg = reg_search(read_value('reg'),content)
        # #     city = reg_search(read_value('city'),content)
        # #     match_log(reg)
        # #     match_log(city)
            
        # #     if(not reg and city):
        # # #     accept = driver.find_element(by=By.ID, value="card_unsorted_accept")
        # #         print('MATCH')
        # # # #     accept.click()
        print("====================================")
        back.click()

def move_to_purchases(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dict['leads']))).click()

    action = webdriver.ActionChains(driver)
    element = wait.until(EC.visibility_of_element_located((By.ID, xpath_dict['overlay'])))
    action.move_to_element(element)
    action.perform()

    # search(driver,'partner')
    search(driver,'main')
    
    driver.quit()

if __name__ == '__main__':
    start()