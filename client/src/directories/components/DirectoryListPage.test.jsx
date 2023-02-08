import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { screen } from '@testing-library/react';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { DirectoryListPage } from './DirectoryListPage';
//import { initialState } from '../../store/initialState';

//import { DirectoryInitialState } from '../directoriesSlice';

describe('DirectoryListPage component', () => {
	beforeEach(() => {
		installFetchMocks(fetchMock, { loggedIn: true });
	});
	afterEach(() => {
		fetchMock.mockReset();
		log.resetLevel();
	});
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
	afterEach(() => log.resetLevel());
});