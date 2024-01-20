import { Outlet, Route, Routes } from 'react-router-dom';
import { createMemoryHistory } from 'history';

import { RouteParams } from '../../routes';
import { ChooseTicketsPage } from './ChooseTicketsPage';
import { ListGamesPage } from '../../games/components';
import { PlayGamePage } from './PlayGamePage';
import { ViewTicketPage } from './ViewTicketPage';
import { renderWithProviders } from '../../../tests';

export function TestGameWrapper() {
    return (
        <Routes>
            <Route path="/" element={<div>Index page</div>} />
            <Route path="game" element={<><Outlet /><RouteParams /></>}>
                <Route path="" element={<ListGamesPage />} />
                <Route path=":gameId" element={<Outlet />}>
                    <Route path="" element={<ChooseTicketsPage />} />
                    <Route path="tickets" element={<PlayGamePage />} />
                    <Route path="tickets/:ticketPk" element={<ViewTicketPage />} />
                </Route>
            </Route>
        </Routes>
    );
}

describe('TestGameWrapper', () => {
    it('index page', () => {
        const history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        const { getByText } = renderWithProviders(<TestGameWrapper />, { history });
        getByText('Index page');
    });
});