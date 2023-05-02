import React from 'react';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';
import { screen } from '@testing-library/react';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { LogoutPage } from './LogoutPage';

import * as user from '../../fixtures/userState.json';

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
		const result = renderWithProviders(
			<LogoutPage {...props} />, { store });
		result.getByText(`Goodbye ${props.user.username}`);
		await waitForExpect(() => {
			expect(apiMock.isLoggedIn()).toBe(false);
		});
		await screen.findByText(`Goodbye ${props.user.username}`);
	});
});