import React from 'react';
import "./fullVerification.css"

function FullVerification() {
    return (
        <div className="fullVerification">
            <div className="content">
                <h1>Все и  сразу!</h1>
                <h3>Вы можете проверить автомобиль и получить полный pdf отчёт о нём</h3>
                <div>Реклама</div>
                <h2>Получите полный отчёт</h2>
                <div className="input">
                    <p>Номер</p>
                    <div>
                        <input type="text" />
                        <button>Получить отчёт</button>
                    </div>
                </div>
                <h3>Введите госномер или VIN номер нужного вам автомобиля. Проверка займёт около 5 минут и вы получите pdf отчёт!</h3>
                <div>Реклама</div>
            </div>
        </div>
            
    );
  }
  
export default FullVerification;