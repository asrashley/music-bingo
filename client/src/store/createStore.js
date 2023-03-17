import { configureStore, getDefaultMiddleware } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import { connectRouter } from 'connected-react-router';

import adminReducer from '../admin/adminSlice';
import directoriesReducer from '../directories/directoriesSlice';
import gamesReducer from '../games/gamesSlice';
import messagesReducer from '../messages/messagesSlice';
import settingsReducer from '../settings/settingsSlice';
import systemReducer from '../system/systemSlice';
import ticketsReducer from '../tickets/ticketsSlice';
import userReducer from '../user/userSlice';
import usersMiddleware from '../user/userMiddleware';
import messagesMiddleware from '../messages/messagesMiddleware';

import { history } from './history';

export function createStore(preloadedState, logging) {
  const middleware = [...getDefaultMiddleware(), usersMiddleware, messagesMiddleware];
  if (logging === undefined) {
    logging = (process.env.NODE_ENV === 'development');
  }
  if (logging) {
    middleware.push(logger);
  }
  return configureStore({
    middleware,
    reducer: {
      admin: adminReducer,
      directories: directoriesReducer,
      games: gamesReducer,
      messages: messagesReducer,
      settings: settingsReducer,
      system: systemReducer,
      tickets: ticketsReducer,
      router: connectRouter(history),
      user: userReducer,
    },
    preloadedState
  });
}
