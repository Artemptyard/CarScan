import base64
import logging
import time
from typing import List
from enum import Enum, auto

from PIL import Image
from io import BytesIO
from dataclasses import dataclass
from selenium import webdriver, common
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from data.appdata.carinfo import CarInfo, Accident, DEFAULT
from data.appdata.functions import stop_program, save_json
from data.appdata.mycaptchasolver import MyCaptchaSolver


class ParserResults(Enum):
    """Результаты работы парсера

    Ok: Получена информация.
    Error: Ошибка при парсинге.
    NotFound: Информации нет.
    """
    Ok = auto()
    Error = auto()
    NotFound = auto()
    Skipped = auto()


@dataclass
class ParserOptions:
    """Настройки парсера.

    try_count (int): Количество попыток CapGuru прочесть текстовую капчу.
    sleep: Время между попытками CapGuru прочесть текстовую капчу.
    load_try_count: количество попыток найти картинки (капчи) на сайте (она загружается не быстро).
    delay: Время между проверками картинки (капчи) на сайте.
    """
    try_count: int = 10
    load_try_count: int = 10
    sleep: int = 5
    delay: int = 5


class MyParser:
    """Класс для получения данных"""
    car_info: CarInfo
    driver: webdriver.Firefox
    options: ParserOptions

    def __init__(self, license_number: str = None, license_region: str = None, vin_number: str = None,
                 car_info: CarInfo = None, options: ParserOptions = ParserOptions()):
        """
        :param license_number: госномер.
        :param license_region: регион от госномера.
        :param vin_number: vin номер. Если он не передан, то он сразу будет получен.
        :param car_info: класс информации о автомобиле.
        """
        if vin_number is None and license_number is None and license_region is None and car_info is None:
            raise Exception("To find information about car, you should have license number "
                            "and license region or vin number")
        self.options = options
        if car_info is not None:
            self.car_info = car_info
            return
        self.car_info = CarInfo()
        self._driver_settings()
        if license_number is not None and license_region is not None:
            self.car_info.license_number = license_number
            self.car_info.license_region = license_region
        elif license_number is not None:
            self.car_info.license_number = license_number
            self._check_licence()
        if vin_number is not None:
            self.car_info.vin_number = vin_number
        # else:
        #     self._try_get_vin()

    def _check_licence(self):
        """Проверка госномера и его региона"""
        if len(self.car_info.license_number) > 6 and self.car_info.license_region == DEFAULT:
            self.car_info.license_region = self.car_info.license_number[6:]
            self.car_info.license_number = self.car_info.license_number[:6]
        if len(self.car_info.license_number) != 6:
            raise Exception("Incorrect licence number")
        if self.car_info.license_region == DEFAULT or len(self.car_info.license_region) == 0:
            raise Exception("Incorrect licence region")

    def _try_get_vin(self):
        """Получение vin номера"""
        result = self.parse_vin()
        while result == ParserResults.Error:
            result = self.parse_vin()
        if result == ParserResults.NotFound:
            raise Exception("There is no vin number")

    def _driver_settings(self) -> None:
        """Настройка веб-драйвера"""
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--disable-audio')
        options.add_argument('--mute-audio')
        # options.headless = True
        self.driver = webdriver.Firefox(options=options)
        # self.driver.install_addon(
        #     "C:/Users/drako/AppData/Roaming/Mozilla/Firefox/Profiles/i28787xu.default-release/extensions/adblockultimate@adblockultimate.net.xpi")
        # self.driver.install_addon(
        #     "C:/Users/drako/AppData/Roaming/Mozilla/Firefox/Profiles/i28787xu.default-release/extensions/uBlock0@raymondhill.net.xpi")
        # self.driver.install_addon(
        #     "C:/Users/drako/AppData/Roaming/Mozilla/Firefox/Profiles/i28787xu.default-release/extensions/jid1-NIfFY2CA8fy1tg@jetpack.xpi")
        self.driver.implicitly_wait(15)

    def _screenshot(self, name: str, log_level: int = logging.DEBUG) -> None:
        """Делать скриншоты страниц учитывая уровень логирования.

        :param name: Названия скриншота для сохранения."""
        # Если уровень логирования в консоль равен log_level
        if logging.getLogger().handlers[1].level <= log_level:
            self.driver.save_full_page_screenshot(f"data/img/{name}.png")

    def _pass_captcha(self) -> str:
        """Прохождение текстовой капчи

        :return: Текст с картинки.
        """
        solver = MyCaptchaSolver(self.driver, try_count=self.options.try_count, sleep=self.options.sleep)
        do = True
        while do:
            try:
                value = solver.get_captcha_value_vin2vin(self.options.delay, self.options.load_try_count)
                do = False
            except Exception:
                time.sleep(10)
        return value

    def _fill_vin(self):
        """Заполнение полей на сайте: VIN и текстовая капча."""
        logging.info("Start filling data to vin2vin")
        captcha_value = self._pass_captcha()
        input_text_vin = self.driver.find_element(By.ID, 'exampleInputEmail2')
        input_text_vin.send_keys(self.car_info.vin_number)
        input_text_captcha = self.driver.find_element(By.ID, 'exampleInputPassword2')
        input_text_captcha.send_keys(captcha_value)
        self._screenshot("filled_vin")

    def _get_parser_with_vin(self, url: str = "https://vin2vin.ru/history") -> bool:
        """
        Прохождение текстовой капчи.

        :param url: Ссылка на сайт для парсинга.
        :return: Успешна ли операция.
        """
        self.driver.get(url)
        try:
            self._fill_vin()
            logging.info("Opening vin2vin page")
            WebDriverWait(self.driver, 15)
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_btn.click()
            WebDriverWait(self.driver, 10)
            self._screenshot("pressed")
        except Exception as err:
            self._screenshot("other_page_error", logging.ERROR)
            logging.error(f"Error was caused while site parsing", exc_info=True)
            return False
        return True

    def _pass_captcha_gibdd(self) -> str:
        """Прохождение текстовой капчи на сайте ГИБДД.

        :return: Текст с картинки. '-1' - Если ошибка.
        """
        solver = MyCaptchaSolver(self.driver, try_count=self.options.try_count, sleep=self.options.sleep)
        do = True
        while do:
            try:
                value = solver.get_captcha_value_gibdd(self.options.delay, self.options.load_try_count)
                do = False
            except TimeoutError:
                logging.error("Error while captcha load", exc_info=True)
                return '-1'
            except Exception:
                time.sleep(10)
        return value

    def _fill_captcha(self):
        """Заполнение поля на сайте ГИБДД: текстовая капча."""
        self._open_captcha()
        captcha_value = self._pass_captcha_gibdd()
        while captcha_value == '-1':
            self.driver.refresh()
            time.sleep(2)
            self._open_captcha()
            captcha_value = self._pass_captcha_gibdd()
        input_text_captcha = self.driver.find_element(By.NAME, 'captcha_num')
        input_text_captcha.send_keys(captcha_value)
        self._screenshot("gibdd_filled")

    def _open_captcha(self):
        """Открытие капчи на сайте ГИБДД"""
        time.sleep(5)
        input_text_vin = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'checkAutoVIN')))
        # input_text_vin = self.driver.find_element(By.ID, 'checkAutoVIN')
        input_text_vin.send_keys(self.car_info.vin_number)
        check_btn = self.driver.find_element(By.LINK_TEXT, "запросить сведения о ДТП")
        time.sleep(5)
        check_btn.click()
        time.sleep(5)
        self._screenshot("gibdd_opened")

    def _get_parser_gibdd(self, url: str = "https://xn--90adear.xn--p1ai/check/auto") -> bool:
        """
        Прохождение текстовой капчи на сайте ГИБДД.

        :param url: Ссылка на сайт для парсинга.
        :return: Успешна ли операция.
        """
        self.driver.get(url)
        try:
            self._fill_captcha()
            WebDriverWait(self.driver, 15)
            try:
                submit_btn = self.driver.find_element(By.ID, 'captchaSubmit')
                submit_btn.click()
            except Exception:
                logging.info("Captcha was disappeared")
            WebDriverWait(self.driver, 10)
            time.sleep(10)
            self._screenshot("gibdd_pressed")
        except Exception as err:
            self._screenshot("other_page_error", logging.ERROR)
            logging.error(f"Error was caused while site parsing", exc_info=True)
            return False
        return True

    def _fill_license(self):
        """Заполнения в полей на сайте: Госномер и регион."""
        input_text_number = WebDriverWait(self.driver, timeout=10).until(lambda d: d.find_element(By.ID, 'exampleInputEmail2'))
        # input_text_number = self.driver.find_element(By.ID, 'exampleInputEmail2')
        input_text_number.send_keys(self.car_info.license_number)
        input_text_region = self.driver.find_element(By.ID, 'exampleInputPassword2')
        input_text_region.send_keys(self.car_info.license_region)
        self._screenshot("filled_licence")

    def _pass_recaptcha(self) -> str:
        """Прохождение рекапчи.

        :return: Код решённой капчи. '-1' - Если капча не решена."""
        solver = MyCaptchaSolver(self.driver, try_count=self.options.try_count, sleep=self.options.sleep)
        do = True
        while do:
            try:
                result = solver.pass_recaptcha()
                do = False
            except Exception:
                time.sleep(10)
                result = solver.get_captcha_value_vin2vin(self.options.delay, self.options.load_try_count)
        return result

    def _get_parser(self) -> bool:
        """Прохождение рекапчи для получения vin номера.

        :return: Успешна ли операция."""
        self.driver.get("https://vin2vin.ru/getvin")
        try:
            self._fill_license()
            WebDriverWait(self.driver, 15)
            code = self._pass_recaptcha()
            recaptcha_response_element = self.driver.find_element(By.ID, 'g-recaptcha-response')
            self.driver.execute_script(f'arguments[0].value = "{code}";', recaptcha_response_element)
            self._screenshot("solved")
            time.sleep(10)
            try:
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_btn.click()
            except:
                self.driver.save_full_page_screenshot("error.png")
            time.sleep(10)
            self._screenshot("opened")
        except Exception:
            self._screenshot("vin_page_error", logging.ERROR)
            logging.error(f"Error was caused while site parsing", exc_info=True)
            return False
        return True

    def _crop_accident_screenshot(self, x: int, y: int, width: int, height: int, padding: int = 25) -> Image:
        """Обрезка скриншота, чтобы получить информацию об авариях

        :param x: Начало по x (слева).
        :param y: Начало по y (слева).
        :param width: Ширина обрезки.
        :param height: Высота обрезки.
        :param padding: Отступ от краёв.
        :return: Обрезанная картинка.
        """
        x -= padding
        width += padding
        screenshot = self.driver.get_full_page_screenshot_as_png()

        img = Image.open(BytesIO(screenshot))
        cropped_img = img.crop((x, y, x + width, y + height))
        return cropped_img

    def _is_accidents(self, content: WebElement) -> bool:
        """Проверка, есть ли ДТП, или они не были загружены

        :param content: div-список с ДТП.
        :return: Результат проверки.
        """
        msg = "В результате обработки запроса к АИУС ГИБДД записи о дорожно-транспортных происшествиях не найдены."
        ps = content.find_elements(By.TAG_NAME, 'p')
        for p in ps:
            if p.text == msg:
                logging.info("There was no accident")
                return False
        logging.error("Result div was None")
        return True

    def _get_accident_imgs(self, content: List[WebElement], titles: List[WebElement]) -> None:
        """Разбиение всех дтп на отдельные скрины

        :param content: Список всех дтп (tag name: li)
        """
        # Начало дтп (hr имеет размер)
        hr_elements = self.driver.find_elements(By.TAG_NAME, 'hr')
        y = 0
        for i in range(len(titles)):
            li = content[i]
            title = titles[i].text
            name = title[title.find("№") + 1:]
            path = f"data/users/dtp№{name}.png"

            content_location = li.location
            # hr[1] - конец блока о дтп
            hr_size = hr_elements[1].size
            hr_location = hr_elements[1].location

            x = content_location['x']
            if i == 0: y = content_location['y']

            width = hr_location['x'] - x + hr_size['width']
            if i + 1 == len(titles):
                height = hr_location['y'] - y
            else:
                height = titles[i + 1].location['y'] - y

            img = self._crop_accident_screenshot(x, y, width, height)
            self.car_info.accidents.append(Accident(path))
            img.save(path)
            y += img.height - 10

    def _parse_page(self, parser_result: bool) -> ParserResults:
        """Парсинг страницы

        :param parser_result: Получен ли доступ к странице.
        :return: Результат парсинга.
        """
        if parser_result:
            logging.info("Start of GIBDD pages parsing")
            # div вкладки о дтп
            div_accident = self.driver.find_element(By.ID, "checkAutoAiusdtp")
            # div результата при прохождении капчи
            div_result = div_accident.find_element(By.CLASS_NAME, "checkResult")
            try:
                # Список всех дтп
                ul = div_result.find_element(By.CLASS_NAME, "aiusdtp-list")
                content = ul.find_elements(By.TAG_NAME, "li")
                titles = ul.find_elements(By.CLASS_NAME, "ul-title")
            except common.exceptions.NoSuchElementException:
                # Либо нет дтп, либо реклама помешала парсингу
                return ParserResults.Error if self._is_accidents(div_accident) else ParserResults.NotFound
            if len(titles) > len(content) or len(content) == 0:
                return ParserResults.Error if self._is_accidents(div_accident) else ParserResults.NotFound
            self._get_accident_imgs(content, titles)
            return ParserResults.Ok
        else:
            logging.error("Parsing was failed")
            return ParserResults.Error

    def parse_accident(self) -> ParserResults:
        """Получаем данные со страницы о ДТП автомобиля:

        https://xn--90adear.xn--p1ai/check/auto.

        :return: Результат парсинга."""
        logging.info("Start of accident parsing")
        return self._parse_page(self._get_parser_gibdd("https://xn--90adear.xn--p1ai/check/auto"))

    def _parse_table(self, parser_result: bool) -> ParserResults:
        """Парсинг таблицы со страницы

        :param parser_result: Получен ли доступ к странице.
        :return: Получилось ли получить данные.
        """
        if parser_result:
            logging.info("Start of tabel parsing")
            try:
                tables = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
            except common.exceptions.NoSuchElementException as ex:
                self._screenshot("Table wasn't found")
                logging.error("Table wasn't found")
                return ParserResults.NotFound
            except common.exceptions.TimeoutException:
                logging.error("Table wasn't found")
                return ParserResults.NotFound
            except Exception as ex:  # Непредвиденная ошибка
                logging.critical("Table wasn't found", exc_info=True)
            dictionary: {str: str} = {}
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    key = str(cells[0].text).replace(':', '').strip()
                    if key == "VIN номер":
                        if len(cells[1].text.strip()) == 0:
                            logging.info("There is no info about car")
                            return ParserResults.NotFound
                        if cells[1].text.strip() == DEFAULT:
                            logging.error("There was an error while parsing")
                            return ParserResults.Error
                    dictionary[key] = cells[1].text.strip()
            try: self.car_info.set_dictionary(dictionary)
            except Exception:
                logging.error("Dictionary set was failed:", exc_info=True)
                return ParserResults.Error
            finally:
                save_json(self.car_info.get_dictionary(True), self.car_info.vin_number)
            return ParserResults.Ok
        else:
            logging.error("Parsing was failed")
            return ParserResults.Error

    def parse_vin(self) -> ParserResults:
        """Получение данных о vin номере:

        https://vin2vin.ru/getvin.

        :return: Результат парсинга."""
        logging.info("Start of vin parsing")
        return self._parse_table(self._get_parser())

    def parse_history(self) -> ParserResults:
        """Получаем данные со страницы об истории автомобиля:

        https://vin2vin.ru/history.

        :return: Результат парсинга."""
        logging.info("Start of history parsing")
        return self._parse_table(self._get_parser_with_vin("https://vin2vin.ru/history"))

    def parse_limits(self) -> ParserResults:
        """Получаем данные со страницы о лимитах автомобиля:

        https://vin2vin.ru/restricted.

        :return: Результат парсинга."""
        logging.info("Start of limits parsing")
        return self._parse_table(self._get_parser_with_vin("https://vin2vin.ru/restricted"))

    def parse_hijacking(self) -> ParserResults:
        """Получаем данные со страницы об угоне автомобиля:

        https://vin2vin.ru/wanted.

        :return: Результат парсинга."""
        logging.info("Start of hijacking parsing")
        return self._parse_table(self._get_parser_with_vin("https://vin2vin.ru/wanted"))

    def parse_inspection(self) -> ParserResults:
        """Получаем данные со страницы о техосмотре автомобиля:

        https://vin2vin.ru/eaisto.

        :return: Результат парсинга."""
        logging.info("Start of inspection parsing")
        return self._parse_table(self._get_parser_with_vin("https://vin2vin.ru/eaisto"))

    def __del__(self):
        try: self.driver.quit()
        except Exception as e:
            logging.info("Error closing driver:", exc_info=True)
