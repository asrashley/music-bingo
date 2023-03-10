import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { fetchUserIfNeeded } from '../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames, gameInitialFields } from '../games/gamesSlice';
import { ticketInitialState } from '../tickets/ticketsSlice';

import { getActiveGamesList, getPastGamesOrder } from '../games/gamesSelectors';
import { getUser } from '../user/userSelectors';

import { Welcome } from './Welcome';

import routes from '../routes';

/* import '../styles/games.scss'; */

class IndexPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: PropTypes.object.isRequired,
    games: PropTypes.array,
    pastGames: PropTypes.array,
  };

  constructor(props) {
    super(props);
    const now = new Date();
    const game = {
      ...gameInitialFields,
      pk: now.getFullYear(),
      id: `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`,
      options: {
        ...gameInitialFields.options,
        rows: 3,
        columns: 5,
      }
    };
    const ticket = {
      ...ticketInitialState(),
      pk: now.getFullYear(),
      game: game.pk,
      number: 1 + now.getHours(),
      tracks: [],
      rows: [],
    };
    for (let i = 0; i < game.options.rows; ++i) {
      const cols = [];
      for (let j = 0; j < game.options.columns; ++j) {
        cols.push({ title: '', artist: '' });
      }
      ticket.rows.push(cols);
    }
    this.state = { game, ticket };
  }

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()));
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  onReload = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  };

  render() {
    const { games, user, pastOrder } = this.props;
    const { game, ticket } = this.state;
    let text = 'If you are feeling nostalgic, why not browse the ';
    if (games.length === 0) {
      text = 'There are no upcoming Bingo games, but in the meantime you could browse the ';
    }
    const actions = [];
    if (!user.loggedIn) {
      actions.push("You need a registered account to play Musical Bingo. It is free and we won't pass on your details to anyone else.");
      actions.push(<div className="action-buttons">
        <Link to={reverse(`${routes.login}`)} className="btn btn-lg btn-success login-button">log in</Link> &nbsp;
        <Link to={reverse(`${routes.register}`)} className="btn btn-lg btn-primary register-button">create an account</Link>
      </div>);
    } else {
      if (games.length > 0) {
        actions.push(<React.Fragment>You can <Link to={reverse(`${routes.listGames}`)}>choose tickets</Link>&nbsp;
          for the upcoming Bingo games</React.Fragment>);
      }
      if (pastOrder.length > 0) {
        actions.push(<React.Fragment>{text}<Link to={reverse(`${routes.pastGames}`)}>
          previous Bingo games</Link>.</React.Fragment>);
      }
    }
    return (
      <Welcome className="index-page" game={game} ticket={ticket}>
        {actions.map((act, idx) => <div className="description" key={idx}>{act}</div>)}
      </Welcome>
    );
  }
}

const mapStateToProps = (state, props) => {
  return {
    user: getUser(state, props),
    games: getActiveGamesList(state),
    pastOrder: getPastGamesOrder(state),
  };
};

IndexPage = connect(mapStateToProps)(IndexPage);

export {
  IndexPage
};
