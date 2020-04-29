import React from 'react';
import { ConnectedRouter } from 'connected-react-router';
import { Switch, Route } from 'react-router-dom';

import { NavPanel } from '../components/NavPanel';
import routes from '../routes';
import { IndexPage, TrackListingPage } from '../games/components';
import { ChooseTicketsPage, PlayGamePage, ManageGamePage } from '../tickets/components';
import { LoginPage, LogoutPage, PasswordResetPage } from '../user/components';
import { RegisterPage } from '../user/components/RegisterPage';
import { history } from './store';

import '../styles/main.scss';

function App() {
  return (
    <ConnectedRouter history={history}>
      <NavPanel />
      <div className="container">
        <Switch>
          <Route exact path={routes.login} component={LoginPage} />
          <Route exact path={routes.logout} component={LogoutPage} />
          <Route exact path={routes.register} component={RegisterPage} />
          <Route exact path={routes.passwordReset} component={PasswordResetPage} />
          <Route exact path={routes.game} component={ChooseTicketsPage} />
          <Route exact path={routes.trackListing} component={TrackListingPage} />
          <Route exact path={routes.manage} component={ManageGamePage} />
          <Route exact path={routes.play} component={PlayGamePage} />
          <Route path={routes.index} component={IndexPage} />
        </Switch>
      </div>
    </ConnectedRouter>
  );
}

export default App;
