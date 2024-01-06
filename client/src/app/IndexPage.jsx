import React, { useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { fetchUserIfNeeded } from '../user/userSlice';
import { fetchGamesIfNeeded, gameInitialFields } from '../games/gamesSlice';
import { ticketInitialState } from '../tickets/ticketsSlice';

import { getActiveGamesList, getPastGamesOrder } from '../games/gamesSelectors';
import { getUser } from '../user/userSelectors';

import { UserPropType } from '../user/types/User';
import { GamePropType } from '../games/types/Game';

import { Welcome } from './Welcome';

import { routes } from '../routes/routes';

function Description({ children }) {
  return (
    <div className="description">
      {children}
    </div>
  );
}
Description.propTypes = {
  children: PropTypes.node
};

function IndexActions({ games, pastOrder, user }) {
  if (!user.loggedIn) {
    return (<>
      <Description>
        You need a registered account to play Musical Bingo. It is free and we won&apos;t pass on
        your details to anyone else.
      </Description>
      <div className="action-buttons">
        <Link to={reverse(`${routes.login}`)} className="btn btn-lg btn-success login-button">log in</Link> &nbsp;
        <Link to={reverse(`${routes.register}`)} className="btn btn-lg btn-primary register-button">create an account</Link>
      </div>
    </>)
  }
  let text = 'If you are feeling nostalgic, why not browse the ';
  if (games.length === 0) {
    text = 'There are no upcoming Bingo games, but in the meantime you could browse the ';
  }
  return (<>
    {(games.length > 0) && <Description>
      You can <Link to={reverse(`${routes.listGames}`)}>choose tickets</Link>&nbsp;
      for the upcoming Bingo games
    </Description>
    }
    {(pastOrder.length > 0) && <Description>
      {text}<Link to={reverse(`${routes.pastGamesPopularity}`)}> previous Bingo games</Link>.
    </Description>
    }
  </>);
}

IndexActions.propTypes = {
  user: UserPropType.isRequired,
  games: PropTypes.arrayOf(GamePropType),
  pastOrder: PropTypes.arrayOf(PropTypes.number).isRequired,
};

export function IndexPage() {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const games = useSelector(getActiveGamesList);
  const pastOrder = useSelector(getPastGamesOrder);

  const game = useMemo(() => {
    const now = new Date();
    return {
      ...gameInitialFields,
      pk: now.getFullYear(),
      id: `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`,
      options: {
        ...gameInitialFields.options,
        rows: 3,
        columns: 5,
      }
    };
  }, []);

  const ticket = useMemo(() => {
    const now = new Date();
    const tk = {
      ...ticketInitialState(),
      pk: now.getFullYear(),
      game: game.pk,
      number: 1 + now.getHours(),
      tracks: [],
      rows: [],
    };
    for (let i = 0; i < game.options.rows; ++i) {
      const cols = [];
      for (let j = 0; j < game.options.columns; ++j) {
        cols.push({ title: '', artist: '' });
      }
      tk.rows.push(cols);
    }
    return tk;
  }, [game]);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.pk >= 0) {
      dispatch(fetchGamesIfNeeded());
    }
  }, [dispatch, user.pk]);

  return (
    <Welcome className="index-page" game={game} ticket={ticket}>
      <IndexActions games={games} pastOrder={pastOrder} user={user} />
    </Welcome>
  );
}
