import { initialState as admin } from '../admin/adminSlice';
import { initialState as games } from '../games/gamesSlice';
import { initialState as directories } from '../directories/directoriesSlice';
import { initialState as messages } from '../messages/messagesSlice';
import { initialState as routes } from '../routes/routesSlice';
import { initialState as tickets } from '../tickets/ticketsSlice';
import { initialState as settings } from '../settings/settingsSlice';
import { initialState as system } from '../system/systemSlice';
import { initialState as user } from '../user/userSlice';

export const initialState = Object.freeze({
    admin,
    directories,
    games,
    messages,
    routes,
    settings,
    system,
    tickets,
    user,
});
