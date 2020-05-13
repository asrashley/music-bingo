import { initialState as admin } from '../admin/adminSlice';
import { initialState as cards } from '../cards/cardsSlice';
import { initialState as games } from '../games/gamesSlice';
import { initialState as messages } from '../messages/messagesSlice';
import { initialState as tickets } from '../tickets/ticketsSlice';
import { initialState as user } from '../user/userSlice';

export const initialState = Object.freeze({
    admin,
    cards,
    games,
    messages,
    tickets,
    user,
});
