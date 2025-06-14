import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import "./index.css"
import {BrowserRouter} from 'react-router-dom';

export const API_URL = "http://127.0.0.1:8000/api/cars/"
export const API_STATIC_MEDIA = "http://127.0.0.1:8000/"

export const API_URL = "http://127.0.0.1:8000/api/cars/"
export const API_STATIC_MEDIA = "http://127.0.0.1:8000/"

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </React.StrictMode>
);

