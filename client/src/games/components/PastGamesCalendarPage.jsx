import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { PastGamesCalendar, PastGamesCalendarPropType } from './PastGamesCalendar';
import { PastGamesButtons } from './PastGamesButtons';

import { fetchUserIfNeeded } from '../../user/userSlice';
import {
    fetchGamesIfNeeded, invalidateGames,
} from '../gamesSlice';

import { getPastGamesCalendar } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { UserPropType } from '../../user/types/User';

class PastGamesCalendarPageComponent extends React.Component {
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        user: UserPropType.isRequired,
        pastGamesCalendar: PastGamesCalendarPropType.isRequired,
    };

    componentDidMount() {
        const { dispatch } = this.props;
        dispatch(fetchUserIfNeeded());
        dispatch(fetchGamesIfNeeded());
    }

    componentDidUpdate(prevProps, prevState) {
        const { user, dispatch } = this.props;
        if (user.pk > 0 && user.pk !== prevProps.user.pk) {
            dispatch(fetchGamesIfNeeded());
        }
    }

    onReload = () => {
        const { dispatch } = this.props;
        dispatch(invalidateGames());
        dispatch(fetchGamesIfNeeded());
    };

    render() {
        const { user } = this.props;
        const { themes, months } = this.props.pastGamesCalendar;

        return (
            <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
                <PastGamesButtons page="calendar" />
                <PastGamesCalendar themes={themes} months={months} />
            </div>
        );
    }
}

const mapStateToProps = (state, ownProps) => {
    return {
        user: getUser(state, ownProps),
        pastGamesCalendar: getPastGamesCalendar(state, ownProps),
    };
};

export const PastGamesCalendarPage = connect(mapStateToProps)(PastGamesCalendarPageComponent);
