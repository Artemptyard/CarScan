import React from 'react';
import "./partialVerification.css"
import { useEffect, useState } from "react";
import { API_URL_PARSE } from "../../../index";

function PartialVerification() {
    const [taskId, setTaskId] = useState(null);
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    const sendData = async () => {
        setLoading(true);
        const data = { param1: 'something' };

        try {
            const csrfToken = getCookie('csrftoken');
            const res = await fetch(API_URL_PARSE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(data),
            });

            const result = await res.json();
            setTaskId(result.task_id);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const checkResult = async () => {
        if (!taskId) return;

        setLoading(true);
        const data = {task_id: taskId}
        try {
            const csrfToken = getCookie('csrftoken');
            const res = await fetch(API_URL_PARSE + `result/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(data),
            });
            const result = await res.json();
            if ("message" in result)
                setResponse(result.message)
            if ("result" in result)
                setResponse(result.result)
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let intervalId;
        if (taskId)
          intervalId = setInterval(checkResult, 1000); // Проверка каждые 2 секунды
    
        return () => clearInterval(intervalId);
      }, [taskId]);

    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };
    return (
        <div className="partialVerification">
            <div className="content_partial">
                <h1>Разделяй и властвуй!</h1>
                <h3>Вы можете проверить только ту информацию об
                    автомобиле, которая нужна вам именно сейчас
                </h3>
                <div className='advertisement_partial'>Реклама</div>
                <h2>Выберите одну из карточек ниже, нажмите на кнопку, введите
                    требуемые данные и частичная проверка начнется!
                </h2>
                <div className="input_partial">
                    <h1>Узнайте VIN по Госномеру</h1>
                    <p>Узнав VIN, вы сможете продолжить проверку автомобиля!</p>
                    <button>Узнать VIN</button>
                </div>
                <div className='advertisement_partial'>Реклама</div>
                <div className="services">
                    <div>
                        <h3>Получи историю регистрации</h3>
                        <p>Информация о периоде регистрации и всех собствениках автомобиля</p>
                        <button>Проверить</button>
                    </div>
                    <div>
                        <h3>Получи историю регистрации</h3>
                        <p>Информация о периоде регистрации и всех собствениках автомобиля</p>
                        <button>Проверить</button>
                    </div>
                    <div>
                        <h3>Получи историю регистрации</h3>
                        <p>Информация о периоде регистрации и всех собствениках автомобиля</p>
                        <button>Проверить</button>
                    </div>
                    <div>
                        <h3>Получи историю регистрации</h3>
                        <p>Информация о периоде регистрации и всех собствениках автомобиля</p>
                        <button>Проверить</button>
                    </div>
                    <div>
                        <h3>Получи историю регистрации</h3>
                        <p>Информация о периоде регистрации и всех собствениках автомобиля</p>
                        <button>Проверить</button>
                    </div>
                    <div>
                        <h3>Получи историю регистрации</h3>
                        <p>Информация о периоде регистрации и всех собствениках автомобиля</p>
                        <button>Проверить</button>
                    </div>
                </div>
                <div className='advertisement_partial'>Реклама</div>
            </div>
        </div>
            
    );
  }
  
export default PartialVerification;