import React from 'react';
import { vi, describe, it, expect } from 'vitest';
import { act } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks } from '../testHelpers';
import { IndexPage } from './IndexPage';

import { initialState } from '../store/initialState';
import userState from '../fixtures/userState.json';

describe('IndexPage component', () => {

	afterAll(() => {
		vi.resetAllMocks();
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
		vi.useRealTimers();
	});

	it('renders without throwing an exception with initial state', async () => {
		const userFetchProm = new Promise(resolve => {
			fetchMock.get('/api/user', async (url) => {
				resolve(url);
				return 401;
			});
		});
		const { findByText } = renderWithProviders(<IndexPage />);
		await act(async () => {
			await userFetchProm;
		});
		await findByText("You need a registered account to play Musical Bingo.", { exact: false });
	});

	it('renders when logged in', async () => {
		vi.useFakeTimers('modern');
		vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
		const user = {
			...userState,
			groups: {
				"users": true, "creators": true, "hosts": true, "admin": true
			},
			isFetching: false,
			registering: false,
			error: null,
			lastUpdated: 1675455186677,
			didInvalidate: false
		};
		const preloadedState = {
			...initialState,
			user,
		};
		installFetchMocks(fetchMock, { loggedIn: true });
		const { asFragment, findByText } = renderWithProviders(<IndexPage />, { preloadedState });
		await findByText('previous Bingo games');
		expect(fetchMock.called('/api/games')).toBe(true);
		expect(asFragment()).toMatchSnapshot();
	});
});
