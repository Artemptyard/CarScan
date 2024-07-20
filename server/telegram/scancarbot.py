import os.path
import time
from pprint import pprint

import telebot
import logging
from typing import Dict, List, Union, Optional
from telebot import types
from queue import Queue
from threading import Thread, current_thread, active_count

from data.appdata.carinfo import CarInfo
from data.appdata.myparser import ParserOptions, MyParser, ParserResults, DEFAULT
from data.appdata.user import User, UserStates
from data.appdata.functions import save_json, load_json


class ScanCarBot:
    """Телеграмм бот для проверки автомобилей"""
    _token: str = "7162134726:AAHtDCF86bITtcAubMJM_4mSV87v5_GFdeM"

    def __init__(self, parser_options: ParserOptions = ParserOptions(), thread_count: int = 3):
        self.bot = telebot.TeleBot(self._token)
        self.users: Dict[int, User] = {}
        self.parser_options = parser_options
        logging.info("Bot was started")
        self._load_users()
        self.thread_queue: Queue[Thread] = Queue()
        self.thread_count = thread_count
        self.main_thread = Thread(target=self._start_thread)

    def _get_free_thread_count(self) -> int:
        """Получение количества свободных потоков"""
        return self.thread_count - active_count()

    def _start_thread(self):
        """Проверка количества активных потоков и запуск новых"""
        logging.info("The main thread was started")
        while getattr(self.main_thread, "do_run", True):
            free = self._get_free_thread_count()
            for _ in range(free):
                if not self.thread_queue.empty():
                    self.thread_queue.get().start()
        logging.info("The main thread was ended")

    def _load_users(self):
        """Загрузка пользователей из файла"""
        logging.info("Start of loading users data")
        if not os.path.isfile("data/json/users.json"):
            return
        users: Dict[int, List[dict]] = load_json("users")
        for key, item in users.items():
            user = User(id=key)
            for info in item:
                car_info = CarInfo()
                car_info.load_from_json(info)
                user.cars_info.append(car_info)
                # pprint(car_info.get_dictionary(True))
            self.users[int(key)] = user
        logging.info("End of loading users data")

    def _save_users(self):
        """Сохранение данных пользователей в файл"""
        logging.info("Start of saving users data")
        users: Dict[int, List[dict]] = {}
        for user in self.users.values():
            info = []
            for car in user.cars_info:
                info.append(car.get_dictionary(True))
            users[user.id] = info
        save_json(users, "users")
        logging.info("End of saving users data")

    def _parser_invoke(self, parser_func) -> ParserResults:
        """Запуск парсинга, пока есть ошибка

        :param parser_func: Функция парсера для запуска."""
        result = parser_func()
        while result == ParserResults.Error:
            result = parser_func()
        return result

    def _parse(self, message: types.Message) -> ParserResults:
        """Начало проверки автомобиля

        :param message: Сообщение от пользователя
        :return:
        """
        number = message.text
        user_id = message.from_user.id
        result = self._get_auto_by_number(number)
        if result is None:
            if len(number) == 17:
                my_parser = MyParser(vin_number=number, options=self.parser_options)
            else:
                my_parser = MyParser(license_number=message.text, options=self.parser_options)
            if my_parser.car_info.vin_number == DEFAULT:
                if self._parser_invoke(my_parser.parse_vin) != ParserResults.Ok:
                    my_parser.driver.quit()
                    # my_parser.driver.close()
                    return ParserResults.NotFound
            self._parser_invoke(my_parser.parse_history)
            self._parser_invoke(my_parser.parse_accident)
            self.users[user_id].cars_info.append(my_parser.car_info)
            # my_parser.driver.close()
            return ParserResults.Ok
        else:
            if result.vin_number not in [info.vin_number for info in self.users[user_id].cars_info]:
                self.users[user_id].cars_info.append(result)
            return ParserResults.Skipped

    def _check_data(self, message: str) -> bool:
        """Проверка данных введённых пользователем

        :param message: Сообщение от пользователя.
        :return: Корректны ли данные.
        """
        message = message.strip()
        length = len(message)
        check_null = length == 0
        check_count = len(message.split()) != 1
        check_length = length not in [8, 9, 17]
        return not any([check_null, check_count, check_length])

    def _get_auto_by_number(self, number: str) -> Optional[CarInfo]:
        """Получение проверенного автомобиля по номеру

        :param number: vin номер или гос номер.
        :return: Информация о машине CarInfo, если она проверялась, иначе None.
        """
        for user in self.users.values():
            for car_info in user.cars_info:
                vin = car_info.vin_number
                license = car_info.license_number + car_info.license_region
                if vin == number or license == number:
                    return car_info
        return None

    def _get_message_info(self, car_info: CarInfo, number: str, parse_result: ParserResults) -> str:
        """Составление сообщение с информацией о автомобиле

        :param car_info: Информация о машине.
        :param number: vin номер или гос номер.
        :param parse_result: Результат парсинга.
        """
        json_str = car_info.get_dictionary(True)
        message = []
        if parse_result == ParserResults.Skipped:
            message.append(f"--_Машина с номером {number} уже проверялась._--")
        else:
            message.append(f"--_Проверена машина с номером {number}._--")
        for key, value in json_str.items():
            if type(value) is str:
                message.append(f"*{key}*: {value}")
            elif type(value) is list:
                if key == "Информация о ДТП":
                    message.append(f"*{key}*: Фотографии")
                elif key == "История регистрации":
                    message.append(f"*{key}:*")
                    for item in value:
                        values = list(item.values())
                        message.append(f"_\t{values[0]}_: {values[1]}")
                else:
                    logging.error(f"Unexpected value: {key}: {value}")
                    message.append(f"{key}: {value}")
            else:
                logging.error(f"Unexpected type: {type(value)} in: {key}: {value}")
                message.append(f"{key}: {value}")
        return '\n'.join(message)

    def _send_car_info(self, user_id: int, number: str, parse_result: ParserResults):
        """Вывод красивого сообщение с информацией о автомобиле

        :param user_id: id пользователя.
        :param number: vin номер или гос номер.
        :param parse_result: Результат парсинга.
        """
        car_info = self._get_auto_by_number(number)
        if car_info is None or parse_result == ParserResults.NotFound:
            self.bot.send_message(user_id, "К сожалению, по данному номеру не было найдено информации.")
            return
        message = self._get_message_info(car_info, number, parse_result)
        self.bot.send_message(user_id, message, parse_mode="Markdown")
        if type(car_info.accidents) is list and len(car_info.accidents) != 0:
            media = []
            for photo_path in car_info.accidents:
                media.append(types.InputMediaPhoto(open(photo_path.img_path, 'rb')))
            media[0].caption = "ДТП"
            self.bot.send_media_group(user_id, media)
            for photo in media:
                photo.media.close()

    def _parsing(self, message: types.Message):
        """Парсинг в отдельном потоке"""
        user_id = message.from_user.id
        self.bot.send_message(user_id, f"Начинаю проверку по номеру: {message.text}. "
                                       f"Это может занять около 5 минут.")
        try:
            logging.info(f"New {current_thread().name} was started")
            result = self._parse(message)
            self._send_car_info(user_id, message.text, result)
            self._save_users()
        except Exception:
            self.bot.send_message(user_id, "Во время проверки произошла ошибка. "
                                           "Пожалуйста попробуйте ещё раз.")
            logging.error("Error appeared while parsing: ", exc_info=True)
        finally:
            self.users[user_id].state = UserStates.Nothing
        logging.info(f"{current_thread().name} was ended")

    def start(self):
        """Запуск бота"""

        @self.bot.message_handler(commands=["start"])
        def start(message: types.Message):
            """Начало общения с ботом"""
            user_id = message.from_user.id
            if user_id not in self.users:
                logging.info(f"New user subscribed: {user_id}")
                self.users[user_id] = User(id=user_id)
                self._save_users()
            self.bot.send_message(user_id, "Привет! Я бот для проверки машин. "
                                           "Введите /scancar чтобы начать проверку автомобиля.")

        @self.bot.message_handler(commands=["scancar"])
        def scan_car(message):
            """Запрос на сканирование машины"""
            user_id = message.from_user.id
            user = self.users.get(user_id)
            if user:
                if user.state != UserStates.WaitForResult:
                    logging.info(f"User id{user_id} start scanning")
                    # Отправляем сообщение, запрашивающее номер автомобиля
                    self.bot.reply_to(message, "Введите гос номер автомобиля (например, А123БВ123) или "
                                               "vin номер (A0B001023C4506789).")
                    # Устанавливаем состояние ожидания номера автомобиля
                    user.state = UserStates.WritingCarNumber
                elif user.state == UserStates.WaitForResult:
                    self.bot.send_message(user_id, "Извините, вы уже запустили данную функцию. "
                                                   "Пожалуйста, дождитесь окончания процесса.")
            else:
                self.bot.reply_to(message, 'Чтобы начать проверку машины, сначала введите команду /start.')

        @self.bot.message_handler(commands=["getcar"])
        def get_car(message):
            """Запрос на получение информации об уже отсканированных машин"""
            user_id = message.from_user.id
            user = self.users.get(user_id)
            if user:
                car_parameter = message.text.split("/getcar ", 1)[1]
                # Здесь должен быть код для получения машины с указанными параметрами
                self.bot.reply_to(message, f"Машина с параметром '{car_parameter}': ...")
            else:
                self.bot.reply_to(message, "Чтобы получить информацию о машине, сначала введите команду /start.")

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            user_id = message.from_user.id
            user = self.users.get(user_id)
            if user and user.state == UserStates.WritingCarNumber:
                car_number = message.text
                if not self._check_data(car_number):
                    self.bot.send_message(user_id, "Вы ввели некорректный номер.\n"
                                                   "Введите гос номер автомобиля (например, А123БВ123) или "
                                                   "vin номер (A0B001023C4506789).")
                else:
                    if self._get_free_thread_count() == 0:
                        self.bot.send_message(user_id, "Вас запрос находиться в очереди. "
                                                       "Вам придёт сообщение, когда проверка начнётся.")
                    user.state = UserStates.WaitForResult
                    # if result == ParserResults.Ok:
                    #     self._send_car_info(user_id, car_number)
                    #     self._save_users()
                    # else:
                    #     self.bot.send_message(user_id, "К сожалению, по данному номеру не было найдено информации.")
                    self.thread_queue.put(Thread(target=self._parsing, args=(message, )))
            else:
                self.bot.reply_to(message, 'Извините, я не понимаю команду. Введите /start чтобы начать.')

        self.main_thread.start()
        self.thread_count += active_count() + 1
        self.bot.infinity_polling()

    def __del__(self, instance):
        """"""
        self.main_thread.do_run = False
