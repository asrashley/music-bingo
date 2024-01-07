import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App';
import { Provider } from 'react-redux';

import { createStore } from './store/createStore';
import { initialState } from './store/initialState';

import * as serviceWorker from './serviceWorker';

const store = createStore(initialState);

const container = document.getElementById('root');

const root = createRoot(container);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();