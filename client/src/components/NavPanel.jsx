import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';
import GitInfo from 'react-git-info/macro';

import { getUser } from '../user/userSelectors';
import { getGameId } from '../games/gamesSelectors';
import { getBreadcrumbs, getLocation } from '../routes/selectors';

import routes from '../routes';
import { initialState } from '../app/initialState';
import { createSelector } from '@reduxjs/toolkit';

const gitInfo = GitInfo();

class NavPanel extends React.Component {
  static sections = [
    'Home', 'Game', 'History', 'User', 'Users',
  ];

  static propTypes = {
    user: PropTypes.object.isRequired,
    sections: PropTypes.object.isRequired,
    gamePk: PropTypes.number,
  };

  render() {
    const { breadcrumbs, user, sections, gameId } = this.props;
    let manage = '';
    if (user.groups.admin === true) {
      manage = (
        <React.Fragment>
          <li className={`nav-item ${sections.Users.item}`}>
            <Link className={`nav-link ${sections.Users.link}`}
              to={reverse(`${routes.listUsers}`)}
            >Users
              </Link>
          </li>
        </React.Fragment>
      );
    }

    const className = "navbar navbar-expand navbar-light " + Object.keys(user.groups).join(" ");
    return (
      <div id="nav-bar">
        <nav id="nav-menu" className={className}>
          <Link className="navbar-brand" to={reverse(`${routes.index}`)}>
            <img src={`${process.env.PUBLIC_URL}/img/Icon.png`} width="30" height="30"
              className="d-inline-block align-top" alt="" />
          Musical Bingo
          </Link>
          <button className="navbar-toggler" type="button"
            data-toggle="collapse" data-target="#nav-menu"
            aria-controls="nav-menu" aria-expanded="false"
            aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="nav nav-pills">
              <li className={`nav-item ${sections.Home.item}`}>
                <Link className={`nav-link ${sections.Home.link}`}
                  to={reverse(`${routes.index}`)}>
                  Home <span className="sr-only">(current)</span>
                </Link>
              </li>
              {manage}
              <li className={`nav-item ${sections.Game.item}`}>
                <Link className={`nav-link ${sections.Game.link}`}
                  to={gameId ? reverse(`${routes.play}`, { gameId }) : reverse(`${routes.listGames}`)}
                >Now Playing
              </Link>
              </li>
              <li className={`nav-item ${sections.History.item}`}>
                <Link className={`nav-link ${sections.History.link}`}
                  to={reverse(`${routes.pastGames}`)}
                >Previous Games
              </Link>
              </li>
              <li className={`nav-item ${sections.User.item}`}>
                {
                  user.loggedIn ?
                    <Link
                      to={reverse(`${routes.logout}`)}
                      className={`logout nav-link  ${sections.User.link}`}
                    >Log Out</Link> :
                    <Link to={reverse('login')}
                      className={`login nav-link  ${sections.User.link}`}
                    >Log in</Link>
                }
              </li>
            </ul>
          </div>
        </nav>
        <nav aria-label="breadcrumb" className="navbar navbar-light breadcrumbs">
          <ol className="breadcrumb">
            {breadcrumbs.map((crumb, idx) => <li key={idx} className={crumb.className}>
              {crumb.url ? <Link to={crumb.url}>{crumb.label}</Link> : <span>{crumb.label}</span>}
            </li>)
            }
          </ol>
        </nav>
        <div className="version-info">
          <p className="tags">{gitInfo.commit.tags}</p>
          <p className="hash">{gitInfo.commit.shortHash}</p>
        </div>
      </div>
    );
  }
}

const getCurrentSection = createSelector(
  [getBreadcrumbs], (breadcrumbs) => {
    let currentSection = 'Home';
    breadcrumbs.forEach(part => {
      if (NavPanel.sections.includes(part.label)) {
        currentSection = part.label;
      }
    });
    console.log(`currentSection ${currentSection}`);
    return currentSection;
  });

const getSections = createSelector(
  [getCurrentSection, getGameId], (currentSection, gameId) => {
    const sections = {};
    NavPanel.sections.forEach(area => {
      const active = currentSection === area;
      sections[area] = {
        item: active ? 'active' : '',
        link: active ? 'active' : '',
      };
    });
    if (!gameId && currentSection !== 'Game') {
      sections.Game.link = 'disabled';
    }
    return sections;
  });

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    breadcrumbs: getBreadcrumbs(state, ownProps),
    currentSection: getCurrentSection(state, ownProps),
    gameId: getGameId(state, ownProps),
    user: getUser(state, ownProps),
    location: getLocation(state, ownProps),
    sections: getSections(state, ownProps),
  };
};

NavPanel = connect(mapStateToProps)(NavPanel);
export { NavPanel };
