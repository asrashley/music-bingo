import React, { useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import { push } from '@lagunovsky/redux-react-router';
import { reverse } from 'named-urls';

/* components */
import { BingoTicketIcon } from './BingoTicketIcon';
import { TrackListing, ModifyGame } from '../../games/components';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchTicketsIfNeeded, fetchTicketsStatusUpdateIfNeeded } from '../ticketsSlice';
import { fetchGamesIfNeeded, fetchDetailIfNeeded, invalidateGameDetail } from '../../games/gamesSlice';
import { fetchUsersIfNeeded } from '../../admin/adminSlice';

/* selectors */
import { getMyGameTickets, getGameTickets, getLastUpdated } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';
import { getUsersMap } from '../../admin/adminSelectors';

/* data */
import { routes } from '../../routes/routes';

/* prop types */
import { GamePropType } from '../../games/types/Game';

import '../styles/tickets.scss';

function Instructions({ game, selected, maxTickets }) {
  if (selected === 0) {
    return (<p className="instructions">Please select a Bingo Ticket</p>);
  }
  const link = <Link to={reverse(`${routes.play}`, { gameId: game.id })}
    className="btn btn-primary play-game">Let&apos;s play!</Link>;
  let text = (selected === 1) ?
    "You have selected a ticket" : `You have selected ${selected} tickets`;
  if (selected === maxTickets) {
    text += ' and cannot select any additional tickets';
  }
  return (
    <p className="instructions">{text}{link}</p>
  );
}
Instructions.propTypes = {
  game: GamePropType.isRequired,
  selected: PropTypes.number.isRequired,
  maxTickets: PropTypes.number.isRequired
};

const ticketPollInterval = 5000;

function pollForTicketChanges(dispatch, gamePk) {
  function poll() {
    if (gamePk > 0) {
      dispatch(fetchTicketsStatusUpdateIfNeeded(gamePk));
    }
  }
  return window.setInterval(poll, ticketPollInterval);
}

export function ChooseTicketsPage() {
  const dispatch = useDispatch();
  const routeParams = useParams();
  const user = useSelector(getUser);
  const usersMap = useSelector(getUsersMap);
  const game = useSelector((state) => getGame(state, { routeParams }));
  const tickets = useSelector((state) => getGameTickets(state, { routeParams }));
  const myTickets = useSelector((state) => getMyGameTickets(state, { routeParams }));
  const lastUpdated = useSelector(getLastUpdated);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.loggedIn) {
      dispatch(fetchGamesIfNeeded());
      if (user.groups.admin === true || user.groups.hosts === true) {
        dispatch(fetchUsersIfNeeded());
      }
    }
  }, [dispatch, user]);

  useEffect(() => {
    if (game.pk > 0) {
      dispatch(fetchTicketsIfNeeded(game.pk));
      if (user.groups.admin === true || user.groups.hosts === true) {
        dispatch(fetchDetailIfNeeded(game.pk));
      }
    }
    const gamePoll = pollForTicketChanges(dispatch, game.pk);
    return () => {
      window.clearInterval(gamePoll);
    }
  }, [dispatch, game.pk, user.groups]);

  const onGameDelete = useCallback(() => {
    dispatch(push(`${routes.index}`));
  }, [dispatch]);

  const reload = useCallback(() => {
    dispatch(invalidateGameDetail({ game }));
    dispatch(fetchTicketsIfNeeded(game.pk));
    if (user.groups.admin === true) {
      dispatch(fetchDetailIfNeeded(game.pk));
      dispatch(fetchUsersIfNeeded());
    }
  }, [dispatch, game, user.groups.admin]);

  return (
    <div>
      <div
        className="ticket-chooser"
        data-last-update={lastUpdated}
        data-game-last-update={game.lastUpdated} >
        <h1>The theme of this round is &quot;{game.title}&quot;</h1>
        <Instructions game={game} maxTickets={user.options.maxTickets} selected={myTickets.length} />
        {tickets.map((ticket, key) => <BingoTicketIcon
          ticket={ticket}
          key={key}
          game={game}
          user={user}
          usersMap={usersMap}
          maxTickets={user.options.maxTickets}
          selected={myTickets.length}
        />)}
      </div>
      {user.groups.admin === true && <ModifyGame
        game={game}
        dispatch={dispatch}
        onDelete={onGameDelete}
        options={user.options}
        onReload={reload} />}
      {user.groups.admin === true && <TrackListing game={game} />}
    </div>
  );
}
