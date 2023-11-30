import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
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
        const { asFragment, store } = renderWithProviders(<PastGamesLastUsagePage />);
        await screen.findAllByText("Rock & Power Ballads", { exact: false });
        const { games } = store.getState().games;
        Object.values(games).forEach(game => {
            screen.getByText(game.title);
        });
        expect(asFragment()).toMatchSnapshot();
    });
});