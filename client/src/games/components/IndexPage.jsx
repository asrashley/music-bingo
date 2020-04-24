import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';
import routes from '../../routes';
import { LoginDialog } from '../../user/components/LoginDialog';

import '../styles/games.scss';

const utcFields = ['getUTCHours', 'getUTCMinutes',
  'getUTCSeconds', 'getUTCDate',
  'getUTCMonth', 'getUTCFullYear'];

const localFields = utcFields.map(f => f.replace('UTC', ''));


const DateTime = ({ date, useUTC=false, withTimezone=false, withDate=true, withTime=true, ...params }) => {
  if (typeof (date) === "string") {
    date = new Date(date);
  };
  let fields = (useUTC === false) ? localFields : utcFields;
  fields = fields.map((f) => {
    const val = date[f]();
    if (/Year/.test(f)) {
      return `${val}`;
    }
    if (/Month/.test(f)) {
      return `0${val + 1}`.slice(-2);
    }
    return `0${val}`.slice(-2);
  });
  let tz = '';
  if (withTimezone === true) {
    if (useUTC === false) {
      const offset = date.getTimezoneOffset();
      if (offset === 0) {
        tz = ' GMT';
      } else {
        tz = ' BST';
      }
    } else {
      tz = ' UTC';
    }
  }
  const time = withTime ? `${fields[0]}:${fields[1]}:${fields[2]}` : '';
  const dstr = withDate ? `${fields[3]}/${fields[4]}/${fields[5]}` : '';
  if (!withTime) {
    tz = '';
  }
  return `${time} ${dstr} ${tz}`;
};

const TableRow = ({ game }) => {
  let url, linkText;

  if (game.userCount === 0) {
    linkText = "Choose tickets";
    url = reverse(`${routes.game}`, { gamePk: game.pk });
  } else {
    url = reverse(`${routes.play}`, { gamePk: game.pk });
    linkText = `You have chosen ${game.userCount} ticket${(game.userCount > 1) ? 's' : ''}`;
  }
  return (
    <tr>
      <td className="round-column">{game.gameRound}</td>
      <td className="date-column">
        <DateTime date={game.start} withTime={false} />
      </td>
      <td className="theme-column">
        <Link to={reverse(`${routes.game}`, { gamePk: game.pk })}>{game.title}</Link>
      </td>
      <td className="ticket-column">
        <Link to={url}>{linkText}</Link>
      </td>
    </tr>
  );
};

class IndexPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    loggedIn: PropTypes.bool.isRequired,
    user: PropTypes.object,
    games: PropTypes.array,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
  }

  componentWillReceiveProps(nextProps) {
    const { user, dispatch } = nextProps;
    if (user.pk !== this.props.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  render() {
    const { games, user, loggedIn } = this.props;
    return (
      <div id="games-page">
        {user && <h2 className="greeting">Hello {user.username}</h2>}
        <table className="table table-striped table-bordered game-list">
          <thead>
            <tr>
              <th colSpan="4" className="available-games">Available Bingo games</th>
            </tr>
            <tr>
              <th className="round-column">Round</th>
              <th className="date-column">Date</th>
              <th className="theme-column">Theme</th>
              <th className="ticket-column">Your Tickets</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game, idx) => (<TableRow game={game} key={idx} />))}
          </tbody>
        </table>
        {!loggedIn && <LoginDialog dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

//IndexPage.whyDidYouRender = true;

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user } = state;
  const { games, order } = state.games;
  const { location } = ownProps;
  const gameList = [];
  order.forEach(pk => gameList.push(games[pk]));
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    location,
    games: gameList,
  };
};

IndexPage = connect(mapStateToProps)(IndexPage);

export {
  IndexPage
};
