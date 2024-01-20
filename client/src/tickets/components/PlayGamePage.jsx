import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';

/* components */
import { BingoTicket } from './BingoTicket';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchTicketsIfNeeded, fetchTicketDetailIfNeeded, setChecked } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';

/* selectors */
import { getMyGameTickets } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';


function PlayGamePageComponent({ route }) {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const game = useSelector((state) => getGame(state, route));
  const tickets = useSelector(getMyGameTickets);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchGamesIfNeeded());
  }, [dispatch, user.pk, user.loggedIn]);

  useEffect(() => {
    if (game.pk > 0) {
      dispatch(fetchTicketsIfNeeded(game.pk));
    }
  }, [dispatch, game.pk]);

  useEffect(() => {
    if (game.pk > 0 && tickets.length) {
      tickets.forEach(ticket => dispatch(fetchTicketDetailIfNeeded(game.pk, ticket.pk)));
    }
  }, [dispatch, game.pk, tickets]);

  const onSetChecked = (values) => {
    dispatch(setChecked(values));
  };

  return (
    <div className="card-list">
      {tickets.length === 0 && <h2 className="warning">You need to choose a ticket to be able to play!</h2>}
      {tickets.map((ticket) => <BingoTicket key={ticket.pk} ticket={ticket} game={game}
        setChecked={onSetChecked} dispatch={dispatch} download />)}
    </div>
  );
}

PlayGamePageComponent.propTypes = {
  route: PropTypes.object
};

export function PlayGamePage() {
  const routeParams = useParams();
  const route = { routeParams };
  return <PlayGamePageComponent route={route} />;
}
