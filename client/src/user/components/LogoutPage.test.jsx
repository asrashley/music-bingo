import React from 'react';
import { waitFor } from '@testing-library/react';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { LogoutPage } from './LogoutPage';

import user from '../../fixtures/userState.json';

describe('LogoutPage component', () => {
	it('calls onCancel() and onConfirm() when buttons are clicked', async () => {
		const store = createStore({
			...initialState,
			user,
		});
		const apiMock = installFetchMocks(fetchMock, { loggedIn: true });
		const props = {
			user,
			dispatch: store.dispatch,
		};

		expect(apiMock.isLoggedIn()).toBe(true);
		const { findByText, getByText } = renderWithProviders(
			<LogoutPage {...props} />, { store });
		getByText(`Goodbye ${props.user.username}`);
		await waitFor(() => {
			expect(apiMock.isLoggedIn()).toBe(false);
		});
		await findByText(`Goodbye ${props.user.username}`);
	});
});