import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn, setActiveGame } from '../../user/userSlice';
import { fetchTicketsIfNeeded, ticketsInitialState } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';

import '../styles/tickets.scss';

class ManageGamePage extends React.Component {
  static propTypes = {
    game: PropTypes.object.isRequired,
    tickets: PropTypes.object.isRequired,
    selected: PropTypes.number.isRequired,
    loggedIn: PropTypes.bool,
  };

  constructor(props) {
    super(props);
    this.state = {
      ActiveDialog: null,
      dialogData: null,
    };
  }

  componentDidMount() {
    const { dispatch, gamePk } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()))
      .then(() => dispatch(fetchTicketsIfNeeded(gamePk)))
      .then(() => dispatch(setActiveGame(gamePk)));
  }

  render() {
    const { game, loggedIn } = this.props;
    const { ActiveDialog, dialogData } = this.state;
    return (
      <div className="ticket-chooser ticket-manager">
        <h1>The theme of this round is "{game.title}"</h1>
        {loggedIn || < LoginDialog dispatch={this.props.dispatch} onSuccess={() => null} />}
        {ActiveDialog && <ActiveDialog {...dialogData} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  //console.dir(ownProps);
  const { user } = state;
  const { gamePk } = ownProps.match.params;
  let game = state.games.games[gamePk];
  if (game === undefined) {
    game = {
      title: '',
      pk: -1,
      placeholder: true,
    };
  }
  let tickets;
  if (state.tickets.games[gamePk]) {
    tickets = state.tickets.games[gamePk];
  } else {
    tickets = ticketsInitialState();
  }
  let selected = 0;
  Object.keys(tickets.tickets).forEach(pk => {
    /*if (pk === null) {
        return;
    }
    console.log(`pk ${pk}`);
    order.push(pk);*/
    if (tickets.tickets[pk].user === user.pk) {
      selected++;
    }
  });
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    game,
    gamePk,
    tickets,
    selected,
  };
};

ManageGamePage = connect(mapStateToProps)(ManageGamePage);

export {
  ManageGamePage
};
