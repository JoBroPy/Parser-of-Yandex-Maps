from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from colorama import *
from Write_Data import main_for_two_file
# импортируем все нужные библиотки, и второй файл с нужней нам фукцией

DATA = []
num_of_page = 1
URL = "https://yandex.ru/maps"
init()

def get_links(source): # создаём функцию получения ссылок
    soup = BeautifulSoup(source, "lxml")
    many_links = soup.find("ul", class_="search-list-view__list").find_all("a", class_="search-snippet-view__link-overlay _focusable") # находим все ссылки на карточки с помощью find_all
    for i in many_links: # с помощью цикла собираем все ссылки и ложим их в список
        text = i.get("href")
        res_link = "https://yandex.ru" + text
        DATA.append(res_link)
    print(str(len(DATA)) + " - сколько ссылок на данный момент в txt-файле")

def pagenation(url, num): # функция для задавания новой страницы
    list_url = url.split("&")
    list_url[1] = "page=" + str(num)
    main_url = "&".join(list_url)

    return main_url

def save_in_txt(data): # сохраняем все ссылки в txt-файл
    with open("links.txt", 'a') as file:
        for line in data:
            file.write(line + "\n")

def scrolling_of_page(data_one, data_two): # функция прокуртки страницы
    try:
        driver.get(URL)
    except:
        print("Если высветилось данное изображение, то либо что-то с интернетом, толи с браузером, поэтому пожалуйста перезапустите программу.")
        driver.close()
        driver.quit()
    sleep(1)

    # тут программа вводит город, который указал пользователь
    driver.find_element(By.TAG_NAME, "input").send_keys(data_one)
    driver.find_element(By.TAG_NAME, "input").send_keys(" " + data_two)
    driver.find_element(By.TAG_NAME, "button").click()
    sleep(1.5)

    # тут она находит элемент кликает на него, тем самым регестрирует тег body для того, чтобы кнопки END и DOWN работали на странцие
    clickable_element = driver.find_element(By.CLASS_NAME, "search-list-view__content").find_element(By.TAG_NAME, "div")
    actions.click(clickable_element).perform()
    html = driver.find_element(By.TAG_NAME, "body")
    html.send_keys(Keys.END)
    get_links(driver.page_source)# находит все ссылки
    sleep(1)
    html.send_keys(Keys.END)
    sleep(1.5)

    return driver.current_url

def get_data_from_links():
    # тут пользоваетль вводит все необходимые данные
    N = num_of_page
    print(Fore.MAGENTA + Style.BRIGHT + "Введите город: ", end="")
    city_data = input()
    print(Fore.CYAN + Style.BRIGHT + "Введите что вы хотите найти: ", end="")
    what_data = input()

    try:
        url = scrolling_of_page(city_data, what_data)
    except:
        sleep(3)
        url = scrolling_of_page(city_data, what_data)

    # запускается цикл
    while True:
        N += 1
        print("Спаршена страница, у которой номер: " + str(N))
        link = pagenation(url, N)# происходит пагинация

        try:
            driver.get(link)
        except:
            print("Если высветилось данное изображение, то либо что-то с интернетом, толи с браузером, поэтому пожалуйста перезапустите программу.")
            driver.close()
            driver.quit()
        sleep(1.5)

        # проверка на то, что страница уже была спаршена, так как в яндекс картах есть особенность, когда
        # переходишь на страницу, где нету новых данных, она возвращает тебе данные с самой первой страницы
        if len(driver.find_element(By.CLASS_NAME, "seo-pagination-view").find_elements(By.TAG_NAME, "li")) == 1:
            break

        clickable_element = driver.find_element(By.CLASS_NAME, "search-list-view__content").find_element(By.TAG_NAME, "div")
        actions.click(clickable_element).perform()
        sleep(1)

        # прокручивает страницу именно DOWN, так как при прокрутке с END, много данных может просто не зафиксироваться на странице
        for i in range(111):
            html = driver.find_element(By.TAG_NAME, "body")
            html.send_keys(Keys.DOWN)

        try:
            get_links(driver.page_source)# даёт на всю странциу, чтобы получить ссылки снова
        except AttributeError:
            # если вдруг страница выдаст "Страница не найдена"
            if BeautifulSoup(driver.page_source, "lxml").find("div", class_="sidebar-container").find("div", class_="search-list-view").find("div", class_="nothing-found-view__header").text == "Ничего не найдено.":
                break

    save_in_txt(DATA)
    print(str(len(DATA)) + " - сколько ссылок в нашлось по данному запросу")
    sleep(5)
    return city_data

def main():
    name_city = get_data_from_links()
    return name_city

if __name__ == "__main__":
    timeheadless = bool(input("Хотите, чтобы программа работала в фоновом режиме(Если да, то напишете любое слово, если нет, то тогда вообще ничего не пишите): "))

    options = webdriver.ChromeOptions() # вводим опции хрома из селениума, чтобы можно было дабавить фоновый режим

    if timeheadless:
        options.headless = True # добавление фонового режима
    else:
        options.headless = False # недобавление фонового режима

    # создаём новый экземпляр класса селениума, хром-вебдрайвера
    driver = webdriver.Chrome \
        (
            executable_path=r"Chromedriver\chromedriver.exe",
            # здесь надо ввести свой путь к драйверу браузера(у всех драйверов своя
            # версия для каждой версии браузера), у меня он находиться в папке с названием "Chromedriver"
            options=options
        )

    # создаём новый экземпляр класса селениума, активные действия
    actions = ActionChains(driver)

    city_data = main()

    # полное закрытие браузера
    driver.close()
    driver.quit()

    # запуск функции из второго файла
    main_for_two_file(city_data)
