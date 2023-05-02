import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders, installFetchMocks, jsonResponse } from '../../testHelpers';
import { DirectoryListPage } from './DirectoryListPage';
import { initialState } from '../../store/initialState';
import * as user from '../../fixtures/userState.json';

describe('DirectoryListPage component', () => {
	beforeEach(() => {
		installFetchMocks(fetchMock, { loggedIn: true });
	});
	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});
	afterEach(() => log.resetLevel());
	it('renders a directory', async () => {
		const location = {
				params: {
					dirPk: 1
				}
		};
		//log.setLevel('debug');
		const { asFragment } = renderWithProviders(<DirectoryListPage match={location} /> /*, { preloadedState }*/);
		await screen.findByText("100 Nows");
		expect(asFragment()).toMatchSnapshot();
	});

	it('fetches directories if component is mounted when the user has already logged in', async () => {
		const preloadedState = {
			...initialState,
			tickets: {
				...initialState.tickets,
				user: user.pk
      },
			user
		};
		const location = {
			params: {
				dirPk: 1
			}
		};
		//log.setLevel('debug');
		renderWithProviders(<DirectoryListPage match={location} />, { preloadedState });
		await screen.findByText("100 Nows");
	});

	it('toggles showing songs', async () => {
		const preloadedState = {
			...initialState,
			tickets: {
				...initialState.tickets,
				user: user.pk
			},
			user
		};
		const location = {
			params: {
				dirPk: 1
			}
		};
		//log.setLevel('debug');
		renderWithProviders(<DirectoryListPage match={location} />, { preloadedState });
		await screen.findByText("100 Nows");
		fireEvent.click(screen.getByTestId('dir-toggle-1'));
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
		const location = {
			params: {
			}
		};
		await new Promise((resolve) => {
			fetchMock.get('/api/song?q=Prince', async (url, opts) => {
				const queryData = await import('../../fixtures/song/query.json');
				resolve();
				return jsonResponse(queryData['default']);
			});
			//log.setLevel('debug');
			renderWithProviders(<DirectoryListPage match={location} />, { preloadedState });
			fireEvent.input(screen.getByPlaceholderText("search..."), {
				target: {
					value: 'Prince'
				}
			});
		});
		await screen.findByText("Play In The Sunshine");
	});
});