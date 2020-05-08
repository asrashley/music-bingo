import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchTicketsIfNeeded} from '../ticketsSlice';
import { makeGetMyTickets } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoTicket } from './BingoTicket';

class PlayGamePage extends React.Component {
  static propTypes = {
    tickets: PropTypes.array.isRequired,
    game: PropTypes.object.isRequired,
    loggedIn: PropTypes.bool,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded())
  }

  componentWillReceiveProps(nextProps) {
    const { dispatch, user, game } = nextProps;
    if (user.pk !== this.props.user.pk) {
      dispatch(fetchGamesIfNeeded());
    } else if (game.pk > 0 && game.pk !== this.props.game.pk) {
      dispatch(fetchTicketsIfNeeded(game.pk));
    }
  }

  render() {
    const { game, tickets, user, loggedIn } = this.props;
    return (
      <div className="card-list">
        {tickets.length===0 && <h2 className="warning">You need to choose a ticket to be able to play!</h2>}
        {tickets.map((ticket, idx) => <BingoTicket key={idx} ticket={ticket} game={game} user={user} />)}
        {!loggedIn && <LoginDialog dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  const getMyTickets = makeGetMyTickets();
  const { user } = state;

  return {
    loggedIn: userIsLoggedIn(state),
    user,
    game: getGame(state, props),
    tickets: getMyTickets(state, props),
  };
};

PlayGamePage = connect(mapStateToProps)(PlayGamePage);

export {
  PlayGamePage
};
