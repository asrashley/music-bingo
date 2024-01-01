import React from 'react';
import PropTypes from 'prop-types';
import { reverse } from 'named-urls';
import { routes } from '../../routes/routes';
import { Link } from 'react-router-dom';

import { DateTime } from '../../components/DateTime';

import { GamePropType } from '../types/Game';
import { UserPropType } from '../../user/types/User';

const TableRow = ({ game, past, user, slug }) => {
  let ticketColumn, idColumn, themeColumn;
  let rowClass = `round-${game.round}`;

  if (past) {
    themeColumn = <Link to={reverse(`${routes.pastGamesByTheme}`, { slug: game.slug })}>
      {game.title}
    </Link>;
    if (user.groups?.guests === true) {
      idColumn = <span>{game.id}</span>;
      ticketColumn = (<span>Log in to view track listing</span>);
    } else {
      const url = slug ?
        reverse(`${routes.trackListingByTheme}`, { slug, gameId: game.id }) :
        reverse(`${routes.trackListing}`, { gameId: game.id });
      idColumn = (<Link to={url}>{game.id}</Link>);
      ticketColumn = (<Link to={url}>View track listing</Link>);
    }
  } else if (game.userCount === 0) {
    const url = reverse(`${routes.chooseTickets}`, { gameId: game.id });
    idColumn = (<Link to={url}>{game.id}</Link>);
    themeColumn = (<Link to={url}>{game.title}</Link>);
    ticketColumn = (<Link to={url}>Choose tickets</Link>);
  } else {
    const ticketUrl = reverse(`${routes.play}`, { gameId: game.id });
    const themeUrl = reverse(`${routes.chooseTickets}`, { gameId: game.id });
    idColumn = (<Link to={themeUrl} > {game.id}</Link>);
    themeColumn = (<Link to={themeUrl} > {game.title}</Link>);
    ticketColumn = (<Link to={ticketUrl}>You have chosen {game.userCount} ticket{(game.userCount > 1) ? 's' : ''}</Link>);
  }
  if (game.options && game.options.colour_scheme) {
    rowClass += ` ${game.options.colour_scheme}-theme`;
  }
  const start = new Date(game.start);
  return (
    <React.Fragment>
      {game.firstGameOfTheDay === true && (<tr>
        <th colSpan="5">{start.toDateString()}</th>
      </tr>)}
      <tr className={rowClass} data-testid={`${past ? "past" : ""}game[${game.pk}]`}>
        <td className="round-column">{game.round}</td>
        <td className="date-column"><DateTime date={start} ampm={true} /></td>
        <td className="game-id-column">{idColumn}</td>
        <td className="theme-column">{themeColumn}</td>
        <td className="ticket-column">{ticketColumn}</td>
      </tr>
    </React.Fragment>
  );
};
TableRow.propTypes = {
  game: GamePropType.isRequired,
  past: PropTypes.bool,
  user: UserPropType.isRequired,
  slug: PropTypes.string,
};

export const BingoGamesTable = ({ title, games, past, onReload, footer, user, slug }) => {
  return (
    <table className="table table-bordered game-list">
      <thead>
        <tr>
          <th colSpan="5" className="available-games">{title}
            <button className="btn btn-light refresh-icon btn-sm" aria-label="Reload" onClick={onReload}>&#x21bb;</button>
          </th>
        </tr>
        <tr>
          <th className="round-column">Round</th>
          <th className="date-column">Date and Time</th>
          <th className="game-id-column">Game ID</th>
          <th className="theme-column">Theme</th>
          {past && <th className="ticket-column">Track listing</th>}
          {!past && <th className="ticket-column">Your Tickets</th>}
        </tr>
      </thead>
      <tbody>
        {games.map((game, idx) => (<TableRow game={game} key={idx} past={past} user={user} slug={slug} />))}
      </tbody>
      {footer && <tfoot>{footer}</tfoot>}
    </table>
  );
};

BingoGamesTable.propTypes = {
  title: PropTypes.string.isRequired,
  games: PropTypes.arrayOf(GamePropType).isRequired,
  past: PropTypes.bool,
  onReload: PropTypes.func.isRequired,
  footer: PropTypes.node,
  user: UserPropType.isRequired,
  slug: PropTypes.string,
};
