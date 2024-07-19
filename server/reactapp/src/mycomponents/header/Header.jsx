import React from 'react';
import "./header.css"

function Header() {
    return (
        <div className="header">
            <p>Carscan</p>
            <div className="navigation">
                <a href=''>Полная проверка</a>
                <a href=''>Частичная проверка</a>
                <a href=''>Войти</a>
            </div>
        </div>
    );
  }
  
export default Header;