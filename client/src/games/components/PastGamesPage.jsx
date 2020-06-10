import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { BingoGamesTable } from './BingoGamesTable';
import { PopularityGraph } from './PopularityGraph';

import { fetchUserIfNeeded } from '../../user/userSlice';
import {
  fetchGamesIfNeeded, invalidateGames, setPopularityOptions,
} from '../gamesSlice';

import { getLocation } from '../../routes/selectors';
import {
  getPastGamesList, getPastGamesPopularity, getPopularityOptions,
} from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { initialState } from '../../app/initialState';


import '../styles/games.scss';

class PastGamesPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: PropTypes.object.isRequired,
    pastGames: PropTypes.array,
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
  }

  toggleOrientation = () => {
    const { dispatch, popularityOptions } = this.props;
    const { vertical } = popularityOptions;
    dispatch(setPopularityOptions({vertical: !vertical}));
  }

  render() {
    const { pastGames, popularity, popularityOptions, user } = this.props;
    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <PopularityGraph popularity={popularity} options={popularityOptions}
                         toggleOrientation={this.toggleOrientation} />
        <BingoGamesTable games={pastGames} onReload={this.onReload} past title="Previous Bingo games" />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    location: getLocation(state, ownProps),
    user: getUser(state, ownProps),
    pastGames: getPastGamesList(state, ownProps),
    popularity: getPastGamesPopularity(state, ownProps),
    popularityOptions: getPopularityOptions(state, ownProps),
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
