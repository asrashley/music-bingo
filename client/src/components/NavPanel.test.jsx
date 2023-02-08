import React from 'react';
import { ConnectedRouter } from 'connected-react-router';
import GitInfo from 'react-git-info/macro';

import { renderWithProviders, createJsonWithProviders } from '../testHelpers';
import { NavPanel } from './NavPanel';
import { history } from '../store/history';

import * as userData  from '../fixtures/user.json';

jest.mock('react-git-info/macro', () => {
	return function () {
		return {
			commit: {
				tags: 'tags',
				shortHash: 'githash'
			}
		};
	};
});

function NavPanelWrapper({ user }) {
	return (
		<ConnectedRouter history={history}>
			<NavPanel user={user} />
		</ConnectedRouter>
	);
}

describe('NavPanel component', () => {
	it('renders without throwing an exception', () => {
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
		const result = renderWithProviders(
			<NavPanelWrapper user={user} />);
		result.findByText(user.username);
		result.findByText('githash');
		result.findByText('Clips');
	});

	it("doesn't include clips if not a creator", () => {
		const user = {
			...userData['default'],
			groups: {
				"users": true, "creators": false, "hosts": true, "admin": false
			},
			isFetching: false,
			registering: false,
			error: null,
			lastUpdated: 1675455186677,
			didInvalidate: false
		};
		const result = renderWithProviders(
			<NavPanelWrapper user={user} />);
		result.findByText(user.username);
		result.findByText('githash');
		expect(result.queryByText('Clips')).toBe(null);
	});

	it('matches JSON snapshot', () => {
		const user = {
			...userData['default'],
			groups: {
				"users": true
			},
			isFetching: false,
			registering: false,
			error: null,
			lastUpdated: 1675455186677,
			didInvalidate: false
		};
		const { asFragment } = renderWithProviders(
			<NavPanelWrapper user={user} />);
		expect(asFragment()).toMatchSnapshot();
	});
});