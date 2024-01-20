import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { GameAdminActions } from './GameAdminActions';
import { PastGamesLastUsage } from './PastGamesLastUsage';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';

import { getPastGamesCalendar, isFetchingGames } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

export function PastGamesLastUsagePage() {
    const dispatch = useDispatch();
    const loading = useSelector(isFetchingGames);
    const pastGamesCalendar = useSelector(getPastGamesCalendar);
    const user = useSelector(getUser);
    const { themes } = pastGamesCalendar;

    useEffect(() => {
        dispatch(fetchUserIfNeeded());
    }, [dispatch]);

    useEffect(() => {
        if (user.pk > 0) {
            dispatch(fetchGamesIfNeeded());
        }
    }, [dispatch, user.pk]);

    return (
        <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
            <GameAdminActions />
            <PastGamesLastUsage themes={themes} loading={loading} />
        </div>
    );
}
