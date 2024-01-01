import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { SongRow } from './SongRow';

describe('SongRow component', () => {
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

	it('renders without throwing an exception', () => {
		const props = {
			className: "",
			depth: 2,
			song,
			selected: {
				song,
				directory: null
			},
			onSelect: () => false
		};
		const { getByText, asFragment } = renderWithProviders(
			<table>
				<tbody>
					<SongRow {...props} />
				</tbody>
			</table>);
		getByText(song.title);
		getByText(song.artist);
		expect(asFragment()).toMatchSnapshot();
	});

	it('calls onSelect when song title is clicked', () => {
		const props = {
			className: "",
			depth: 2,
			song,
			selected: {
				song,
				directory: null
			},
			onSelect: vi.fn(() => false)
		};
		const result = renderWithProviders(
			<table>
				<tbody>
					<SongRow {...props} />
				</tbody>
			</table>);
		fireEvent.click(result.getByText(song.title));
		expect(props.onSelect).toHaveBeenCalledTimes(1);
	});
});