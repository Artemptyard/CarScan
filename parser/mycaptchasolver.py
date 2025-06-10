import requests
import logging
import time
import datetime as dt
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from data.appdata.functions import stop_program, get_image_bytes


@dataclass
class MyCaptchaSolver:
    """Решение капчей всех типов"""
    driver: webdriver.Firefox
    key: str = "***"
    try_count: int = 10
    sleep: int = 3

    def __post_init__(self):
        """"""

    def get_wallet(self) -> int:
        """Функция для получения текущего баланса"""
        balance = int(requests.get(f"https://api.cap.guru/res.php?action=getbalance&key={self.key}").text)
        logging.info(f"Current balance received - Cap Guru: ~{balance} rub")
        return balance

    def _check_wallet(self) -> None:
        """Проверка баланса"""
        balance = self.get_wallet()
        if balance < 5:
            logging.warning("Running out of balance - Cap Guru")
        if balance <= 0:
            logging.critical("Out of balance - Cap Guru")
            stop_program("Out of balance - Cap Guru")

    def _captcha_solving(self, req_id: str) -> str:
        """Ожидание решения капчи"""
        logging.info("Start of captcha solving")
        for _ in range(self.try_count):
            res = requests.get(f"https://api.cap.guru/res.php?key={self.key}&action=get&id={req_id}")
            if res.text.find('CAPCHA_NOT_READY') > -1:
                logging.debug("The captcha is not ready yet")
                time.sleep(self.sleep)
            elif res.text.find('ERROR') > -1:
                logging.error(f"The captcha in the picture was not solved: {res.text}")
                return '-1'
            elif res.text.find('OK') > -1:
                result = res.text[res.text.find('|') + 1:]
                logging.debug(f"The captcha is ready: {result}")
                return result
        logging.error(f"The number of solving iterations was exceed {self.try_count}")
        return "-1"

    def _solve_img_captcha(self, img_path: str) -> str:
        """Решение текстовой капчи на картинке

        (картинка сохранена)"""
        files = {'file': open(img_path, 'rb')}
        data = {'key': self.key, 'method': 'post'}
        res = requests.post("https://api.cap.guru/in.php", files=files, data=data)
        if res.ok and res.text.find('OK') > -1:
            req_id = res.text[res.text.find('|') + 1:]
        return self._captcha_solving(req_id)

    def _solve_img_captcha_bytes(self, img_bytes: bytes) -> str:
        """Решение текстовой капчи на картинке

        (картинка в байтах)"""
        files = {'file': img_bytes}
        data = {'key': self.key, 'method': 'post'}
        res = requests.post("https://api.cap.guru/in.php", files=files, data=data)
        if res.ok and res.text.find('OK') > -1:
            req_id = res.text[res.text.find('|') + 1:]
        else:
            logging.error(f"Cap Guru request was not ok: {res.ok} and {res.text.find('OK')}")
            return '-1'
        return self._captcha_solving(req_id)

    def _check_result(self, result: str):
        """Проверка результата решения капчи"""
        if result == "-1":
            fpath = f"data/img/page_screenshots_{dt.datetime.today().strftime('%d-%m-%y %H-%M-%S')}.png"
            self.driver.save_full_page_screenshot(fpath)
            raise Exception(f"The captcha wasn't solved. The page screenshot is saved: {fpath}")

    def get_captcha_value_vin2vin(self, load_delay: int, load_try_count: int) -> str:
        """Получение значение текстовой капчи на сайте vin2vin

        :param load_delay: Время отведённое на загрузку элемента.
        :param load_try_count: Количество попыток запроса на загрузку.
        :return: Текст с картинки.
        """
        # ждём загрузки элемента
        element = WebDriverWait(self.driver, load_delay).until(EC.presence_of_element_located((By.ID, 'p2')))
        self._check_wallet()
        image_src = element.get_attribute("src")
        while image_src is None or "gif" in image_src:
            element = WebDriverWait(self.driver, load_delay).until(EC.presence_of_element_located((By.ID, 'p2')))
            image_src = element.get_attribute("src")
            time.sleep(2)

        res = self._solve_img_captcha_bytes(get_image_bytes(image_src))
        c = 0
        while res == '-1' and c <= load_try_count or "gif" in image_src:
            image_element = self.driver.find_element(By.ID, 'p2')
            image_src = image_element.get_attribute("src")
            # driver.save_full_page_screenshot("page_screenshots.png")
            res = self._solve_img_captcha_bytes(get_image_bytes(image_src))
            time.sleep(2)
            c += 1
        self._check_result(res)

        return res

    def get_captcha_value_gibdd(self, load_delay: int, load_try_count: int) -> str:
        """Получение значение текстовой капчи на сайте ГИБДД"""
        self._check_wallet()
        # ждём загрузки элемента
        element = WebDriverWait(self.driver, load_delay).until(EC.presence_of_element_located((By.ID, 'captchaPic')))
        img_element = element.find_element(By.TAG_NAME, "img")
        image_src = img_element.get_attribute("src")
        start = dt.datetime.now()
        while image_src is None or "gif" in image_src:
            img_element = element.find_element(By.TAG_NAME, "img")
            image_src = img_element.get_attribute("src")
            time.sleep(2)
            end = dt.datetime.now()
            if (end - start).total_seconds() > 60:
                raise TimeoutError("Time out exception fo GIBDD captcha load")

        res = self._solve_img_captcha_bytes(get_image_bytes(image_src))
        c = 0
        while res == '-1' and c <= load_try_count:
            image_element = self.driver.find_element(By.ID, 'p2')
            image_src = image_element.get_attribute("src")
            # driver.save_full_page_screenshot("page_screenshots.png")
            res = self._solve_img_captcha_bytes(get_image_bytes(image_src))
            time.sleep(2)
            c += 1
        self._check_result(res)

        return res

    def pass_recaptcha(self) -> str:
        """Прохождение рекапчи.

        :return: Код решённой капчи. '-1' - Если капча не решена."""
        self._check_wallet()
        method = 'userrecaptcha'
        google_key = '6LfY85spAAAAAE0dA0h57RxA5TEegIruV38jDeEQ'
        url = self.driver.current_url
        res = requests.get(
            "https://api.cap.guru/in.php?key={}&method={}&googlekey={}&pageurl={}&cookies={}&userAgent={}".format(
                self.key,
                method,
                google_key,
                url,
                self.driver.get_cookies(),
                self.driver.execute_script('return navigator.userAgent;')
            ))
        if res.ok and res.text.find('OK') > -1:
            req_id = res.text[res.text.find('|') + 1:]
            res = self._captcha_solving(req_id)
        else:
            logging.error(f"Cap Guru request was not ok: {res.ok} and {res.text.find('OK')}")
            res = '-1'
        self._check_result(res)

        return res
