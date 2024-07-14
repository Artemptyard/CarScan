from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union, ClassVar
from abc import ABC, abstractmethod


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class UserTypes(models.TextChoices):
    """Типы пользователей сайта.

    USER: Зарегистрированный пользователь.
    VIP: Пользователь, оформивший подписку.
    SUPPOR: Техническая поддержка.
    ADMIN: Администрация.
    """
    PREUSER = 'PRE', 'PreUser'
    USER = 'US', 'User'
    VIP = 'VIP', 'VIP'
    SUPPORT = 'SUP', 'Support'
    ADMIN = 'AD', 'Admin'


class User(AbstractBaseUser, PermissionsMixin):
    """Таблица с информацией о пользователях сайта."""
    email = models.EmailField(unique=True)
    user_type = models.CharField("User Type", max_length=3, choices=UserTypes.choices, default=UserTypes.USER)
    subscription_expired_date = models.DateField("Subscription Expired Date", null=True, default=None)
    registration_date = models.DateField("Registration Date", auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


# Значение текстовых полей по умолчанию
DEFAULT = "Нет информации"


class CarInfo(models.Model):
    """Абстрактный класс для описания классов с информацией об автомобиле"""

    created_date = models.DateField("Created Date", auto_now_add=True)

    class Meta:
        abstract = True

    @abstractmethod
    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        translation: Dict[str, str] = {}
        for line in self.__doc__.split('\n'):
            if ':' in line:
                en = line[:line.find(':')].strip()
                ru = line[line.find(':') + 1: -1].strip()
                translation[en] = ru
        return translation

    @abstractmethod
    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        translation: Dict[str, str] = {}
        for line in self.__doc__.split('\n'):
            if ':' in line:
                en = line[:line.find(':')].strip()
                ru = line[line.find(':') + 1: -1].strip()
                translation[ru] = en
        return translation

    @abstractmethod
    def get_dictionary(self, translate: bool = False) -> Dict[str, str]:
        """Получение словаря всех данных"""
        dictionary: Dict[str, str] = self.__dict__
        if translate:
            translation = self._get_ru_names()
            dictionary = dict(map(lambda item: (translation[item[0]], item[1]), dictionary.items()))
        return dictionary

    @abstractmethod
    def load_from_json(self, dictionary: Dict[str, Union[str, List[Dict[str, str]]]], translate: bool = True):
        """Загрузка из json файла"""
        this = self.__dict__
        translation = self._get_en_names()
        for key, value in dictionary.items():
            if translate and key in translation.keys():
                key = translation[key]
            if key in this.keys():
                this[key] = value


class Car(CarInfo):
    """Вся информация о автомобиле.

    vin_number: VIN номер.
    body_number: Номер кузова.
    chassis_number: Номер шасси.
    license_number: Госномер.
    license_region: Регион госномера.
    brand: Модель.
    model: Марка.
    manufacture_year: Год выпуска.
    vehicle_category: Категория ТС.
    vehicle_category_tr: Категория ТС по ТР ТС.
    min_weight: Масса без нагрузки.
    max_weight: Макс масса.
    power_hp: Мощность двигателя.
    fuel_type: Топливо.
    brake_system: Торм. система.
    document_type_sts: Тип документа.
    document_series: Серия документа.
    document_number: Номер документа.
    document_date: Дата выдачи.
    document_maker: Кем выдан.
    color: Цвет.
    vehicle_type: Тип ТС.
    engine_capacity: Объем двигателя.
    engine_number: Номер двигателя.
    pts_series_number: Серия и номер ПТС.
    pts_maker: Кем выдан ПТС.
    pts_owner: Владельцев по ПТС.
    registration_history: История регистрации.
    vehicle_limits: Ограничения у автомобиля.
    hijacking: Угон.
    inspections: Информация о пробеге.
    accidents: Информация о ДТП.
    fines: Штрафы.
    """
    # license_alphabet: ClassVar[List[str]] = ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х']
    vin_number = models.CharField(max_length=17, default=DEFAULT, unique=True)
    body_number = models.CharField(max_length=20, default=DEFAULT)
    chassis_number = models.CharField(max_length=50, default=DEFAULT)
    license_number = models.CharField(max_length=6, default=DEFAULT)
    license_region = models.CharField(max_length=3, default=DEFAULT)
    model = models.CharField(max_length=50, default=DEFAULT)
    brand = models.CharField(max_length=50, default=DEFAULT)
    manufacture_year = models.CharField(max_length=4, default=DEFAULT)
    vehicle_category = models.CharField(max_length=3, default=DEFAULT)
    vehicle_category_tr = models.CharField(max_length=10, default=DEFAULT)
    min_weight = models.CharField(max_length=6, default=DEFAULT)
    max_weight = models.CharField(max_length=6, default=DEFAULT)
    power_hp = models.CharField(max_length=8, default=DEFAULT)
    fuel_type = models.CharField(max_length=10, default=DEFAULT)
    brake_system = models.CharField(max_length=20, default=DEFAULT)
    document_type_sts = models.CharField(max_length=10, default=DEFAULT)
    document_series = models.CharField(max_length=4, default=DEFAULT)
    document_number = models.CharField(max_length=6, default=DEFAULT)
    document_date = models.CharField(max_length=10, default=DEFAULT)
    document_maker = models.CharField(max_length=20, default=DEFAULT)
    color = models.CharField(max_length=20, default=DEFAULT)
    vehicle_type = models.CharField(max_length=50, default=DEFAULT)
    engine_capacity = models.CharField(max_length=10, default=DEFAULT)
    engine_number = models.CharField(max_length=8, default=DEFAULT)
    pts_series_number = models.CharField(max_length=20, default=DEFAULT)
    pts_maker = models.CharField(max_length=20, default=DEFAULT)
    pts_owner = models.CharField(max_length=3, default=DEFAULT)
    hijacking = models.TextField(default=DEFAULT)
    report_path = models.FilePathField(null=True, default=None)


    class Meta:
        db_table = 'cars'

    def __str__(self):
        return f"Госномер {self.license_number}{self.get_dictionary()}" + f" VIN {self.vin_number}"

    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_ru_names()

    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_en_names()

    def _get_dictionary_from_list(self, records: List[CarInfo]) -> List[Dict[str, str]]:
        """Получение словаря из списка классов данных"""
        return [record.get_dictionary() for record in records]

    def get_dictionary(self, translate: bool = False) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Получение словаря всех данных"""
        dictionary: Dict[str, Union[str, List[Dict[str, str]]]] = {}
        for key, value in self.__dict__.items():
            if type(value) is list:
                if len(value) == 0:
                    dictionary[key] = DEFAULT
                else:
                    dictionary[key] = self._get_dictionary_from_list(value)
            else:
                dictionary[key] = value
        if translate:
            if translate:
                translation = self._get_ru_names()
                dictionary = dict(map(lambda item: (translation[item[0]], item[1]), dictionary.items()))
        return dictionary

    def set_dictionary(self, dictionary, translate: bool = True) -> None:
        """Заполнение"""
        this = self.__dict__
        translation = self._get_en_names()
        for key, value in dictionary.items():
            if len(value) == 0 or value == DEFAULT:
                continue
            # В истории автомобиля период начинается с "C 2...",
            # так определяем, что строка относиться к истории
            if "С 2" in key:
                self.registration_history.append(RegistrationHistory(key, value))
            else:
                if translate and key in translation.keys():
                    key = translation[key]
                if key in this.keys():
                    if this[key] != DEFAULT:
                        logging.info(f"Перезапись значений: {this[key]} -> {value}")
                    this[key] = value

    def load_from_json(self, dictionary: Dict[str, Union[str, List[Dict[str, str]]]], translate: bool = True):
        """Загрузка из json файла"""
        this = self.__dict__
        translation = self._get_en_names()
        for key, value in dictionary.items():
            if translate and key in translation.keys():
                key = translation[key]
            if key in this.keys():
                if type(value) is str:
                    this[key] = value
                elif key in ["История регистрации", "registration_history"]:
                    for item in value:
                        history = RegistrationHistory()
                        history.load_from_json(item, translate)
                        self.registration_history.append(history)
                elif key in ["Информация о ДТП", "accidents"]:
                    for item in value:
                        accident = Accident()
                        accident.load_from_json(item, translate)
                        self.accidents.append(accident)
                else:
                    logging.error(f"Unexpected type for CarInfo: {key}: {value}")


class RegistrationHistory(CarInfo):
    """
    История регистрации автомобиля

    period: Период до изменения.
    description: Описание изменения.
    """
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reg_history')
    period = models.CharField(max_length=40)
    description = models.TextField()

    class Meta:
        db_table = 'registrations_histories'

    def __str__(self):
        return f"Регистрация {self.car.id} {self.period}\n{self.description}"

    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_ru_names()

    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_en_names()

    def get_dictionary(self, translate: bool = False) -> Dict[str, str]:
        """Получение словаря всех данных"""
        return super().get_dictionary(translate)

    def load_from_json(self, dictionary: Dict[str, str], translate: bool = True):
        """Загрузка из json файла"""
        super().load_from_json(dictionary, translate)


class VehicleLimits(CarInfo):
    """Ограничения у автомобиля"""

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='limits')
    description = models.TextField()

    class Meta:
        db_table = 'vehicles_limits'

    def __str__(self):
        return f"Ограничения автомобиля {self.car.id}: {self.description}"

    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_ru_names()

    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_en_names()

    def get_dictionary(self, translate: bool = False) -> Dict[str, str]:
        """Получение словаря всех данных"""
        return super().get_dictionary()

    def load_from_json(self, dictionary: Dict[str, str], translate: bool = True):
        """Загрузка из json файла"""
        super().load_from_json(dictionary, translate)


class Inspection(CarInfo):
    """Информация о пробеге

    dc_number: Номер ДК.
    dc_validity_date: Дата действия ДК.
    mileage: Показания одометра.
    """

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inspetions')
    dc_number = models.CharField(max_length=15)
    dc_validity_date = models.CharField(max_length=40)
    mileage: str = models.IntegerField()

    class Meta:
        db_table = 'inspections'

    def __str__(self):
        return f"Пробег {self.mileage}"

    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_ru_names()

    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_en_names()

    def get_dictionary(self, translate: bool = False) -> Dict[str, str]:
        """Получение словаря всех данных"""
        return super().get_dictionary()

    def load_from_json(self, dictionary: Dict[str, str], translate: bool = True):
        """Загрузка из json файла"""
        super().load_from_json(dictionary, translate)


class Accident(CarInfo):
    """ДТП с участием автомобиля

    img_path: Путь к фотографии.
    """

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='accidents')
    img_path = models.FilePathField()

    class Meta:
        db_table = 'accidents'

    def __str__(self):
        return f"ДТП с автомобилем {self.car.id}"

    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_ru_names()

    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_en_names()

    def get_dictionary(self, translate: bool = False) -> Dict[str, str]:
        """Получение словаря всех данных"""
        return super().get_dictionary()

    def load_from_json(self, dictionary: Dict[str, str], translate: bool = True):
        """Загрузка из json файла"""
        super().load_from_json(dictionary, translate)


class Fines(CarInfo):
    """Штрафы

    description: Описание.
    """

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='fines')
    description = models.TextField()

    class Meta:
        db_table = 'fines'

    def __str__(self):
        return f"Штрафы {self.description}"

    def _get_ru_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_ru_names()

    def _get_en_names(self) -> Dict[str, str]:
        """Получения русских названий свойств из описания"""
        return super()._get_en_names()

    def get_dictionary(self, translate: bool = False) -> Dict[str, str]:
        """Получение словаря всех данных"""
        return super().get_dictionary()

    def load_from_json(self, dictionary: Dict[str, str], translate: bool = True):
        """Загрузка из json файла"""
        super().load_from_json(dictionary, translate)


class UserCar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        db_table = 'UsersCars'

    def __str__(self):
        return f'User {self.user.id} - Car {self.car.id}'