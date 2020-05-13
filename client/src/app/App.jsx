import React from 'react';
import { ConnectedRouter } from 'connected-react-router';
import { Switch, Route } from 'react-router-dom';

import { NavPanel } from '../components/NavPanel';
import routes from '../routes';
import { IndexPage, PastGamesPage,TrackListingPage } from '../games/components';
import { ChooseTicketsPage, PlayGamePage, ViewTicketPage} from '../tickets/components';
import { LoginPage, LogoutPage, PasswordResetPage, PasswordResetConfirmPage } from '../user/components';
import { UsersListPage } from '../admin/components';
import { RegisterPage } from '../user/components/RegisterPage';
import { MessagePanel } from '../messages/components';
import { history } from './store';

import '../styles/main.scss';

function App() {
  return (
    <ConnectedRouter history={history}>
      <NavPanel />
      <div className="container">
        <MessagePanel />
        <Switch>
          <Route exact path={routes.login} component={LoginPage} />
          <Route exact path={routes.logout} component={LogoutPage} />
          <Route exact path={routes.register} component={RegisterPage} />
          <Route exact path={routes.passwordResetConfirm} component={PasswordResetConfirmPage} />
          <Route exact path={routes.passwordReset} component={PasswordResetPage} />
          <Route exact path={routes.listUsers} component={UsersListPage} />
          <Route exact path={routes.game} component={ChooseTicketsPage} />
          <Route exact path={routes.play} component={PlayGamePage} />
          <Route exact path={routes.viewTicket} component={ViewTicketPage} />
          <Route exact path={routes.pastGames} component={PastGamesPage} />
          <Route exact path={routes.trackListing} component={TrackListingPage} />
          <Route exact path={routes.index} component={IndexPage} />
        </Switch>
      </div>
    </ConnectedRouter>
  );
}

export default App;
