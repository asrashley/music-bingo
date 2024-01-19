import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders } from '../../../tests';
import { PastGamesCalendarPage } from './PastGamesCalendarPage';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { createStore, initialState } from '../../store';


describe('PastGamesCalendarPage component', () => {
    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
    });

    it('to render a calendar previous games', async () => {
        //log.setLevel('debug');
        const mockServer = new MockBingoServer(fetchMock, { currentUser: normalUser });
        const store = createStore({
            ...initialState,
            user: mockServer.getUserState(normalUser),
        });
        const { asFragment } = renderWithProviders(<PastGamesCalendarPage />, { store });
        await screen.findAllByText("Rock & Power Ballads", { exact: false });
        await fetchMock.flush(true);
        expect(asFragment()).toMatchSnapshot();
    });
});