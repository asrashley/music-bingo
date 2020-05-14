import React from 'react';
import { ConnectedRouter } from 'connected-react-router';
import { Switch, Route } from 'react-router-dom';

import { NavPanel } from '../components/NavPanel';
import routes from '../routes';
import { IndexPage, PastGamesPage, TrackListingPage } from '../games/components';
import { ChooseTicketsPage, PlayGamePage, ViewTicketPage } from '../tickets/components';
import { LoginPage, LogoutPage, PasswordResetPage, PasswordResetConfirmPage } from '../user/components';
import { UsersListPage } from '../admin/components';
import { RegisterPage } from '../user/components/RegisterPage';
import { MessagePanel } from '../messages/components';
import { history } from './store';

import '../styles/main.scss';

const routeComponents = [
  { path: routes.login, component: LoginPage, exact:true },
  { path: routes.logout, component: LogoutPage, exact: true },
  { path: routes.register, component: RegisterPage, exact: true },
  { path: routes.passwordResetConfirm, component: PasswordResetConfirmPage, exact: true },
  { path: routes.passwordReset, component: PasswordResetPage, exact: true },
  { path: routes.listUsers, component: UsersListPage, exact: true },
  { path: routes.game, component: ChooseTicketsPage, exact: true },
  { path: routes.play, component: PlayGamePage, exact: true },
  { path: routes.viewTicket, component: ViewTicketPage, exact: true },
  { path: routes.pastGames, component: PastGamesPage, exact: true },
  { path: routes.trackListing, component: TrackListingPage, exact: true },
  { path: routes.index, component: IndexPage, exact: false },
];

function App() {
  return (
    <ConnectedRouter history={history}>
      <Switch>
        {routeComponents.map((route, index) => (
          <Route exact={route.exact} path={route.path} key={index} component={NavPanel} />
        ))}
      </Switch>
        <div className="container">
          <MessagePanel />
      <Switch>
          {routeComponents.map((route, index) => (
            <Route exact={route.exact} path={route.path} key={index} component={route.component} />
          ))}
      </Switch>
        </div>
    </ConnectedRouter>
  );
}

export default App;
