import React from 'react';

import { renderWithProviders } from '../../testHelpers';
import { DirectoryRow } from './DirectoryRow';

describe('DirectoryRow component', () => {
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
			directory,
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
					<DirectoryRow {...props} />
				</tbody>
			</table>);
		result.getByText(directory.title);
	});
});