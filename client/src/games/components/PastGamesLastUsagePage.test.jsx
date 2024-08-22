import React from 'react';
import { vi } from 'vitest';
import log from 'loglevel';

import { fetchMock, renderWithProviders } from '../../../tests';
import { initialState } from '../../store/initialState';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { PastGamesLastUsagePage } from './PastGamesLastUsagePage';

describe('PastGamesLastUsagePage component', () => {
    beforeEach(() => {
        vi.useFakeTimers('modern');
        vi.setSystemTime(new Date('19 Jan 2024 19:09:00 GMT'));
    });

    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
        vi.useRealTimers();
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
