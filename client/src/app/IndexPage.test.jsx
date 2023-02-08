import React from 'react';
import { screen } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';
import { ConnectedRouter } from 'connected-react-router';

import { renderWithProviders, createJsonWithProviders, installFetchMocks } from '../testHelpers';
import { IndexPage } from './IndexPage';

import { initialState } from '../store/initialState';
import { history } from '../store/history';

function IndexPageWrapper() {
	return (
		<ConnectedRouter history={history}>
			<IndexPage />
		</ConnectedRouter>
	);
}

describe('IndexPage component', () => {
	beforeEach(() => {
		installFetchMocks(fetchMock, { loggedIn: false });
	});

	it('renders without throwing an exception with initial state', () => {
		const result = renderWithProviders(<IndexPageWrapper />);
		result.findByText("You need a registered account to play Musical Bingo.");
	});

	it('renders when logged in', async () => {
		const userData = await import('../fixtures/user.json');
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
		const { store } = renderWithProviders(<IndexPageWrapper />, { preloadedState });
		await screen.findByText('previous Bingo games');
		expect(fetchMock.called('/api/games')).toBe(true);
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});
});
