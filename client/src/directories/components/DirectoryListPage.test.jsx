import React from 'react';
import { act } from '@testing-library/react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks, jsonResponse } from '../../../tests';
import { DirectoryListPage } from './DirectoryListPage';
import { initialState } from '../../store/initialState';
import user from '../../../tests/fixtures/userState.json';

describe('DirectoryListPage component', () => {
	beforeEach(() => {
		installFetchMocks(fetchMock, { loggedIn: true });
	});

	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});

	it('renders empty directory if not logged in', async () => {
		//log.setLevel('debug');
		const { findByText } = renderWithProviders(<DirectoryListPage />);
		await findByText('Title');
		await findByText('Artist');
	});

	it('fetches directories if component is mounted when user logged in', async () => {
		const preloadedState = {
			...initialState,
			tickets: {
				...initialState.tickets,
				user: user.pk
			},
			routes: {
				params: {
					dirPk: 1,
				}
			},
			user
		};
		//log.setLevel('debug');
		const { asFragment, findByText } = renderWithProviders(<DirectoryListPage />, { preloadedState });
		await findByText("100 Nows");
		expect(asFragment()).toMatchSnapshot();
	});

	it('toggles showing songs', async () => {
		const preloadedState = {
			...initialState,
			tickets: {
				...initialState.tickets,
				user: user.pk
			},
			routes: {
				params: {
					dirPk: 1,
				}
			},
			user
		};
		//log.setLevel('debug');
		const { findByText, findByTestId, events } = renderWithProviders(
			<DirectoryListPage />, { preloadedState });
		await findByText("100 Nows");
		await events.click(await findByTestId('dir-toggle-1'));
	});

	it('searches for songs', async () => {
		const preloadedState = {
			...initialState,
			tickets: {
				...initialState.tickets,
				user: user.pk
			},
			user
		};
		const fetchProm = new Promise((resolve) => {
			fetchMock.get('/api/song?q=Prince', async () => {
				const queryData = await import('../../../tests/fixtures/song/query.json');
				resolve();
				return jsonResponse(queryData['default']);
			});
		});
		//log.setLevel('debug');
		const { findByText, getByPlaceholderText, events } = renderWithProviders(
			<DirectoryListPage />, { preloadedState });
		await events.type(getByPlaceholderText("search..."), 'Prince');
		await act(async () => await fetchProm);
		await findByText("Play In The Sunshine");
	});
});