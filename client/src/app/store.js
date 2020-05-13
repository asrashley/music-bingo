import { configureStore, getDefaultMiddleware } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import { connectRouter } from 'connected-react-router';
import { createBrowserHistory } from 'history';

import adminReducer from '../admin/adminSlice';
import cardsReducer from '../cards/cardsSlice';
import gamesReducer from '../games/gamesSlice';
import messagesReducer from '../messages/messagesSlice';
import ticketsReducer from '../tickets/ticketsSlice';
import userReducer from '../user/userSlice';
import usersMiddleware from '../user/userMiddleware';

export const history = createBrowserHistory();

export const store = configureStore({
  middleware: [...getDefaultMiddleware(), usersMiddleware, logger],
  reducer: {
    admin: adminReducer,
    cards: cardsReducer,
    games: gamesReducer,
    messages: messagesReducer,
    tickets: ticketsReducer,
    router: connectRouter(history),
    user: userReducer,
  },
});
