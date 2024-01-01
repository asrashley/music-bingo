import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks } from '../testHelpers';
import { PrivacyPolicyPage } from './PrivacyPolicyPage';

import { initialState } from '../store/initialState';
import userData from '../fixtures/userState.json';

describe('PrivacyPolicy component', () => {
	const completePolicy = {
		name: {
			"help": "Company Name",
			"name": "name",
			"title": "Name",
			"value": "Acme Widgets",
			"type": "text"
		},
		email: {
			"help": "Company Email",
			"name": "email",
			"title": "Email",
			"value": "acme@unit.test",
			"type": "text"
		},
		address: {
			"help": "Company Address",
			"name": "address",
			"title": "Address",
			"value": "One Simple Test",
			"type": "text"
		},
		data_center: {
			"help": "Data Center",
			"name": "data_center",
			"title": "Data Center",
			"value": "eu-west-1",
			"type": "text"
		},
		ico: {
			"help": "Information Commissioner URL",
			"name": "ico",
			"title": "Ico",
			"value": "https://an.ico.site",
			"type": "text"
		}
	};

	beforeEach(() => {
		installFetchMocks(fetchMock, { loggedIn: false });
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});

	it('renders without throwing an exception with initial state', async () => {
		const { findByText } = renderWithProviders(<PrivacyPolicyPage />);
		await findByText('Musical Bingo Privacy Policy');
		await screen.findByText(completePolicy.name.value);
	});

	it('renders with privacy policy settings loaded', async () => {
		const user = {
			...userData,
			groups: {
				"users": true, "creators": true, "hosts": true, "admin": true
			},
			isFetching: false,
			registering: false,
			error: null,
			lastUpdated: 1675455186677,
			didInvalidate: false
		};
		const settings = {
			...initialState.settings,
			sections: {
				privacy: {
					settings: completePolicy,
					order: ["name", "email", "address", "data_center", "ico"],
					valid: true
				}
			},
			invalid: false,
			error: null,
			lastUpdated: user.lastUpdated,
			user: user.pk,
		};
		const preloadedState = {
			...initialState,
			user,
			settings
		};
		const { asFragment, findByText, getAllByText, getByText } = renderWithProviders(
			<PrivacyPolicyPage />, { preloadedState });
		await findByText(completePolicy.name.value);
		getAllByText(completePolicy.email.value);
		getByText(completePolicy.address.value);
		getByText(completePolicy.data_center.value);
		getByText('an.ico.site');
		// check that no API requets were made
		expect(fetchMock.called()).toBe(false);
		expect(asFragment()).toMatchSnapshot();
	});

});
