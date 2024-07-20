import "./navigationMenu.css"
import {Link } from 'react-router-dom';

function NavigationMenu() {
    return (
        <div className="navigationMenu">
            <Link className="navigtion_link" to='/'>Главная</Link>
            <Link className="navigtion_link" to='/full'>Полная проверка</Link>
            <Link className="navigtion_link" to='/partial'>Частичная проверка</Link>
            <Link className="navigtion_link" to='/login'>Войти</Link>
        </div>
    );
  }
  
export default NavigationMenu;