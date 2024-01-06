import React from 'react';
import PropTypes from 'prop-types';

import { SongRow } from './SongRow';

export function SongListing({ depth, songs, onSelect, selected }) {
  return (
    <React.Fragment>
      {songs.map((song, idx) => (<SongRow depth={depth} song={song} onSelect={onSelect}
        key={idx} selected={selected} />))}
    </React.Fragment>
  );
}

SongListing.propTypes = {
  depth: PropTypes.number.isRequired,
  onSelect: PropTypes.func.isRequired,
  songs: PropTypes.array.isRequired,
  selected: PropTypes.object.isRequired
};
