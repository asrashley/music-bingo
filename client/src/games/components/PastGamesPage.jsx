import React, { useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { BingoGamesTable } from './BingoGamesTable';
import { AdminActions } from '../../admin/components/AdminActions';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { getPastGamesList, getThemeSlug } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import '../styles/games.scss';

export function PastGamesPage() {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const pastGames = useSelector(getPastGamesList);
  const slug = useSelector(getThemeSlug);

  const title = useMemo(() => {
    if (slug) {
      if (pastGames.length) {
        return `Previous "${pastGames[0].title}" Bingo games`;
      } else {
        return `Previous "${slug}" Bingo games`;
      }
    }
    return 'Previous Bingo games';
  }, [pastGames, slug]);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.pk > 0) {
      dispatch(fetchGamesIfNeeded());
    }
  }, [dispatch, user.pk]);

  const onReload = () => {
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  };

  return (
    <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}>
      <AdminActions alwaysShowChildren={true}>
        <button className="btn btn-primary"
          onClick={onReload}>Reload</button>
      </AdminActions>
      {user.groups?.guests === true && <div className="alert alert-info" role="alert">
        If you would like to see the track listing of every game, log out from this
        guest account and register an account.</div>}
      <BingoGamesTable games={pastGames} onReload={onReload} user={user} past
        title={title} slug={slug} />
    </div>
  );
}
