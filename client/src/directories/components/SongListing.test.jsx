import React from 'react';

import { renderWithProviders } from '../../testHelpers';
import { SongListing } from './SongListing';

describe('SongListing component', () => {
	it('renders without throwing an exception', () => {
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
		const props = {
			depth: 1,
			songs: [song],
			selected: {
				song,
				directory: null
			},
			onSelect: () => false
		};
		const result = renderWithProviders(
			<table>
				<tbody>
					<SongListing {...props} />
				</tbody>
			</table>);
		result.getByText(song.title);
		result.getByText(song.artist);
	});
});