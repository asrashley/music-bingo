import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App';
import { Provider } from 'react-redux';

import { createStore } from './store/createStore';
import { initialState } from './store/initialState';

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
