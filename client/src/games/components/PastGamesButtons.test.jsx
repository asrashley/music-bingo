import waitForExpect from 'wait-for-expect';
import { fireEvent } from '@testing-library/react';
import { createMemoryHistory } from 'history';
import { Outlet, Route, Routes } from 'react-router-dom';

import { renderWithProviders, installFetchMocks, fetchMock } from '../../testHelpers';

import { PastGamesButtons } from './PastGamesButtons';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import gameFixture from '../../fixtures/game/159.json';
import user from '../../fixtures/userState.json';

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
    let apiMocks;
    beforeEach(() => {
        apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
    });

    afterEach(() => {
        fetchMock.mockReset();
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

    it('will reload data if "reload" button is clicked', async () => {
        const history = createMemoryHistory({
            initialEntries: ['/', '/history/games'],
            initialIndex: 1,
        });
        const store = createStore({
            ...initialState,
            user,
            games: {
                ...initialState.games,
                games: {
                    [gameFixture.pk]: {
                        ...gameFixture,
                        isFetchingDetail: false,
                        invalidDetail: false,
                        invalid: false,
                    }
                },
                gameIds: {
                    [gameFixture.id]: gameFixture.pk,
                },
                pastOrder: [
                    gameFixture.pk,
                ],
                user: user.pk,
            },
            routes: {
                params: {
                    gameId: gameFixture.id,
                    page: 'usage',
                },
            },
        });

        const fetchGamesSpy = vi.fn((_, data) => data);
        apiMocks.setResponseModifier('/api/games', fetchGamesSpy);
        const { getByText } = renderWithProviders(<TestPastGameButtons />, { store, history });
        expect(fetchGamesSpy).not.toHaveBeenCalled();
        fireEvent.click(getByText('Reload'));
        await waitForExpect(() => {
            expect(fetchGamesSpy).toHaveBeenCalledTimes(1);
        });
    });
})