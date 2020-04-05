import React from 'react';
import PropTypes from 'prop-types';
import { ConnectedRouter } from 'connected-react-router';
import { Redirect, Switch, Route } from 'react-router-dom';
import { reverse } from 'named-urls';
import { connect } from 'react-redux';

import { NavPanel } from './components/NavPanel';
import routes from './routes';
import { IndexPage } from './games/components';
import { ChooseTicketsPage, PlayGamePage, ManageGamePage } from './tickets/components';
import { LoginPage, LogoutPage } from './user/components';
import { RegisterPage } from './user/components/RegisterPage';
import { initialState } from './app/initialState';
import { history } from './app/store';

import './styles/main.scss';

function ProtectedRouteFn({ children, ...rest }) {
  return (
    <Route
      {...rest}
      render={(props) => {
        console.log('********** protected route');
        const { location } = props;
        console.dir(props);
        if (false) {
          return children;
        }
        return (
          <Redirect
            to={{
              pathname: reverse('login'),
              state: { from: location }
            }}
          />
        );

      }}
    />
  );
}

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user } = state;
  return {
    user,
  };
};

const ProtectedRoute = connect(mapStateToProps)(ProtectedRouteFn);


function App() {
  return (
    <ConnectedRouter history={history}>
      <NavPanel />
      <Switch>
        <Route exact path={routes.login} component={LoginPage} />
        <Route exact path={routes.logout} component={LogoutPage} />
        <Route exact path={routes.register} component={RegisterPage} />
        <Route exact path={routes.game} component={ChooseTicketsPage} />
        <Route exact path={routes.manage} component={ManageGamePage} />
        <Route exact path={routes.play} component={PlayGamePage} />
        <Route path={routes.index} component={IndexPage} />
      </Switch>
    </ConnectedRouter>
  );
}

export default App;
