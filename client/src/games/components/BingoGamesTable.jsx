import React from 'react';
import { reverse } from 'named-urls';
import routes from '../../routes';
import { Link } from 'react-router-dom';

import { DateTime } from '../../components';

const TableRow = ({ game, past }) => {
  let ticketUrl, themeUrl, linkText;

  if (past) {
    linkText = 'View track listing';
    ticketUrl = themeUrl = reverse(`${routes.trackListing}`, { gamePk: game.pk });
  } else if (game.userCount === 0) {
    linkText = "Choose tickets";
    ticketUrl = reverse(`${routes.game}`, { gamePk: game.pk });
    themeUrl = reverse(`${routes.game}`, { gamePk: game.pk });
  } else {
    ticketUrl = reverse(`${routes.play}`, { gamePk: game.pk });
    themeUrl = reverse(`${routes.game}`, { gamePk: game.pk });
    linkText = `You have chosen ${game.userCount} ticket${(game.userCount > 1) ? 's' : ''}`;
  }
  return (
    <tr>
      <td className="round-column">{game.gameRound}</td>
      <td className="date-column">
        <DateTime date={game.start} withTime={false} />
      </td>
      <td className="theme-column">
        <Link to={themeUrl}>{game.title}</Link>
      </td>
      <td className="ticket-column">
        <Link to={ticketUrl}>{linkText}</Link>
      </td>
    </tr>
  );
};

export const BingoGamesTable = ({ title, games, past }) => {
  return (
    <table className="table table-striped table-bordered game-list">
      <thead>
        <tr>
          <th colSpan="4" className="available-games">{title}</th>
        </tr>
        <tr>
          <th className="round-column">Round</th>
          <th className="date-column">Date</th>
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
