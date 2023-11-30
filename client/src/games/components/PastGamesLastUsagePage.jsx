import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { PastGamesLastUsage } from './PastGamesLastUsage';
import { AdminActions } from '../../admin/components/AdminActions';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { getPastGamesCalendar, isFetchingGames } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { UserPropType } from '../../user/types/User';

class PastGamesLastUsagePageComponent extends React.Component {
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        user: UserPropType.isRequired,
        loading: PropTypes.bool.isRequired,
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
        const { pastGamesCalendar, user, loading } = this.props;
        const { themes } = pastGamesCalendar;

        return (
            <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
                <AdminActions />
                <PastGamesLastUsage themes={themes} loading={loading} />
            </div>
        );
    }
}

const mapStateToProps = (state, ownProps) => {
    return {
        loading: isFetchingGames(state, ownProps),
        pastGamesCalendar: getPastGamesCalendar(state, ownProps),
        user: getUser(state, ownProps),
    };
};

export const PastGamesLastUsagePage = connect(mapStateToProps)(PastGamesLastUsagePageComponent);

