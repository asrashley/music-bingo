import { createMemoryHistory } from 'history';
import { Outlet, Route, Routes } from 'react-router-dom';
import fetchMock from 'fetch-mock';

import { renderWithProviders, installFetchMocks } from '../../../tests';

import { PastGamesButtons } from './PastGamesButtons';

function TestPastGameButtons() {
    return (
        <Routes>
            <Route path="/" element={<div>Index page</div>} />
            <Route path="history" element={<PastGamesButtons />}>
                <Route path="" element={<div>PastGamesPopularityPage </div>} />
                <Route path="calendar" element={<div>PastGamesCalendarPage</div>} />
                <Route path="games" element={<Outlet />}>
                    <Route path="" element={<div>PastGamesPage</div>} />
                    <Route path=":gameId" element={<div>TrackListingPage</div>} />
                </Route>
                <Route path="themes" element={<Outlet />}>
                    <Route path="" element={<div>PastGamesLastUsagePage</div>} />
                    <Route path=":slug" element={<Outlet />}>
                        <Route path="" element={<div>PastGamesPage</div>} />
                        <Route path=":gameId" element={<div>TrackListingPage</div>} />
                    </Route>
                </Route>
            </Route>
        </Routes>
    );
}

describe('PastGamesButtons', () => {
    beforeEach(() => {
        installFetchMocks(fetchMock, { loggedIn: true });
    });

    afterEach(() => {
        fetchMock.reset();
    });

    it.each([{
        pathname: '/history/games',
        page: 'all',
    }, {
        pathname: '/history/calendar',
        page: 'calendar',
    }, {
        pathname: '/history',
        page: 'popularity',
    }, {
        pathname: '/history/themes',
        page: 'usage'
    }])('renders buttons for page $page from URL $pathname', async ({ pathname, page }) => {
        const history = createMemoryHistory({
            initialEntries: ['/', pathname],
            initialIndex: 1,
        });
        const { findByText, container } = renderWithProviders(
            <TestPastGameButtons />, { history });
        await findByText('All Games');
        expect(container.querySelector(`.page-${page}`)).toBeInTheDocument();
    });

})