import React from 'react';

import { formatDuration } from '../../components/DateTime';
import { GamePropType } from '../types/Game';
import { TrackPropType } from '../types/Track';

const TableRow = ({ game, track }) => {
  let rowClass = "track";
  if (game.options && game.options.colour_scheme) {
    rowClass += ` ${game.options.colour_scheme}-theme`;
  }

  return (
    <tr className={rowClass} data-testid={ `track[${track.pk}]`}>
      <td className="number">{track.number + 1}</td>
      <td className="start-time">{formatDuration(track.start_time)}</td>
      <td className="title">{track.title}</td>
      <td className="artist">{track.artist}</td>
      <td className="album">{track.album}</td>
      <td className="duration">{formatDuration(track.duration)}</td>
    </tr>

  );
};

TableRow.propTypes = {
  game: GamePropType,
  track: TrackPropType
};

export function TrackListing({ game }) {
  return (
    <div>
      <table className="table table-bordered track-listing">
        <thead>
          <tr>
            <th colSpan="6" className="heading">Track listing for Game {game.id}: "{game.title}"</th>
          </tr>
          <tr>
            <th className="number">#</th>
            <th className="start-time">Start</th>
            <th className="title">Title</th>
            <th className="artist">Artist</th>
            <th className="album">Album</th>
            <th className="duration">Duration</th>
          </tr>
        </thead>
        <tbody>
          {game.tracks.map((track, idx) => (<TableRow track={track} game={game} key={idx} />))}
        </tbody>
      </table>
    </div>
  );
}

TrackListing.propTypes = {
  game: GamePropType,
};
