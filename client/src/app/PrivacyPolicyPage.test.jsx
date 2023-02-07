import React from 'react';
import { screen } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { renderWithProviders, createJsonWithProviders, installFetchMocks } from '../testHelpers';
import { PrivacyPolicyPage } from './PrivacyPolicyPage';

import { initialState } from '../store/initialState';

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

	it('renders without throwing an exception with initial state', () => {
		renderWithProviders(<PrivacyPolicyPage />);
	});

	it('renders with privacy policy settings loaded', async () => {
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
		const { store } = renderWithProviders(<PrivacyPolicyPage />, { preloadedState });
		await screen.findByText(completePolicy.name.value);
		screen.getAllByText(completePolicy.email.value);
		screen.getByText(completePolicy.address.value);
		screen.getByText(completePolicy.data_center.value);
		screen.getByText('an.ico.site');
		// check that no API requets were made
		expect(fetchMock.called()).toBe(false);
		const { tree } = createJsonWithProviders(<PrivacyPolicyPage />, { store });
		expect(tree).toMatchSnapshot();
	});

	it('loads privacy settings', async () => {
		//log.setLevel("trace");
		renderWithProviders(<PrivacyPolicyPage />);
		await screen.findByText(completePolicy.name.value);
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});
});
