import React from 'react';

import { renderWithProviders } from '../../testHelpers';
import { DirectoryChildren } from './DirectoryChildren';

describe('DirectoryChildren component', () => {
	it('renders songs in a directory', () => {
		const song = {
			"directory": 1,
			"pk": 1,
			"filename": "01-25- Ghostbusters.mp3",
			"title": "Ghostbusters",
			"artist": "Ray Parker Jr",
			"duration": 30016,
			"channels": 2,
			"sample_rate": 44100,
			"sample_width": 16,
			"bitrate": 256,
			"album": "100 Hits 80s Essentials",
			"uuid": "urn:uuid:7dcc81f2-5dbe-5973-9556-494d94cf0f77"
		};
		const directory = {
			pk: 1,
			name: "Clips/TV Themes",
			title: "TV Themes",
			artist: "",
			directories: [],
			songs: [song],
			valid: true,
		};
		const props = {
			depth: 1,
			directory,
			options: {},
			onSelect: () => false,
			onVisibilityToggle: () => false,
			selected: {
				song,
				directory: null
			},
		};
		const result = renderWithProviders(
			<table>
				<tbody>
					<DirectoryChildren {...props} />
				</tbody>
			</table>);
		result.getByText(song.title);
		result.getByText(song.artist);
	});

	it('renders sub-directories of a directory', () => {
		const song = {
			"directory": 1,
			"pk": 1,
			"filename": "01-25- Ghostbusters.mp3",
			"title": "Ghostbusters",
			"artist": "Ray Parker Jr",
			"duration": 30016,
			"channels": 2,
			"sample_rate": 44100,
			"sample_width": 16,
			"bitrate": 256,
			"album": "100 Hits 80s Essentials",
			"uuid": "urn:uuid:7dcc81f2-5dbe-5973-9556-494d94cf0f77"
		};
		const directory = {
			pk: 1,
			name: "Clips",
			title: "Clips",
			artist: "",
			directories: [{
				pk: 2,
				name: "Clips/TV Themes",
				title: "TV Themes",
				artist: "",
				directories: [],
				songs: [song],
				parent: 1,
				valid: true,
			}],
			songs: [],
			valid: true,
		};
		const props = {
			depth: 1,
			directory,
			options: {},
			onSelect: () => false,
			onVisibilityToggle: () => false,
			selected: {
				song: null,
				directory: null
			},
		};
		const result = renderWithProviders(
			<table>
				<tbody>
					<DirectoryChildren {...props} />
				</tbody>
			</table>);
		directory.directories.forEach((item) => {
			result.getByText(item.title);
		});
	});

});