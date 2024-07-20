import React from 'react';
import "./App.css"
import Header from "./mycomponents/header/Header.jsx"
import Footer from "./mycomponents/footer/Footer.jsx"
import FullVerification from "./mycomponents/verification/fullVerification/FullVerification.jsx"
import PartialVerification from './mycomponents/verification/partialVerification/PartialVerification.jsx';
import MainPage from './mycomponents/mainPage/MainPage.jsx';
import { Route, Routes } from 'react-router-dom';

function App() {
    return(
        <>
            <div className='container'>
                <Header/>
                <Routes>
                    <Route path='/' element={<MainPage/>}/>
                    <Route path='/partial' element={<PartialVerification/>}/>
                    <Route path='/full' element={<FullVerification/>}/>                  
                </Routes>
                <Footer/>
            </div>  
        </>
    )
}

export default App;
