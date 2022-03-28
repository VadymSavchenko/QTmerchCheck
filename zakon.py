from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from telethon import TelegramClient, events, sync
from datetime import datetime
import os
import re
import traceback
import sys

async def send_tg_message(message):
    # Me:       +380500369695
    # Me2:      +380676534100
    # Elvira:   +380506701191
    await client.send_message('Ukraine_Laws_Tracker', message)


def smart_sleep(delay):
    for remaining in range(delay, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("Waiting for {:2d} seconds".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.flush()
    sys.stdout.write("\r")


def setup_driver():
    # driver setup
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2}  # experimental, do not load images for better performance
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    return driver


def get_id_file(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        f = open(filename, "r")
        ids = f.read()
        ids = list(filter(None, ids.split("\n")))
        f.close()
    else:
        ids = []
        f = open(filename, "w+")
        f.close()
    return ids

def get_laws_project():
    driver = setup_driver()
    driver.get('https://www.rada.gov.ua/news/zpn')
    print(f'Last updated: {datetime.now().time()}')

    ids = get_id_file("law_id.txt")

    laws_list = driver.find_elements(By.CSS_SELECTOR, '.timeline-block')
    for index, law in enumerate(laws_list):
        url = law.find_element(By.CSS_SELECTOR, '.timeline-block__heading a').get_attribute("href")
        header = law.find_element(By.CSS_SELECTOR, '.timeline-block__heading a').text
        law_id = re.search(r'\(№ (.*)\)', header).group(1)
        description = law.find_element(By.CSS_SELECTOR, '.timeline__conteiner p').text
        time = law.find_element(By.CSS_SELECTOR, '.time').text
        date = law.find_element(By.CSS_SELECTOR, '.timeline-block__date').text
        string = f'**__\U00002754Новий законопроект\U00002754 №{law_id} від {date}, {time}__**:\n{description}\n[Посилання]({url})'
        if law_id in ids:
            print(f'Law {str(law_id)} was already published')
        else:
            latest_law_id = law_id
            f = open("law_id.txt", "a")
            f.write(str(latest_law_id) + "\n")
            f.close()
            with client:
                client.loop.run_until_complete(send_tg_message(string))
            print(string)
            smart_sleep(5)
    driver.quit()


def get_accepted_laws():
    driver = setup_driver()
    driver.get('https://zakon.rada.gov.ua/laws/main/n')
    print(f'Last updated: {datetime.now().time()}')

    law_institutions_emojis = {
        'Національного банку України': '🏦',
        'Президента України': '🤴',
        'Кабінету Міністрів України': '🏛',
        'РНБО': '(🛡🛡Рада національної безпеки і оборони України🛡🛡)'
    }

    law_types_emojis = {
        'Постанова': '',
        'Указ': '',
        'Розпорядження': '',
    }

    statuses = {
        'Чинний': '✅'
    }

    law_explanations = {
        'Постанова': 'Постанова - правовий акт, що приймається найвищими і деякими центральними органами колегіального управління (комітетами, комісіями) з метою вирішення важливих і принципових задач, що стоять перед даними органами.\nУ постановах розкривають господарські, політичні й організаційні питання. Часто за допомогою постанов затверджують різні нормативні документи (типові інструкції, нормативи тощо).',
        'Указ': 'За своєю юридичною силою й характером укази Президента України є актами прямої дії та мають однакову юридичну силу на всій території України',
        'Розпорядження': "Розпорядження - це акт управління посадової особи, державного органу, організації, що виданий у межах їхньої компетенції.\nМає обов'язкову юридичну силу щодо громадян (працівників) та підлеглих організацій, яким адресовано розпорядження",
    }

    ids = get_id_file('acepted_act_id.txt')

    laws_list = driver.find_elements(By.CSS_SELECTOR, '.doc-list li')

    for index, law in enumerate(laws_list[::-1]):
        url = law.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")
        description = law.find_element(By.CSS_SELECTOR, 'a').text
        header = law.find_element(By.CSS_SELECTOR, '.doc-card').text
        is_active_string = law.find_element(By.CSS_SELECTOR, 'a').get_attribute("alt")
        # Parse
        institution = [word for word in law_institutions_emojis if word in header]
        law_type = [word for word in law_explanations if word in header]
        date = re.search(r'\d\d\.\d\d\.\d\d\d\d', header).group(0)
        law_id_friendly = re.search(r'(№ .*)', header)
        law_id_real = driver.execute_script("""
                                            return jQuery(arguments[0]).contents().filter(function() {
                                            return this.nodeType == Node.TEXT_NODE;
                                            }).text();
                                            """, law.find_element(By.CSS_SELECTOR, 'small'))
        if law_id_friendly:
            law_id = law_id_friendly.group(1)
        else:
            law_id = f'ID: {law_id_real}'
        if law_id_real in ids:
            print(f'[{index+1}] Law {law_id_real} ({law_id}) was already published')
        else:
            if institution and law_type:
                inst_emoji = law_institutions_emojis[institution[0]]
                formatted_header = f'{inst_emoji}{law_type[0]} {institution[0]}{inst_emoji}'
                formatted_description = f'\n\nОпис документа:\n```{law_explanations[law_type[0]]}```'
            else:
                formatted_header = header
                formatted_description = ''
            if is_active_string in statuses:
                status_emoji = statuses[is_active_string]
            else:
                status_emoji = '❓'
            status_formatted = f'{status_emoji}{is_active_string}{status_emoji}'
            found = [ele for ele in ['приз', 'мобілізац', 'військ', 'оборон', 'студ', 'відстр'] if (ele in description.lower())]
            marked_text = ''
            for el in found:
                description = description.replace(el, f'⚔⚔⚔{el}')
                marked_text = f'\n```marked```'
            string = f'**__{formatted_header} {law_id} від {date}__**:\n{description}\n{status_formatted}{marked_text}{formatted_description}\n[Посилання]({url})\n'
            with client:
                client.loop.run_until_complete(send_tg_message(string))
            print(f'[#{index+1} of {len(laws_list)}] Sending {law_id_real} ({law_id})')
            smart_sleep(15)
            f = open("acepted_act_id.txt", "a")
            f.write(str(law_id_real) + "\n")
            f.close()
    driver.quit()


if __name__ == '__main__':
    while True:
        try:
            # values from my.telegram.org
            api_id = 800127
            api_hash = '35cf1557adbdd21e59b81bc0a22f2274'
            client = TelegramClient('law_session_vodafone', api_id, api_hash)
            get_laws_project()
            get_accepted_laws()
            smart_sleep(320)
        except:
            print("\n[Exception] ", sys.exc_info()[0])
            print(traceback.format_exc())
            if sys.exc_info()[0] == KeyboardInterrupt:
                break
            continue
