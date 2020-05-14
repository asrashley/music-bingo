import React from 'react';
import { reverse } from 'named-urls';
import routes from '../../routes';
import { Link } from 'react-router-dom';

function formatTime(value) {
  let hours = value.getHours();
  const ampm = value.getHours() >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  if (hours === 0) {
    hours = 12;
  }
  //hours = `0${hours}`.slice(-2);
  const minutes = `0${value.getMinutes()}`.slice(-2);
  return `${hours}:${minutes} ${ampm}`;
}

const TableRow = ({ game, past }) => {
  let ticketUrl, themeUrl, linkText;

  if (past) {
    linkText = 'View track listing';
    ticketUrl = themeUrl = reverse(`${routes.trackListing}`, { gameId: game.id });
  } else if (game.userCount === 0) {
    linkText = "Choose tickets";
    ticketUrl = reverse(`${routes.game}`, { gameId: game.id });
    themeUrl = reverse(`${routes.game}`, { gameId: game.id });
  } else {
    ticketUrl = reverse(`${routes.play}`, { gameId: game.id });
    themeUrl = reverse(`${routes.game}`, { gameId: game.id });
    linkText = `You have chosen ${game.userCount} ticket${(game.userCount > 1) ? 's' : ''}`;
  }
  const start = new Date(game.start);
  return (
    <React.Fragment>
      {game.round === 1 && (<tr>
        <th colSpan="4">{start.toDateString()}</th>
      </tr>)}
      <tr className={`round-${game.round}`}>
        <td className="round-column">{game.round}</td>
        <td className="date-column">{formatTime(start)}</td>
        <td className="theme-column"><Link to={themeUrl}>{game.title}</Link></td>
        <td className="ticket-column"><Link to={ticketUrl}>{linkText}</Link></td>
      </tr>
    </React.Fragment>
  );
};

export const BingoGamesTable = ({ title, games, past, onReload }) => {
  return (
    <table className="table table-striped table-bordered game-list">
      <thead>
        <tr>
          <th colSpan="4" className="available-games">{title}
            <button className="btn btn-light refresh-icon btn-sm" onClick={onReload}>&#x21bb;</button>
          </th>
        </tr>
        <tr>
          <th className="round-column">Round</th>
          <th className="date-column">Date and Time</th>
          <th className="theme-column">Theme</th>
          {past && <th className="ticket-column">Track listing</th>}
          {!past && <th className="ticket-column">Your Tickets</th>}
        </tr>
      </thead>
      <tbody>
        {games.map((game, idx) => (<TableRow game={game} key={idx} past={past} />))}
      </tbody>
    </table>
  );
};
