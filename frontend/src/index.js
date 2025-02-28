import React from 'react';
import ReactDOM from 'react-dom/client'; // Update the import for React 18
import './index.css';
import App from './App';

// Get the root DOM node
const rootElement = document.getElementById('root');

// Create a root and render the App
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
