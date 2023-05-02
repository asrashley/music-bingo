import React from 'react';
import { getByText } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { formatDuration } from '../../components/DateTime';
import { TrackListing } from './TrackListing';

describe('TrackListing component', () => {
  it('to render a game with 3 tracks', () => {
    const songs = [{
      "pk": 359,
      "filename": "01-48- You Spin Me Round (Like a Record) [Original 7 Mix].mp3",
      "title": "You Spin Me Round (Like a Record)",
      "duration": 30016,
      "channels": 2,
      "sample_rate": 44100,
      "sample_width": 16,
      "bitrate": 256,
      "uuid": "urn:uuid:0c76319e-65f1-5b4a-878c-bf06fe7be0ff",
      "directory": 78,
      "album": "100 Hits 80s Essentials",
      "artist": "Dead Or Alive"
    }, {
      "pk": 627,
      "filename": "15 Mad World (From 'Donnie Darko').mp3",
      "title": "Mad World (From \"Donnie Darko\")",
      "duration": 30016,
      "channels": 2,
      "sample_rate": 44100,
      "sample_width": 16,
      "bitrate": 256,
      "uuid": "urn:uuid:c7e63924-f46b-5557-a4d2-92ce83b5d21d",
      "directory": 86,
      "album": "Now That's What I Call Movies",
      "artist": "Tears For Fears"
    }, {
      "pk": 618,
      "filename": "12 Why (From 'Soup for One').mp3",
      "title": "Why (From \"Soup for One\")",
      "duration": 30016,
      "channels": 2,
      "sample_rate": 44100,
      "sample_width": 16,
      "bitrate": 257,
      "uuid": "urn:uuid:9b4557e6-ca6f-51f6-875c-15e2dc57a576",
      "directory": 86,
      "album": "Now That's What I Call Movies",
      "artist": "Carly Simon"
    }];
    const tracks = [{
      ...songs[0],
      "game": 1,
      "number": 1,
      "pk": 2,
      "start_time": 40072
    }, {
      ...songs[1],
      "game": 1,
      "number": 2,
      "pk": 3,
      "start_time": 71096
    }, {
      ...songs[2],
      "game": 1,
      "number": 3,
      "pk": 4,
      "start_time": 102120
      }];
    const game = {
      "pk": 2,
      "id": "18-04-25-2",
      "title": "Pot Luck",
      "start": "2018-04-05T20:43:00Z",
      "end": "2018-04-06T19:43:40Z",
      "options": {
        "colour_scheme": "green",
        "number_of_cards": 24,
        "include_artist": true,
        "page_size": "A4",
        "columns": 5,
        "rows": 3,
        "checkbox": false,
        "cards_per_page": 4,
        "backgrounds": ["#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9"]
      },
      "userCount": 0,
      tracks,
      ticketOrder: [2, 3, 4],
      isFetchingDetail: false,
      invalidDetail: false,
      lastUpdated: 1675455186677,
      isModifying: false,
    };
    const result = renderWithProviders(<TrackListing game={game} />);
    result.getByText(game.title, { exact: false });
    tracks.forEach(track => {
      const tid = `track[${track.pk}]`;
      const dur = formatDuration(track.duration);
      expect('dur').not.toMatch(/N?aN?/);
      const row = result.getByTestId(tid);
      expect(row).toBeVisible()
      expect(row).toHaveClass(`${game.options.colour_scheme}-theme`);
      getByText(row, track.title);
      getByText(row, track.artist);
      getByText(row, track.album);
      getByText(row, dur);
    });
    expect(result.asFragment()).toMatchSnapshot();
  });
});