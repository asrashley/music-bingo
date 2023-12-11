import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { PopularityGraph } from './PopularityGraph';
import { AdminActions } from '../../admin/components/AdminActions';
import { PastGamesButtons } from './PastGamesButtons';

import { fetchUserIfNeeded } from '../../user/userSlice';
import {
    fetchGamesIfNeeded, invalidateGames, setPopularityOptions,
} from '../gamesSlice';

import {
    getPastGamesPopularity, getPopularityOptions,
} from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { ThemePropType } from '../types/Theme';
import { UserPropType } from '../../user/types/User';
import { PopularityOptionsPropType } from '../types/Popularity';

import '../styles/games.scss';

class PastGamesIndexPageComponent extends React.Component {
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        user: UserPropType.isRequired,
        popularityOptions: PopularityOptionsPropType.isRequired,
        popularity: PropTypes.arrayOf(ThemePropType).isRequired,
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

    toggleOrientation = () => {
        const { dispatch, popularityOptions } = this.props;
        const { vertical } = popularityOptions;
        dispatch(setPopularityOptions({ vertical: !vertical }));
    };

    render() {
        const { popularity, popularityOptions, user } = this.props;

        return (
            <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
                <AdminActions alwaysShowChildren={true}>
                    <button className="btn btn-primary"
                        onClick={this.onReload}>Reload</button>
                </AdminActions>
                <PastGamesButtons page="popularity" />
                <PopularityGraph popularity={popularity} options={popularityOptions}
                    toggleOrientation={this.toggleOrientation} />
            </div>
        );
    }
}

const mapStateToProps = (state, ownProps) => {
    return {
        user: getUser(state, ownProps),
        popularity: getPastGamesPopularity(state, ownProps),
        popularityOptions: getPopularityOptions(state, ownProps),
    };
};

export const PastGamesPopularityPage = connect(mapStateToProps)(PastGamesIndexPageComponent);

