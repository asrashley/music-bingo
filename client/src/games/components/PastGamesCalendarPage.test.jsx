import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { PastGamesCalendarPage } from './PastGamesCalendarPage';

describe('PastGamesCalendarPage component', () => {
    beforeEach(() => {
        installFetchMocks(fetchMock, { loggedIn: true });
    });

    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
    });

    it('to render a calendar previous games', async () => {
        //log.setLevel('debug');
        const { asFragment } = renderWithProviders(<PastGamesCalendarPage />);
        await screen.findAllByText("Rock & Power Ballads", { exact: false });
        expect(asFragment()).toMatchSnapshot();
    });
});