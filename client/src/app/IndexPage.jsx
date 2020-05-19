import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { BingoTicket } from '../tickets/components';

import { fetchUserIfNeeded } from '../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames, gameInitialFields } from '../games/gamesSlice';
import { ticketInitialState } from '../tickets/ticketsSlice';

import { getActiveGamesList, getPastGamesOrder } from '../games/gamesSelectors';
import { getUser } from '../user/userSelectors';

import { initialState } from './initialState';
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
      id: `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`,
      options: {
        rows: 3,
        columns: 5,
      }
    };
    const ticket = {
      ...ticketInitialState,
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
      <div id="index-page">
        <BingoTicket className="index-ticket view-ticket" game={game} ticket={ticket} />
        <div className="welcome">
          <h2 className="strapline">Like normal Bingo, but with music!</h2>
          <p className="description">Musical Bingo is a variation on the normal game of bingo, where the numbers are replaced
          with songs that the players must listen out for.</p>
          <p className="description">If you know your Bruce Springsteen from your Beyonce, your Whitney Houston from
            your Wu-Tang Clan, why not join use for a game or two?</p>
          {actions.map((act, idx) => <p className="description" key={idx}>{act}</p>)}
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
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
