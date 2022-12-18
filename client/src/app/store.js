import { configureStore, getDefaultMiddleware } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import { connectRouter } from 'connected-react-router';
import { createBrowserHistory } from 'history';

import adminReducer from '../admin/adminSlice';
import directoriesReducer from '../directories/directoriesSlice';
import gamesReducer from '../games/gamesSlice';
import messagesReducer from '../messages/messagesSlice';
import settingsReducer from '../settings/settingsSlice';
import ticketsReducer from '../tickets/ticketsSlice';
import userReducer from '../user/userSlice';
import usersMiddleware from '../user/userMiddleware';
import messagesMiddleware from '../messages/messagesMiddleware';

export const history = createBrowserHistory();

const middleware = [...getDefaultMiddleware(), usersMiddleware, messagesMiddleware];

if (process.env.NODE_ENV === `development`) {
  middleware.push(logger);
}

export const store = configureStore({
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
});
