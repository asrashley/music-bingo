import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchTicketsIfNeeded } from '../ticketsSlice';
import { getTicket } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoTicket } from './BingoTicket';

class ViewTicketPage extends React.Component {
  static propTypes = {
    ticket: PropTypes.object.isRequired,
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
    const { game, ticket, user, loggedIn } = this.props;
    return (
      <div className="card-list">
        <BingoTicket ticket={ticket} game={game} user={user} />
        {!loggedIn && <LoginDialog dispatch={this.props.dispatch} user={user} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  const { user } = state;

  return {
    loggedIn: userIsLoggedIn(state),
    user,
    game: getGame(state, props),
    ticket: getTicket(state, props),
  };
};

ViewTicketPage = connect(mapStateToProps)(ViewTicketPage);

export {
  ViewTicketPage
};
