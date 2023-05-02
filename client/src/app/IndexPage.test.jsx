import React from 'react';
import { screen } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { renderWithProviders, installFetchMocks } from '../testHelpers';
import { IndexPage } from './IndexPage';

import { initialState } from '../store/initialState';

describe('IndexPage component', () => {
	beforeAll(() => {
		jest.useFakeTimers('modern');
		jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});

	afterAll(() => jest.useRealTimers());

	beforeEach(() => {
		installFetchMocks(fetchMock, { loggedIn: false });
	});

	it('renders without throwing an exception with initial state', () => {
		const result = renderWithProviders(<IndexPage />);
		result.getByText("You need a registered account to play Musical Bingo.", { exact: false });
	});

	it('renders when logged in', async () => {
		const userData = await import('../fixtures/userState.json');
		const user = {
			...userData['default'],
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
		const { asFragment } = renderWithProviders(<IndexPage />, { preloadedState });
		await screen.findByText('previous Bingo games');
		expect(fetchMock.called('/api/games')).toBe(true);
		expect(asFragment()).toMatchSnapshot();
	});
});
