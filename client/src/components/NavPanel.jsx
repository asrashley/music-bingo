import React, { useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { createSelector } from '@reduxjs/toolkit';
import { reverse } from 'named-urls';

import { getUser } from '../user/userSelectors';
import { getBreadcrumbs } from '../routes/selectors';
import { getGitInfo } from '../system/systemSelectors';

import routes from '../routes';
import { GitInfoType } from '../system/types/GitInfo';

import { fetchSystemIfNeeded } from '../system/systemSlice';

const appSections = [
  'Home', 'Game', 'History', 'Directories', 'User', 'Users',
];

function NavPanelComponent({ breadcrumbs, user, sections, gitInfo, dispatch }) {
  useEffect(() => {
    dispatch(fetchSystemIfNeeded());
  }, [dispatch]);
  const className = useMemo(
    () => ("navbar navbar-expand navbar-light " + Object.keys(user.groups).join(" ")),
    [user.groups]);
  const branch = gitInfo.branch !== "main" ? gitInfo.branch : "";
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
            <li className={`nav-item ${sections.Game.item}`}>
              <Link className={`nav-link ${sections.Game.link}`}
                to={reverse(`${routes.listGames}`)}
              >Now Playing
              </Link>
            </li>
            <li className={`nav-item ${sections.History.item}`}>
              <Link className={`nav-link ${sections.History.link}`}
                to={reverse(`${routes.pastGames}`)}
              >Previous Games
              </Link>
            </li>
            {user.groups.creators && <li className={`nav-item ${sections.Directories.item}`}>
              <Link className={`nav-link ${sections.Directories.link}`}
                to={reverse(`${routes.listDirectories}`)}
              >Clips
              </Link>
            </li>}
            <li className={`nav-item ${sections.User.item}`}>
              {
                user.loggedIn ?
                  <Link
                    to={reverse(`${routes.user}`)}
                    className={`logout nav-link  ${sections.User.link}`}
                  >{user.username}</Link> :
                  <Link to={reverse(`${routes.login}`)}
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
        <p className="tags">{branch} {gitInfo.tags}</p>
        <p className="hash">{gitInfo.commit.shortHash}</p>
      </div>
    </div>
  );
}

NavPanelComponent.propTypes = {
  user: PropTypes.object.isRequired,
  sections: PropTypes.object.isRequired,
  breadcrumbs: PropTypes.array.isRequired,
  gitInfo: GitInfoType.isRequired
};

const getCurrentSection = createSelector(
  [getBreadcrumbs], (breadcrumbs) => {
    let currentSection = 'Home';
    breadcrumbs.forEach(part => {
      if (appSections.includes(part.label)) {
        currentSection = part.label;
      }
    });
    return currentSection;
  });

const getSections = createSelector(
  [getCurrentSection], (currentSection) => {
    const sections = {};
    appSections.forEach(area => {
      const active = currentSection === area;
      sections[area] = {
        item: active ? 'active' : '',
        link: active ? 'active' : '',
      };
    });
    return sections;
  });

const mapStateToProps = (state, ownProps) => {
  return {
    breadcrumbs: getBreadcrumbs(state, ownProps),
    user: getUser(state, ownProps),
    sections: getSections(state, ownProps),
    gitInfo: getGitInfo(state, ownProps),
  };
};

export const NavPanel = connect(mapStateToProps)(NavPanelComponent);
