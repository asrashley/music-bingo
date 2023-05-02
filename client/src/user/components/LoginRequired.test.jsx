import React from 'react';

import { initialState } from '../../store/initialState';
import { renderWithProviders } from '../../testHelpers';
import { LoginRequired } from './LoginRequired';

import * as user from '../../fixtures/userState.json';

describe('LoginRequired component', () => {
	it('shows login dialog if not logged in', async () => {
		const history = {
			push: jest.fn()
		};
		const result = renderWithProviders(
			<LoginRequired history={history} />, { preloadedState: initialState });
		result.getByText("Log into Musical Bingo");
	});

	it('is empty if logged in', () => {
		const preloadedState = {
			...initialState,
			user
		};
		const history = {
			push: jest.fn()
		};
		const result = renderWithProviders(
			<LoginRequired history={history} />, { preloadedState });
		expect(result.queryByText("Log into Musical Bingo")).toBe(null);
	});
});