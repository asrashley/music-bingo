import React, { useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { AdminActions } from '../../admin/components/AdminActions';
import { BingoGamesTable } from './BingoGamesTable';

import { getUser } from '../../user/userSelectors';
import { getActiveGamesList, getPastGamesOrder } from '../gamesSelectors';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { routes } from '../../routes/routes';

import '../styles/games.scss';

export function ListGamesPage() {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const games = useSelector(getActiveGamesList);
  const pastOrder = useSelector(getPastGamesOrder);

  const text = useMemo(() => {
    if (games.length === 0) {
      return 'There are no upcoming Bingo games, but in the meantime you could browse the';
    }
    return 'If you are feeling nostalgic, why not browse the ';
  }, [games]);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.pk >= 0) {
      dispatch(fetchGamesIfNeeded());
    }
  }, [dispatch, user.pk]);

  const onReload = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  };

  return (
    <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
      <AdminActions />
      <BingoGamesTable
        games={games}
        onReload={onReload}
        user={user}
        title="Available Bingo games"
      />
      {pastOrder.length > 0 && <p>{text}
        <Link to={reverse(`${routes.pastGamesPopularity}`)} > history of previous Bingo rounds</Link></p>}
    </div>
  );
}
