import React, { useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { createSelector } from '@reduxjs/toolkit';
import { reverse } from 'named-urls';

import { getGameMenuItems, getUserMenuItems } from '../menu';
import { getUser } from '../user/userSelectors';
import { getBreadcrumbs } from '../routes/selectors';
import { getBuildInfo } from '../system/systemSelectors';
import routes, { appSections } from '../routes';

import { BuildInfoPropType } from '../system/types/BuildInfo';
import { UserPropType } from '../user/types/User';
import { HistoryPropType } from '../types/History';

import { fetchSystemIfNeeded } from '../system/systemSlice';

const MenuItemPropType = PropTypes.shape({
  title: PropTypes.string.isRequired,
  href: PropTypes.string.isRequired,
});

const SectionItemPropType = PropTypes.shape({
  item: PropTypes.string.isRequired,
  link: PropTypes.string.isRequired,
});

function DropdownMenuItem({ href, title, onClick }) {
  return (
    <li>
      <Link className="dropdown-item" onClick={onClick} to={href}>{title}</Link>
    </li>
  );
}
DropdownMenuItem.propTypes = {
  href: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
};

function DropdownMenu({ title, items, section }) {
  const [expanded, setExpanded] = useState(false);
  const show = expanded ? 'show' : '';

  const toggleExpand = () => setExpanded(!expanded);

  return (
    <li className={`nav-item dropdown ${section.item ?? ''}`}>
      <button className={`nav-link dropdown-toggle ${section.link} ${show}`}
        aria-expanded={expanded} onClick={toggleExpand}>
        {title}
      </button>
      <ul className={`dropdown-menu  ${show}`}>
        {items.map(({ title, href }, idx) => <DropdownMenuItem
          key={`${idx}-${title}`} title={title} href={href} onClick={() => setExpanded(false)} />)}
      </ul>
    </li>
  );
}
DropdownMenu.propTypes = {
  section: SectionItemPropType.isRequired,
  title: PropTypes.string.isRequired,
  items: PropTypes.arrayOf(MenuItemPropType),
};

function NavMenuComponent({
  className, sections, user, gameMenu, userMenu }) {
  return (
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
          <DropdownMenu
            title="Previous Games"
            items={gameMenu}
            section={sections.History}
          />
          {user.groups.creators && <li className={`nav-item ${sections.Clips.item}`}>
            <Link className={`nav-link ${sections.Clips.link}`}
              to={reverse(`${routes.listDirectories}`)}
            >Clips
            </Link>
          </li>}
          {user.loggedIn ? <DropdownMenu
            title={user.loggedIn ? user.username : 'Log In'}
            items={userMenu}
            section={sections.User}
          /> : <li className={`nav-item ${sections.User.item}`}>
            <Link to={reverse(`${routes.login}`)}
              className={`login nav-link  ${sections.User.link}`}
            >Log in</Link>
          </li>
          }
        </ul>
      </div>
    </nav >
  );
}

NavMenuComponent.propTypes = {
  history: HistoryPropType.isRequired,
  sections: PropTypes.objectOf(SectionItemPropType),
  currentSection: PropTypes.string.isRequired,
  className: PropTypes.string.isRequired,
  user: UserPropType.isRequired,
  gameMenu: PropTypes.arrayOf(MenuItemPropType),
  userMenu: PropTypes.arrayOf(MenuItemPropType),
};

function NavPanelComponent({
  breadcrumbs, user, sections, buildInfo, dispatch, history, currentSection,
  gameMenu, userMenu
}) {
  useEffect(() => {
    dispatch(fetchSystemIfNeeded());
  }, [dispatch]);
  const className = useMemo(
    () => ("navbar navbar-expand navbar-light " + Object.keys(user.groups).join(" ")),
    [user.groups]);
  const branch = buildInfo.branch !== "main" ? buildInfo.branch : "";
  return (
    <div id="nav-bar">
      <NavMenuComponent
        className={className}
        sections={sections}
        currentSection={currentSection}
        user={user}
        gameMenu={gameMenu}
        userMenu={userMenu}
        history={history} />
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
  user: UserPropType.isRequired,
  currentSection: PropTypes.string.isRequired,
  sections: PropTypes.objectOf(SectionItemPropType),
  breadcrumbs: PropTypes.array.isRequired,
  buildInfo: BuildInfoPropType.isRequired,
  history: HistoryPropType.isRequired,
  gameMenu: PropTypes.arrayOf(MenuItemPropType),
  userMenu: PropTypes.arrayOf(MenuItemPropType),
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
    currentSection: getCurrentSection(state, ownProps),
    user: getUser(state, ownProps),
    sections: getSections(state, ownProps),
    buildInfo: getBuildInfo(state, ownProps),
    gameMenu: getGameMenuItems(state, ownProps),
    userMenu: getUserMenuItems(state, ownProps),
  };
};

export const NavPanel = connect(mapStateToProps)(NavPanelComponent);
