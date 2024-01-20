import React from 'react';
import { ReduxRouter } from '@lagunovsky/redux-react-router';
import { Link, Outlet, Route, Routes } from 'react-router-dom';
import { reverse } from 'named-urls';

import { NavPanel } from '../components/NavPanel';
import { DisplayDialog } from '../components/DisplayDialog';
import { routes, RouteParams } from '../routes';
import { IndexPage } from './IndexPage';
import { DirectoryListPage } from '../directories/components';
import {
  PastGamesButtons,
  ListGamesPage,
  PastGamesPage,
  PastGamesPopularityPage,
  PastGamesLastUsagePage,
  PastGamesCalendarPage,
  TrackListingPage
} from '../games/components';

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

const routerSelector = (state) => state.router

function App() {
  return (
    <ReduxRouter history={history} routerSelector={routerSelector}>
      <NavPanel />
      <div className="container">
        <MessagePanel />
        <DisplayDialog>
          <Routes>
            <Route path="/" element={<IndexPage />} />
            <Route path="clips" element={<LoginRequired><Outlet /></LoginRequired>}>
              <Route path="" element={<DirectoryListPage />} />
              <Route path=":dirPk" element={<DirectoryListPage />} />
            </Route>
            <Route path="game" element={<LoginRequired><Outlet /><RouteParams /></LoginRequired>}>
              <Route path="" element={<ListGamesPage />} />
              <Route path=":gameId" element={<Outlet />}>
                <Route path="" element={<ChooseTicketsPage />} />
                <Route path="tickets" element={<PlayGamePage />} />
                <Route path="tickets/:ticketPk" element={<ViewTicketPage />} />
              </Route>
            </Route>
            <Route path="history" element={<LoginRequired><RouteParams /><PastGamesButtons /></LoginRequired>}>
              <Route path="" element={< PastGamesPopularityPage />} />
              <Route path="calendar" element={<PastGamesCalendarPage />} />
              <Route path="games" element={<Outlet />}>
                <Route path="" element={<PastGamesPage />} />
                <Route path=":gameId" element={<TrackListingPage />} />
              </Route>
              <Route path="themes" element={<Outlet />}>
                <Route path="" element={<PastGamesLastUsagePage />} />
                <Route path=":slug" element={<Outlet />}>
                  <Route path="" element={<PastGamesPage />} />
                  <Route path=":gameId" element={<TrackListingPage />} />
                </Route>
              </Route>
            </Route>
            <Route path="privacy" element={<PrivacyPolicyPage />} />
            <Route path="user" element={<><RouteParams /><Outlet /></>}>
              <Route path="" element={<UserPage />} />
              <Route path="guests" element={<LoginRequired><GuestLinksPage /></LoginRequired>} />
              <Route path="login" element={<LoginPage />} />
              <Route path="logout" element={<LogoutPage />} />
              <Route path="modify" element={<LoginRequired><ChangeUserPage /></LoginRequired>} />
              <Route path="reset" element={<PasswordResetPage />} />
              <Route path="reset/:token" element={<PasswordResetConfirmPage />} />
              <Route path="settings" element={<LoginRequired><Outlet /></LoginRequired>}>
                <Route path="" element={<SettingsIndexPage />} />
                <Route path=":section" element={<SettingsSectionPage />} />
              </Route>
              <Route path="users" element={<LoginRequired><UsersListPage /></LoginRequired>} />
            </Route>
            <Route path={routes.guestAccess} element={<GuestAccessPage />} />
            <Route path={routes.register} element={<RegisterPage />} />
          </Routes>
        </DisplayDialog>
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
    </ReduxRouter >
  );
}

export default App;
