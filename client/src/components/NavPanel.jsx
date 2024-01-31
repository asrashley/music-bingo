import React, { useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { createSelector } from '@reduxjs/toolkit';

import { NavMenuComponent } from './NavMenu';

import { getGameMenuItems, getUserMenuItems } from '../menu';
import { getUser } from '../user/userSelectors';
import { getBreadcrumbs, getCurrentAppSection } from '../routes/routesSelectors';
import { appSections } from '../routes/appSections';
import { getBuildInfo } from '../system/systemSelectors';

import { BuildInfoPropType } from '../system/types/BuildInfo';
import { UserPropType } from '../user/types/User';
import { MenuItemPropType, SectionItemPropType } from '../types/Menu';

import { fetchSystemIfNeeded } from '../system/systemSlice';

function NavPanelComponent({
  breadcrumbs, user, sections, buildInfo, dispatch, gameMenu, userMenu
}) {
  const className = useMemo(
    () => ("navbar navbar-expand navbar-light " + Object.keys(user.groups).join(" ")),
    [user.groups]);
  const branch = useMemo(() => buildInfo.branch !== "main" ? buildInfo.branch : "",
    [buildInfo.branch]);

  useEffect(() => {
    dispatch(fetchSystemIfNeeded());
  }, [dispatch]);

  return (
    <div id="nav-bar">
      <NavMenuComponent
        className={className}
        sections={sections}
        user={user}
        gameMenu={gameMenu}
        userMenu={userMenu}
      />
      <nav aria-label="breadcrumb" className="navbar navbar-light breadcrumbs">
        <ol className="breadcrumb">
          {breadcrumbs.map((crumb, idx) => <li key={idx} className={crumb.className}>
            {crumb.url ? <Link to={crumb.url}>{crumb.label}</Link> : <span>{crumb.label}</span>}
          </li>)
          }
        </ol>
      </nav>
      <div className="version-info">
        <p className="version">{branch} v{buildInfo.version}</p>
        <p className="hash">{buildInfo.commit.shortHash}</p>
      </div>
    </div>
  );
}

NavPanelComponent.propTypes = {
  dispatch: PropTypes.func.isRequired,
  user: UserPropType.isRequired,
  sections: PropTypes.objectOf(SectionItemPropType),
  breadcrumbs: PropTypes.array.isRequired,
  buildInfo: BuildInfoPropType.isRequired,
  gameMenu: PropTypes.arrayOf(MenuItemPropType),
  userMenu: PropTypes.arrayOf(MenuItemPropType),
};

const getSections = createSelector(
  [getCurrentAppSection], (currentSection) => {
    const sections = {};
    appSections.forEach(area => {
      const active = currentSection === area;
      sections[area] = {
        active,
        id: area,
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
    buildInfo: getBuildInfo(state, ownProps),
    gameMenu: getGameMenuItems(state, ownProps),
    userMenu: getUserMenuItems(state, ownProps),
  };
};

export const NavPanel = connect(mapStateToProps)(NavPanelComponent);
