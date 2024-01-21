import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import PropTypes from 'prop-types';

import { GameAdminActions } from './GameAdminActions';
import { PastGamesCalendar } from './PastGamesCalendar';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';

import { getPastGamesCalendar } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';
import { useParams } from 'react-router-dom';
import { UserPropType } from '../../user/types/User';

export function PastGamesCalendarPage() {
    const user = useSelector(getUser);
    const params = useParams();
    const gamesSelector = (state) => getPastGamesCalendar(state, params);

    return <PastGamesCalendarPageComponent gamesSelector={gamesSelector} user={user} />;
}

function PastGamesCalendarPageComponent({ user, gamesSelector }) {
    const dispatch = useDispatch();
    const pastGamesCalendar = useSelector(gamesSelector);

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

PastGamesCalendarPageComponent.propTypes = {
    gamesSelector: PropTypes.func.isRequired,
    user: UserPropType.isRequired,
};
