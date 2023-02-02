import React from 'react';
import { ConnectedRouter } from 'connected-react-router';
import { Link, Switch, Route } from 'react-router-dom';
import { reverse } from 'named-urls';

import { NavPanel } from '../components/NavPanel';
import routes from '../routes';
import { IndexPage } from './IndexPage';
import { DirectoryListPage } from '../directories/components';
import { ListGamesPage, PastGamesPage, TrackListingPage } from '../games/components';
import { ChooseTicketsPage, PlayGamePage, ViewTicketPage } from '../tickets/components';
import {
  LoginPage, LogoutPage, PasswordResetPage, PasswordResetConfirmPage,
  LoginRequired, UserPage, ChangeUserPage, RegisterPage, GuestAccessPage,
} from '../user/components';
import { GuestLinksPage, UsersListPage } from '../admin/components';
import { MessagePanel } from '../messages/components';
import { PrivacyPolicyPage } from './PrivacyPolicyPage';
import { SettingsIndexPage, SettingsSectionPage } from '../settings/components';
import { history } from '../store/history';

import '../styles/main.scss';

const routeComponents = [
  { path: routes.login, component: LoginPage, exact: true },
  { path: routes.logout, component: LogoutPage, exact: true },
  { path: routes.user, component: UserPage, exact: true, protected: true },
  { path: routes.changeUser, component: ChangeUserPage, exact: true, protected: true },
  { path: routes.register, component: RegisterPage, exact: true },
  { path: routes.passwordResetConfirm, component: PasswordResetConfirmPage, exact: true },
  { path: routes.passwordReset, component: PasswordResetPage, exact: true },
  { path: routes.guestAccess, component: GuestAccessPage, exact: true },
  { path: routes.guestLinks, component: GuestLinksPage, exact: true, protected: true },
  { path: routes.listDirectory, component: DirectoryListPage, exact: true, protected: true },
  { path: routes.listDirectories, component: DirectoryListPage, exact: true, protected: true },
  { path: routes.listUsers, component: UsersListPage, exact: true, protected: true },
  { path: routes.listGames, component: ListGamesPage, exact: true, protected: true },
  { path: routes.chooseTickets, component: ChooseTicketsPage, exact: true, protected: true },
  { path: routes.play, component: PlayGamePage, exact: true, protected: true },
  { path: routes.viewTicket, component: ViewTicketPage, exact: true, protected: true },
  { path: routes.pastGames, component: PastGamesPage, exact: true, protected: true },
  { path: routes.trackListing, component: TrackListingPage, exact: true, protected: true },
  { path: routes.privacy, component: PrivacyPolicyPage, exact: true },
  { path: routes.settingsSection, component: SettingsSectionPage, exact: true, protected: true },
  { path: routes.settingsIndex, component: SettingsIndexPage, exact: true, protected: true },
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
        <Switch>
          {routeComponents.filter(route => route.protected === true).map((route, index) => (
            <Route exact={route.exact} path={route.path} key={index} component={LoginRequired} />
          ))}
        </Switch>
      </div>
        <footer>
          <p className="footer">
            <span className="copyright">(c) 2020 Alex Ashley</span>
            <span className="github-link" >
              <a href="https://github.com/asrashley/music-bingo">github.com/asrashley/music-bingo</a>
            </span>
            <span className="privacy-policy">
              <Link to={reverse(`${routes.privacy}`)}>Privacy Policy</Link>
              </span>
          </p>
        </footer>
    </ConnectedRouter>
  );
}

export default App;
