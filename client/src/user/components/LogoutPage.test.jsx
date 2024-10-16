import React from 'react';
import { waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders } from '../../../tests';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { LogoutPage } from './LogoutPage';
import { afterEach } from 'vitest';

describe('LogoutPage component', () => {
	afterEach(() => {
		fetchMock.reset();
	});

	it('logs out user after LogoutPage has rendered', async () => {
		const apiMock = new MockBingoServer(fetchMock, { loggedIn: true });
		const user = apiMock.getUserState(normalUser);
		const store = createStore({
			...initialState,
			user,
		});
		const props = {
			user,
			dispatch: store.dispatch,
		};

		expect(apiMock.isLoggedIn(normalUser)).toBe(true);
		const { findByText, getByText } = renderWithProviders(
			<LogoutPage {...props} />, { store });
		getByText(`Goodbye ${props.user.username}`);
		await waitFor(() => {
			expect(apiMock.isLoggedIn(normalUser)).toBe(false);
		});
		await findByText(`Goodbye ${props.user.username}`);
	});
});