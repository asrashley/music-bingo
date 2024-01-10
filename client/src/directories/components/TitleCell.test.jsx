import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../../tests';
import { TitleCell } from './TitleCell';

describe('TitleCell component', () => {
  it('renders without throwing an exception', () => {
    const directory = {
      directories: [],
      songs: [],
      title: 'Directory Title'
    };
    const props = {
      className: "",
      directory,
      onSelect: () => false,
      onVisibilityToggle: () => false
    };
    const result = renderWithProviders(<TitleCell {...props} />);
    result.findByText(directory.title);
  });

  it('calls onVisibilityToggle when directory title is clicked', () => {
    const directory = {
      directories: [],
      songs: [{
        "pk": 288,
        "filename": "02_little_red_corvette.mp3",
        "title": "Little Red Corvette",
        "duration": 19998,
        "channels": 2,
        "sample_rate": 44100,
        "sample_width": 16,
        "bitrate": 128,
        "uuid": "urn:uuid:d2a8c24d-d58c-53f1-8e1c-c578c1b1a165",
        "directory": 5,
        "artist": "Prince",
        "album": "1999"
      },
      {
        "pk": 300,
        "filename": "09_purple_rain.mp3",
        "title": "Purple Rain",
        "duration": 19998,
        "channels": 2,
        "sample_rate": 44100,
        "sample_width": 16,
        "bitrate": 128,
        "uuid": "urn:uuid:001dbb20-8a87-5796-bc7b-e71a6802e3d7",
        "directory": 5,
        "artist": "Prince",
        "album": "Purple Rain"
      }],
      title: 'Directory Title'
    };
    const props = {
      className: "",
      directory,
      onSelect: vi.fn(() => false),
      onVisibilityToggle: vi.fn(() => false)
    };
    const { getByText } = renderWithProviders(<TitleCell {...props} />);
    fireEvent.click(getByText(directory.title));
    expect(props.onVisibilityToggle).toHaveBeenCalledTimes(1);
    expect(props.onSelect).toHaveBeenCalledTimes(0);
  });

  it('calls onSelect when directory title is clicked', () => {
    const directory = {
      directories: [],
      songs: [],
      title: 'Directory Title'
    };
    const props = {
      className: "",
      directory,
      onSelect: vi.fn(() => false),
      onVisibilityToggle: vi.fn(() => false)
    };
    const { getByText } = renderWithProviders(<TitleCell {...props} />);
    fireEvent.click(getByText(directory.title));
    expect(props.onSelect).toHaveBeenCalledTimes(1);
    expect(props.onVisibilityToggle).toHaveBeenCalledTimes(0);
  });
});