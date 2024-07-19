import React from 'react';
import "./footer.css"

function Footer() {
    return (
        <div className="footer">
            <div className="car_container">
                <a href=''><img src="images/car_scan.jpeg" alt=''/></a>
            </div>
            <h2>© All rights reserved</h2>
            <div className="icons">
                <a href=''><img src='images/telephone.png' alt=''/></a>
                <a href=''><img src='images/mail.png' alt=''/></a>
                <a href=''><img src='images/telegram.png' alt=''/></a>
            </div>
        </div>
    );
  }
  
export default Footer;