import React from 'react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../../tests';
import { PastGamesLastUsagePage } from './PastGamesLastUsagePage';

describe('PastGamesLastUsagePage component', () => {
    beforeEach(() => {
        installFetchMocks(fetchMock, { loggedIn: true });
    });

    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
    });

    it('to render listing of when each theme was last used', async () => {
        const { asFragment, findAllByText, getByText, store } = renderWithProviders(<PastGamesLastUsagePage />);
        await findAllByText("Rock & Power Ballads", { exact: false });
        const { games } = store.getState().games;
        Object.values(games).forEach(game => {
            getByText(game.title);
        });
        expect(asFragment()).toMatchSnapshot();
    });
});