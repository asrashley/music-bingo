import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { GameAdminActions } from './GameAdminActions';
import { PastGamesCalendar } from './PastGamesCalendar';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';

import { getPastGamesCalendar } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

export function PastGamesCalendarPage() {
    const dispatch = useDispatch();
    const user = useSelector(getUser);
    const pastGamesCalendar = useSelector(getPastGamesCalendar);

    useEffect(() => {
        dispatch(fetchUserIfNeeded());
    }, [dispatch]);

    useEffect(() => {
        if (user.loggedIn) {
            dispatch(fetchGamesIfNeeded());
        }
    }, [dispatch, user]);

    const { themes, months } = pastGamesCalendar;

    return (
        <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
            <GameAdminActions />
            <PastGamesCalendar themes={themes} months={months} />
        </div>
    );
}
