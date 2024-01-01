import { configureStore } from '@reduxjs/toolkit';
import { createLogger } from 'redux-logger';
import { createRouterMiddleware, createRouterReducer } from '@lagunovsky/redux-react-router';
import log from 'loglevel';

import adminReducer from '../admin/adminSlice';
import directoriesReducer from '../directories/directoriesSlice';
import gamesReducer from '../games/gamesSlice';
import messagesReducer from '../messages/messagesSlice';
import routesReducer from '../routes/routesSlice';
import settingsReducer from '../settings/settingsSlice';
import systemReducer from '../system/systemSlice';
import ticketsReducer from '../tickets/ticketsSlice';
import userReducer from '../user/userSlice';
import usersMiddleware from '../user/userMiddleware';
import messagesMiddleware from '../messages/messagesMiddleware';

import { history } from './history';
const routerMiddleware = createRouterMiddleware(history);

export function createStore(preloadedState, logging) {
  const middleware = (getDefaultMiddleware) => {
    const mw = getDefaultMiddleware()
      .prepend(routerMiddleware)
      .concat(usersMiddleware)
      .concat(messagesMiddleware);
    if (logging === undefined) {
      logging = import.meta.env.DEV;
    }
    if (!logging) {
      return mw;
    }
    const logger = {
      debug: log.debug,
      info: log.info,
      warn: log.warn,
      error: log.error,
      log: log.debug,
    };
    const loggerMiddleware = createLogger({
      level: 'debug',
      logger
    });
    return mw.concat(loggerMiddleware);
  };
  return configureStore({
    middleware,
    reducer: {
      admin: adminReducer,
      directories: directoriesReducer,
      games: gamesReducer,
      messages: messagesReducer,
      routes: routesReducer,
      settings: settingsReducer,
      system: systemReducer,
      tickets: ticketsReducer,
      router: createRouterReducer(history),
      user: userReducer,
    },
    preloadedState
  });
}
