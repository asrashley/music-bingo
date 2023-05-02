import React from 'react';
import ReactDOM from 'react-dom';
import App from './app/App';
import { Provider } from 'react-redux';

import { createStore } from './store/createStore';
import { initialState } from './store/initialState';

import * as serviceWorker from './serviceWorker';

const store = createStore(initialState);

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);

if (module.hot) {
    module.hot.accept('./app/App', () => {
        const NextApp = require('./app/App').default
        ReactDOM.render(
            <NextApp />,
            document.getElementById('root')
        )
    })
}

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
