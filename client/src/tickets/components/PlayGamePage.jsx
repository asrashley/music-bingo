import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoTicket } from '../../cards/components';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchTicketsIfNeeded } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';

/* selectors */
import { getMyGameTickets } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';

/* data */
import { initialState } from '../../app/initialState';

class PlayGamePage extends React.Component {
  static propTypes = {
    tickets: PropTypes.array.isRequired,
    game: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
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
    const { game, tickets, user } = this.props;
    return (
      <div className="card-list">
        {tickets.length===0 && <h2 className="warning">You need to choose a ticket to be able to play!</h2>}
        {tickets.map((ticket, idx) => <BingoTicket key={idx} ticket={ticket} game={game} user={user} />)}
        {!user.loggedIn && <LoginDialog dispatch={this.props.dispatch} user={user} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
    game: getGame(state, props),
    tickets: getMyGameTickets(state, props),
  };
};

PlayGamePage = connect(mapStateToProps)(PlayGamePage);

export {
  PlayGamePage
};
