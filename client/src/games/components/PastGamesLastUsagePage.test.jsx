import React from 'react';
import log from 'loglevel';

import { fetchMock, renderWithProviders } from '../../../tests';
import { initialState } from '../../store/initialState';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { PastGamesLastUsagePage } from './PastGamesLastUsagePage';

describe('PastGamesLastUsagePage component', () => {
    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
    });

    it('to render listing of when each theme was last used', async () => {
        const mockServer = new MockBingoServer(fetchMock, { currentUser: normalUser });
        const user = mockServer.getUserState(normalUser);
        const preloadedState = {
            ...initialState,
            user,
        };
        const { asFragment, findAllByText, getByText, store } = renderWithProviders(
            <PastGamesLastUsagePage />, { preloadedState });
        await findAllByText("Rock & Power Ballads", { exact: false });
        const { games } = store.getState().games;
        Object.values(games).forEach(game => {
            getByText(game.title);
        });
        await fetchMock.flush(true);
        expect(asFragment()).toMatchSnapshot();
    });
});