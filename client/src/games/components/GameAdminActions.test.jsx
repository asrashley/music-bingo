import { waitFor } from '@testing-library/react';
import { createMemoryHistory } from 'history';
import fetchMock from 'fetch-mock';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { renderWithProviders } from '../../../tests';

import { GameAdminActions } from './GameAdminActions';

describe('GameAdminActions', () => {
    afterEach(() => {
        fetchMock.reset();
    });

    it('will reload data if "reload" button is clicked', async () => {
        const mockServer = new MockBingoServer(fetchMock, { currentUser: normalUser });
        const user = mockServer.getUserState(normalUser);
        const history = createMemoryHistory({
            initialEntries: ['/', '/history/games'],
            initialIndex: 1,
        });
        const store = createStore({
            ...initialState,
            user,
            games: {
                ...initialState.games,
                user: user.pk,
            },
        });

        const getGamesPromise = mockServer.addResponsePromise('/api/games', 'GET');
        const { events, getByText } = renderWithProviders(<GameAdminActions />, { store, history });
        expect(fetchMock.calls('/api/games', 'GET').length).toEqual(0);
        await events.click(getByText('Reload'));
        await waitFor(async () => {
            await getGamesPromise;
        })
        expect(fetchMock.calls('/api/games', 'GET').length).toEqual(1);
    });
});