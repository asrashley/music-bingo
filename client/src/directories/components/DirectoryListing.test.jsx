import React from 'react';

import { renderWithProviders } from '../../../tests';
import { DirectoryListing } from './DirectoryListing';

describe('DirectoryListing component', () => {
	it('renders without throwing an exception', () => {
		const song = {
			"directory": 1,
			"pk": 1,
		};
		const directory = {
			pk: 1,
			name: "Clips/TV Themes",
			title: "TV Themes",
			artist: "",
			directories: [],
			songs: [song],
		};
		const props = {
			depth: 1,
			songs: [song],
			options: {},
			directories: [
				directory
			],
			selected: {
				song,
				directory: null
			},
			onSelect: () => false,
			onVisibilityToggle: () => false
		};
		const result = renderWithProviders(
			<table>
				<tbody>
					<DirectoryListing {...props} />
				</tbody>
			</table>);
		result.getByText(directory.title);
	});
});