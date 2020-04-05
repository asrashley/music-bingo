import { initialState as cards } from '../cards/cardsSlice';
import { initialState as games } from '../games/gamesSlice';
import { initialState as tickets } from '../tickets/ticketsSlice';
import { initialState as user } from '../user/userSlice';

export const initialState = Object.freeze({
    cards,
    games,
    tickets,
    user,
});
