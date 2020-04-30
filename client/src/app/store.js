import { configureStore, getDefaultMiddleware } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import { connectRouter } from 'connected-react-router';
import { createBrowserHistory } from 'history';
import { reducer as formReducer } from 'redux-form';

import cardsReducer from '../cards/cardsSlice';
import gamesReducer from '../games/gamesSlice';
import ticketsReducer from '../tickets/ticketsSlice';
import userReducer from '../user/userSlice';
import adminReducer from '../admin/adminSlice';
import usersMiddleware from '../user/userMiddleware';

export const history = createBrowserHistory();

export const store = configureStore({
  middleware: [...getDefaultMiddleware(), usersMiddleware, logger],
  reducer: {
    admin: adminReducer,
    cards: cardsReducer,
    form: formReducer,
    games: gamesReducer,
    tickets: ticketsReducer,
    router: connectRouter(history),
    user: userReducer,
  },
});
