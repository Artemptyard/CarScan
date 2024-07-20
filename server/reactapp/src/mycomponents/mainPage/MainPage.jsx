import React from 'react';
import "./mainPage.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { API_URL } from "../../index";
import { API_URL_PARSE } from "../../index";

function MainPage() {

    return (
        <div className="partialVerification">
            <div className="content_main">
                <h1>CarScan</h1>
                <h3>Бесплатный сервис для проверки автомобилей!</h3>
                <h3>
                    На нашем сайте вы можете узнать практически всю
                    информацию об автомобиле из открытых баз данных!
                </h3>
                <div className='advertisement_main'>Реклама</div>
                <h2>Узнайте VIN по Госномеру</h2>
                {/* {!taskId && ( */}
                    <div className="input_main">
                        <div>
                            <p>Номер</p>
                            <input type="text" />
                        </div>
                        <div>
                            <p>Регион</p>
                            <input type="text" />
                        </div>
                        {/* <button onClick={sendData} disabled={loading}>
                            {loading ? 'В процессе...' : 'Узнать VIN'}
                        </button> */}
                        <button>Узнать VIN</button>
                    </div>
                {/* )} */}
                {/* <p>{response}</p> */}
                <h3>Введите госномер или VIN номер нужного вам автомобиля.
                    Проверка займёт около 5 минут и вы получите pdf отчёт!</h3>
                <div className='advertisement_main'>Реклама</div>
                <h2>Зарегистрируйтесь!</h2>
                <h3>
                    Зарегестрированный пользователь получает больше
                    возможностей БЕСПЛАТНО!
                </h3>
                <div className='subscription'>
                    <div>
                        <h3>Посетитель</h3>
                        <p>Пользователь без регистрации</p>
                        <h1>0₽/мес.</h1>
                        <p>Частичная проверка машины</p>
                        <p>Полная проверка машины</p>
                        <p>Получение pdf отчёта</p>
                        <button>Проверить машину</button>
                    </div>
                    <div>
                        <h3>Зарегестрированный</h3>
                        <p>Зарегестрированный пользователь</p>
                        <h1>0₽/мес.</h1>
                        <p>Сохранение проверенных автомобилей в течении недели</p>
                        <p>Проверка 2 машин одновременно</p>
                        <p>Приоритет на проверку автомобиля</p>
                        <button>Проверить машину</button>
                    </div>
                    <div>
                        <h3>PRO</h3>
                        <p>Зарегестрированный пользователь с подпиской</p>
                        <h1>199₽/мес.</h1>
                        <p>Сохранение проверенных машин в течении месяца</p>
                        <p>
                            Одновременная проверка 5 машин с
                            максимальным приоритетом
                        </p>
                        <p>Доступ к телеграм боту для проверки автомобилей</p>
                        <p>Отсутсвие рекламы</p>
                        <button>Проверить машину</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default MainPage;