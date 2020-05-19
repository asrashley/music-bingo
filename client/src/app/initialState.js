import { initialState as admin } from '../admin/adminSlice';
import { initialState as games } from '../games/gamesSlice';
import { initialState as messages } from '../messages/messagesSlice';
import { initialState as tickets } from '../tickets/ticketsSlice';
import { initialState as user } from '../user/userSlice';

export const initialState = Object.freeze({
    admin,
    games,
    messages,
    tickets,
    user,
});
