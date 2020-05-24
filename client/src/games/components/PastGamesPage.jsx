import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { BingoGamesTable } from './BingoGamesTable';
import { initialState } from '../../app/initialState';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { getLocation } from '../../routes/selectors';
import { getPastGamesList, getPastGamesPopularity } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import '../styles/games.scss';

const colours = [
  '#FF0000',
  '#008000',
  '#00EFEF',
  '#808000',
  '#BFBF00',
  '#808080',
  '#008080',
  '#00EF00',
  '#C0C0C0',
  '#800000',
  '#0000FF',
  '#000080',
  '#FF00FF',
  '#800080',
];

function ThemeRow({index, theme}) {
  const style = {
    width: `${100 * theme.count / theme.maxCount}%`,
    backgroundColor: colours[index % colours.length],
  };
  return (
    <tr className="theme">
      <td className="title" style={{color: colours[index % colours.length]}}>{theme.title}</td>
      <td className="count"><div className="bar" style={style}>{theme.count}</div> </td>
    </tr>
  );
}

function PopularityGraph({popularity}) {
  return (
    <table className="popularity-graph">
      <thead><tr><th className="title">Theme</th><th className="count">Popularity</th></tr></thead>
      <tbody>
        {popularity.map((theme, idx) => <ThemeRow key={idx} index={idx} theme={theme} />)}
      </tbody>
    </table>
  );
}

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

  render() {
    const { pastGames, popularity, user } = this.props;
    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <PopularityGraph popularity={popularity} />
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
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
