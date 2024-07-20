import React, { useState } from 'react';
import "./header.css"
import NavigationMenu from './navigationMenu/NavigationMenu';
import { Link } from 'react-router-dom';

function Header() {

    const [menuState, setMenuState] = useState(false);

    const toggleMenu = () => {
        setMenuState(prevState => !prevState);
    };

    return (
        <>
            <div className="header">
                <p>Carscan</p>
                <div className="navigation">
                    <Link className="link" to='/'>Главная</Link>
                    <Link className="link" to='/full'>Полная проверка</Link>
                    <Link className="link" to='/partial'>Частичная проверка</Link>
                    <Link className="link" to='/login'>Войти</Link>
                    <div id="nav-icon" className={menuState ? "open" : ""} onClick={toggleMenu}>
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
            <div className={`menu-container ${menuState ? "show" : ""}`}>
                <NavigationMenu/>
            </div>
        </>
    );
  }
  
export default Header;