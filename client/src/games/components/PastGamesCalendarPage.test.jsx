import React from 'react';
import log from 'loglevel';
import fetchMock from 'fetch-mock';

import { renderWithProviders } from '../../../tests';
import { PastGamesCalendarPage } from './PastGamesCalendarPage';
import { MockBingoServer, adminUser } from '../../../tests/MockServer';
import { createStore, initialState } from '../../store';


describe('PastGamesCalendarPage component', () => {
    afterEach(() => {
        fetchMock.reset();
        log.resetLevel();
    });

    it('to render a calendar previous games', async () => {
        const mockServer = new MockBingoServer(fetchMock, { currentUser: adminUser });
        const user = mockServer.getUserState(adminUser);
        const store = createStore({
            ...initialState,
            games: {
                ...initialState.games,
                user: user.pk,
            },
            user,
        });
        const { asFragment, findAllByText } = renderWithProviders(<PastGamesCalendarPage />, { store });
        await findAllByText("Rock & Power Ballads", { exact: false });
        await fetchMock.flush(true);
        expect(asFragment()).toMatchSnapshot();
    });
});