from selenium import webdriver
from selenium.webdriver.common.by import By
import winsound
from playsound import playsound
import time
from telethon import TelegramClient, events, sync
from datetime import datetime
import os
from termcolor import colored
import sys
import re
async def send_tg_message(message):
    # Me:       +380500369695
    # Elvira:   +380506701191
    await client.send_message('+380500369695', message)


def smart_sleep(delay):
    for remaining in range(delay, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("Trying again in{:2d} seconds".format(remaining))
        sys.stdout.flush()
        time.sleep(1)


def get_availability(url, *expected_sizes):
    if url != 'https://ludwig.gg/product/mogul-irrelevant-mockneck':
        print(colored("THIS LINK IS WRONG!!", 'red'))
        print(colored("THIS LINK IS WRONG!!", 'red'))
        print(colored("THIS LINK IS WRONG!!", 'red'))
    clear = lambda: os.system('cls')  # Create clear console lambda
    # driver setup
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2}  # experimental, do not load images for better performance
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    clear()
    driver.get(url)
    found = False
    expected_sizes = [size.upper() for size in expected_sizes]
    while not found:
        print(f'Last updated: {datetime.now().time()}')
        print('Expected sizes: ' + ", ".join(expected_sizes))

        driver.find_element(By.CSS_SELECTOR, '.MuiInputBase-formControl ').click()
        sizes = {}
        sizes_string = ''
        sizes_string_colorized = ''
        sizes_elements = driver.find_elements(By.CSS_SELECTOR, f'.MuiPaper-root li')
        for index, size in enumerate(sizes_elements):
            is_size_available = not size.get_attribute("aria-disabled") == 'true'
            size_name = size.get_attribute("data-value")
            if not size_name:
                continue
            if size is None:
                is_size_available = True
            sizes_string += f'\t{size_name}: { "**__Доступен__**" if is_size_available else "Недоступен"}\n'
            sizes_string_colorized += f'\t{size_name}: \t{colored("Available", "green")  if is_size_available else colored("Out Of Stock", "red")}\n'
            sizes[size_name] = is_size_available

        print(f'All available sizes:\n{sizes_string_colorized}')

        dict_keys_list = list(sizes.keys())
        dict_keys_list.sort()
        expected_sizes_results = {}
        expected_sizes_result_string = ''
        expected_sizes_result_string_eng = ''
        for key in dict_keys_list:
            if key in expected_sizes:
                expected_sizes_results[key] = sizes[key]
                expected_sizes_result_string += f'\t{key}: { "**__Доступен__**" if sizes[key] else "Недоступен"}\n'
                expected_sizes_result_string_eng += f'\t{key}: \t{colored("Available", "green")  if sizes[key] else colored("Out Of Stock", "red")}\n'

        if True in list(expected_sizes_results.values()):
            found = True
            string = f'Один из ожидаемых размеров появился в наличии:\n{expected_sizes_result_string}\nВсе размеры:\n{sizes_string}\n[Ссылка на товар]({url})'
            with client:
                client.loop.run_until_complete(send_tg_message(string))
            print(f'One or more of the expected sizes are now available!!\U0001F60D\U0001F60D\U0001F60D\n{expected_sizes_result_string_eng}')
        else:
            print(f'None of the expected sizes are available, sadge \U0001F972')
            smart_sleep(4)
            driver.refresh()
            clear()
    winsound.PlaySound('count_what_you_have.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
    input("Press Enter to continue...")
    driver.quit()


if __name__ == '__main__':
    while True:
        try:
            # Remember to use your own values from my.telegram.org!
            api_id = 800127
            api_hash = '35cf1557adbdd21e59b81bc0a22f2274'
            client = TelegramClient('test_session', api_id, api_hash)
            # CORRECT ONE https://ludwig.gg/product/mogul-irrelevant-mockneck !!!!
            # TEST: https://ludwig.gg/product/mogul-anemones-and-smiles-crewneck
            get_availability('https://ludwig.gg/product/mogul-irrelevant-mockneck', 'M')
        except:
            print("\n[Exception] ", sys.exc_info()[0])
            if sys.exc_info()[0] == KeyboardInterrupt:
                break
            continue
        break
