import React from 'react';

import { renderWithProviders } from '../../testHelpers';
import { DetailsPanel } from './DetailsPanel';

describe('DetailsPanel component', () => {
	it('returns an empty div if nothing is selected', () => {
		const props = {
			selected: {
				directory: null,
				song: null
			},
			directoryMap: {}
		};
		const { asFragment } = renderWithProviders(<DetailsPanel {...props} />);
		const expected = renderWithProviders(<div />).asFragment();
		expect(asFragment()).toStrictEqual(expected);
	});

	it('renders song details when a song is selected', () => {
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
		const directoryMap = {
			1: {
				pk: 1,
				name: "/home/users/alex/musicbingo/Clips/TV Themes",
				title: "TV Themes",
				artist: "",
				directories: [],
				songs: [song],
      }
		};
		const props = {
			selected: {
				directory: null,
				song
			},
			directoryMap
		};

		const result = renderWithProviders(<DetailsPanel {...props} />);
		for (const [key, value] of Object.entries(song)) {
			result.getByText(key);
			result.getByText(`${value}`);
    }
	});

	it('renders directory details when a directory is selected', () => {
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
		const directoryMap = {
			1: {
				pk: 1,
				name: "/home/users/alex/musicbingo/Clips/TV Themes",
				title: "TV Themes",
				artist: "",
				directories: [],
				songs: [song],
			}
		};
		const props = {
			selected: {
				directory: directoryMap[1],
				song: null
			},
			directoryMap
		};

		const result = renderWithProviders(
			<DetailsPanel {...props} />);
		result.getByText(directoryMap[1].title);
		result.getByText(directoryMap[1].name);
		result.getByText(`${directoryMap[1].pk}`);
		result.getByText('1 song');
	});
});