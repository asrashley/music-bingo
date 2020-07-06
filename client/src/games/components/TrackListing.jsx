import React from 'react';
import PropTypes from 'prop-types';

function formatDuration(ms_dur) {
  let seconds = Math.floor(ms_dur / 1000);
  const digit = Math.floor(ms_dur / 100) % 10;
  let minutes = Math.floor(seconds / 60) % 60;
  const hours = Math.floor(seconds / 3600);
  seconds = seconds % 60;
  seconds = `0${seconds}`.slice(-2);
  minutes = `0${minutes}`.slice(-2);
  if (hours) {
    return `${hours}:${minutes}:${seconds}.${digit}`;
  }
  return `${minutes}:${seconds}.${digit}`;
}

const TableRow = ({ game, track }) => {
  let rowClass = "track";
  if (game.options && game.options.colour_scheme) {
    rowClass += ` ${game.options.colour_scheme}-theme`;
  }

  return (
    <tr className={rowClass}>
      <td className="number">{track.number + 1}</td>
      <td className="start-time">{formatDuration(track.start_time)}</td>
      <td className="title">{track.title}</td>
      <td className="artist">{track.artist}</td>
      <td className="album">{track.album}</td>
      <td className="duration">{formatDuration(track.duration)}</td>
    </tr>

    )
}

export class TrackListing extends React.Component {
  static propTypes = {
    game: PropTypes.object.isRequired,
  };
  render() {
    const { game } = this.props;
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
}