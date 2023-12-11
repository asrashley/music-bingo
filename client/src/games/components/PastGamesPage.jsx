import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { BingoGamesTable } from './BingoGamesTable';
import { AdminActions } from '../../admin/components/AdminActions';
import { PastGamesButtons } from './PastGamesButtons';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { getPastGamesList, getThemeSlug } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { UserPropType } from '../../user/types/User';
import { GamePropType } from '../../games/types/Game';

import '../styles/games.scss';

class PastGamesPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: UserPropType.isRequired,
    pastGames: PropTypes.arrayOf(GamePropType).isRequired,
    slug: PropTypes.string,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
  }

  componentDidUpdate(prevProps) {
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
    const { pastGames, user, slug } = this.props;
    let title = 'Previous Bingo games';
    if (slug) {
      if (pastGames.length) {
        title = `Previous "${pastGames[0].title}" Bingo games`;
      } else {
        title = `Previous "${slug}" Bingo games`;
      }
    }

    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}>
        <AdminActions alwaysShowChildren={true}>
          <button className="btn btn-primary"
            onClick={this.onReload}>Reload</button>
        </AdminActions>
        <PastGamesButtons page="all" />
        {user.groups?.guests === true && <div className="alert alert-info" role="alert">
          If you would like to see the track listing of every game, log out from this
          guest account and register an account.</div>}
        <BingoGamesTable games={pastGames} onReload={this.onReload} user={user} past
          title={title} slug={slug} />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    user: getUser(state, ownProps),
    pastGames: getPastGamesList(state, ownProps),
    slug: getThemeSlug(state, ownProps),
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
