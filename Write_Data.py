from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from os import mkdir
import csv
# импортируем опять же всё что нам нужно

def dataes_append_in_csv_and_photos(webdriver, city):
    mkdir("Логотипы")
    mkdir("Фотки")
    n = 0# самый первый счётчик для счёта спаршенных карточек

    # открываем csv-файл и добавляем туда первую строчку c названиями колонок
    with open("MD.csv", "a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(
            ['Индетификатор', 'Название', 'Рейтинг', 'Город', 'Ближайшие станции метро', 'Адрес',
            'Координаты', 'Телефоны', 'e-mail', 'WhatsApp',
            'Telegram', 'Сайт (и соцсети)', 'Режим работы', 'Ссылка на логотип', 'Ссылки на фото']
        )


    def SF_metro(tag):# сортировачная функция для столбца "метро"
        try:
            li = tag.find("div", class_="masstransit-stops-view _type_metro _clickable").find_all("div")[-1].find_all("a")
            li_metro = []
            for i in li:
                li_metro.append(i.get_text())
            return ", ".join(li_metro)
        except:
            return "Нету данных в карточке"

    def SF_messendgers(tags_without_mess, mess):# сортировачная функция для столбцов "WhatsApp", 'Telegram', 'Сайт (и соцсети)'
        try:
            tags_with_mess = tags_without_mess.find_all("a", class_="button _view_secondary-gray _ui _size_medium _link")
            if tags_with_mess:
                data_mess = []
                for i in tags_with_mess:
                    if mess != "ВО":
                        if i.get("aria-label") == mess:
                            return i.get("href")
                    else:
                        if i.get("aria-label") != "Соцсети, whatsapp" or "Соцсети, telegram":
                            data_mess.append(i.get("href"))
                return ", ".join(data_mess)
        except:
            return "Нету данных в карточке"

    def SF_working_mode(working_list):# сортировачная функция для столбца "Режим работы"
        try:
            data_working_mode = []
            for i in working_list:
                data_working_mode.append(i.get("content"))
            str_wm = ", ".join(data_working_mode)
            new_str_wm = str_wm.replace("Mo", "Понедельник").replace("Tu", "Вторник").replace("We", "Среда").replace(
                "Th", "Четверг").replace("Fr", "Пятница").replace("Sa", "Суббота").replace("Su", "Воскресенье")
            return new_str_wm
        except:
            return "Нету данных в карточке"

    def save_logo(link):# функция для сохранения логотипа карточки
        try:
            main_link = link.find("img").get("src")
            webdriver.get(main_link)
            sleep(1)

            webdriver.get_screenshot_as_file(r"Логотипы\logo {}.png".format(id_of_card))# метод делает скриншот и сохраняет в файл-png
            webdriver.back()
            sleep(0.7)
            return main_link
        except:
            return "Нету данных в карточке"

    def SF_others(soupvid, gt=True, req=None):# функция сортировки для столбцов "Название", "Рейтинг", "Адрес", "Телефоны", "e-mail"
        try:
            if gt and req != True:
                text_from_tag = soupvid.get_text()
                return text_from_tag
            if req:
                tag = soupvid.find("span", class_="business-rating-badge-view__rating").find("span", class_="business-rating-badge-view__rating-text _size_m")
                return tag.get_text()
            else:
                text_from_div = soupvid.text
                return text_from_div
        except:
            return "Нету данных в карточке"

    def save_photos(xy):# функция для сохранения картинок в описании карточки
        data_for_photos = []
        t = 0 # счётчик заданной случайной переменной
        new_link_to_photos = f"https://yandex.ru/maps/org/{name_of_object_on_card}/{id_of_card}/gallery/?ll={xy[0]}&photos%5Bbusiness%5D={id_of_card}&{xy[1]}"

        webdriver.get(new_link_to_photos)
        sleep(0.7)
        p = BeautifulSoup(webdriver.page_source, "lxml").find_all("div", class_="photo-list__frame-wrapper")

        try:
            sh = 0# тоже счётчик, но уже в конструкции исключения
            mkdir("Фотки\\" + str(id_of_card))
        except FileExistsError:
            sh += 1
            if sh == 6:
                print("Происходит повтор ссылок, удалите все дубликаты в последних строках таблицы, и закройте программу)))")
                sleep(1000)
            else:
                pass

        for i in p:
            t += 1

            try:
                z = i.find("img").get("src")
            except:
                break

            data_for_photos.append(z)
            webdriver.get(str(z))
            sleep(0.7)

            webdriver.get_screenshot_as_file("Фотки\\" + str(id_of_card) + f"\\photo {t}.png")# тоже метод, который сохраняет фотки с описания, но уже в папку с названием в виде id карточки

        return ", ".join(data_for_photos)

    # открытие файла с ссылками и их чтение
    with open("links.txt", "r") as file:
        for i in file:
            n += 1
            try:
                webdriver.get(i.strip())
                sleep(0.7)
            except:
                sleep(2)
                webdriver.get(i.strip())

            soup = BeautifulSoup(webdriver.page_source, "lxml")

            id_of_card = webdriver.current_url.split("/")[6]# id карточки
            name_of_object_on_card = webdriver.current_url.split("/")[5]
            x_and_y = webdriver.current_url.split("/")[7].replace("?ll=", "").split("&")# координаты карточки

            # главный словарь со всеми данными, которые
            # потом будут сохраняться в csv
            data = {
                "Индетификатор": id_of_card,
                "Название": SF_others(soup.find("div", class_="sticky-wrapper _position_top _header _border_auto _wide").find("div", class_="orgpage-header-view__header-wrapper").find("h1", class_="orgpage-header-view__header")),
                "Рейтинг": SF_others(soup.find("div", class_="orgpage-header-view__wrapper"), req=True),
                "Город": city,
                "Ближайшие станции метро": SF_metro(soup.find("div", class_="card-transit-view")),
                "Адрес": SF_others(soup.find("a", class_="business-contacts-view__address-link")),
                "Координаты": webdriver.current_url.split("/")[7].replace("?ll=", "").replace("%2C", " ").split("&")[0],
                "Телефоны": SF_others(soup.find("div", class_="orgpage-header-view__contacts").find("div", class_="orgpage-phones-view__phone-number"), gt=False),
                "e-mail": SF_others(soup.find("span", class_="business-urls-view__text")),
                "WhatsApp": SF_messendgers(soup.find("div", class_="card-feature-view _view_normal _size_small _no-side-padding business-contacts-view__social-links"), "Соцсети, whatsapp"),
                "Telegram": SF_messendgers(soup.find("div", class_="card-feature-view _view_normal _size_small _no-side-padding business-contacts-view__social-links"), "Соцсети, telegram"),
                "Сайт (и соцсети)": SF_messendgers(soup.find("div", class_="card-feature-view _view_normal _size_small _no-side-padding business-contacts-view__social-links"), "ВО"),
                "Режим работы":SF_working_mode(soup.find_all("meta", {"itemprop":"openingHours"})),
                "Ссылка на логотип": save_logo(soup.find("div", class_="orgpage-photos-view__logo")),
                "Ссылки на фото": save_photos(x_and_y)
            }

            # открывает csv-файл и добавляет из словаря данные в столбцы
            with open("MD.csv", "a", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(
                    [data["Индетификатор"], data["Название"], data["Рейтинг"], data["Город"], data["Ближайшие станции метро"],
                     data["Адрес"], data["Координаты"], data["Телефоны"], data["e-mail"], data["WhatsApp"], data["Telegram"],
                     data["Сайт (и соцсети)"], data["Режим работы"], data["Ссылка на логотип"], data["Ссылки на фото"]]
                )

            print("В таблицу добавилась карточка номер {}".format(n))


def main_for_two_file(city_for_func):# главная функция вызывающая весь процесс добавления данных
    options = webdriver.ChromeOptions()
    options.headless = True

    driver = webdriver.Chrome(
        executable_path=r"Chromedriver\chromedriver.exe",# здесь также, как и в Main.py файле
        chrome_options=options
    )

    dataes_append_in_csv_and_photos(driver, city_for_func)

    driver.close()
    driver.quit()

