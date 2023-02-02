import { configureStore, getDefaultMiddleware } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import { connectRouter } from 'connected-react-router';

import adminReducer from '../admin/adminSlice';
import directoriesReducer from '../directories/directoriesSlice';
import gamesReducer from '../games/gamesSlice';
import messagesReducer from '../messages/messagesSlice';
import settingsReducer from '../settings/settingsSlice';
import ticketsReducer from '../tickets/ticketsSlice';
import userReducer from '../user/userSlice';
import usersMiddleware from '../user/userMiddleware';
import messagesMiddleware from '../messages/messagesMiddleware';

import { history } from './history';

const middleware = [...getDefaultMiddleware(), usersMiddleware, messagesMiddleware];

if (process.env.NODE_ENV === `development`) {
  middleware.push(logger);
}

export function createStore(preloadedState) {
  return configureStore({
    middleware,
    reducer: {
      admin: adminReducer,
      directories: directoriesReducer,
      games: gamesReducer,
      messages: messagesReducer,
      settings: settingsReducer,
      tickets: ticketsReducer,
      router: connectRouter(history),
      user: userReducer,
    },
    preloadedState
  });
}
