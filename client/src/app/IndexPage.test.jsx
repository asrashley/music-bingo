import React from 'react';
import { vi, describe, it, expect } from 'vitest';
import log from 'loglevel';
import fetchMock from 'fetch-mock';

import { renderWithProviders } from '../../tests';
import { MockBingoServer, normalUser } from '../../tests/MockServer';
import { IndexPage } from './IndexPage';

import { initialState } from '../store/initialState';

describe('IndexPage component', () => {
	afterAll(() => {
		vi.resetAllMocks();
	});

	afterEach(() => {
		fetchMock.reset();
		log.resetLevel();
		vi.useRealTimers();
	});

	it('renders without throwing an exception with initial state', async () => {
		const mockServer = new MockBingoServer(fetchMock);
		const { findByText } = renderWithProviders(<IndexPage />);
		await findByText("You need a registered account to play Musical Bingo.", { exact: false });
		await mockServer.shutdown();
	});

	it('renders when logged in', async () => {
		vi.useFakeTimers('modern');
		vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
		const mockServer = new MockBingoServer(fetchMock, { currentUser: normalUser });
		const user = mockServer.getUserState(normalUser);
		const preloadedState = {
			...initialState,
			user,
		};
		const { asFragment, findByText } = renderWithProviders(<IndexPage />, { preloadedState });
		await findByText('previous Bingo games');
		expect(fetchMock.called('/api/games')).toBe(true);
		expect(asFragment()).toMatchSnapshot();
		await mockServer.shutdown();
	});
});
