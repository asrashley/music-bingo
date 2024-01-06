import React from 'react';
import PropTypes from 'prop-types';

export function SongRow({ onSelect, depth, song, selected }) {
  let className = "song";
  if (selected.song?.pk === song.pk) {
    className += ' is-selected';
  }
  return (
    <tr className={className}>
      <td className="select"></td>
      <td className="title" style={{ paddingLeft: `${depth}em` }}>
        <button className="btn btn-link song-link" onClick={(ev) => { ev.preventDefault(); onSelect({ song }); }} >
          {song.title}
        </button>
      </td>
      <td className="artist">
        {song.artist}
      </td>
    </tr>
  );
}

SongRow.propTypes = {
  depth: PropTypes.number.isRequired,
  selected: PropTypes.object.isRequired,
  song: PropTypes.object.isRequired,
  onSelect: PropTypes.func.isRequired
};

