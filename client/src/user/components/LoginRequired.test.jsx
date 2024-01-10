import React from 'react';
import log from 'loglevel';

import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, installFetchMocks } from '../../../tests';
import { LoginRequired } from './LoginRequired';

import user from '../../../tests/fixtures/userState.json';

describe('LoginRequired component', () => {
	beforeEach(() => {
		log.setLevel('silent');
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});

	it('shows login dialog if not logged in', async () => {
		const history = {
			push: vi.fn()
		};
		installFetchMocks(fetchMock, { loggedIn: false });
		const { findByText } = renderWithProviders(
			<LoginRequired history={history} />, { preloadedState: initialState });
		await findByText("Log into Musical Bingo");
	});

	it('is empty if logged in', async () => {
		const preloadedState = {
			...initialState,
			user
		};
		const history = {
			push: vi.fn()
		};
		installFetchMocks(fetchMock, { loggedIn: true });
		const { queryByText, findByText } = renderWithProviders(
			<LoginRequired history={history}><div>Already logged in</div></LoginRequired>, { preloadedState });
		await findByText('Already logged in');
		expect(queryByText("Log into Musical Bingo")).toBe(null);
	});
});