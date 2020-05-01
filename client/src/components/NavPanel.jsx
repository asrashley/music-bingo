import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import routes from '../routes';
import { initialState } from '../app/initialState';
import { userIsLoggedIn } from '../user/userSlice';

class NavPanel extends React.Component {
  static sections = [
    'home', 'game', 'history', 'user', 'users',
  ];

  static propTypes = {
    user: PropTypes.object.isRequired,
    sections: PropTypes.object.isRequired,
    gamePk: PropTypes.number,
  };

  render() {
    const { breadcrumbs, user, sections, currentSection, loggedIn } = this.props;
    const gamePk = user.activeGame;
    let manage = '';
    if (user.groups.admin === true) {
      manage = (
        <React.Fragment>
          <li className={`nav-item ${sections.users.item}`}>
            <Link className={`nav-link ${sections.users.link}`}
              to={reverse(`${routes.listUsers}`)}
            >Users
              </Link>
          </li>
        </React.Fragment>
      );
    }

    const className = "navbar navbar-expand-lg navbar-light " + Object.keys(user.groups).join(" ");
    return (
      <div id="nav-bar">
        <nav id="nav-menu" className={className}>
          <Link className="navbar-brand" to={reverse(`${routes.index}`)}>
            <img src={`${process.env.PUBLIC_URL}/img/Icon.png`} width="30" height="30"
              className="d-inline-block align-top" alt="" />
          Musical Bingo
          </Link>
          <button className="navbar-toggler" type="button"
            data-toggle="collapse" data-target="#navbarNav"
            aria-controls="navbarNav" aria-expanded="false"
            aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="nav nav-pills">
              <li className={`nav-item ${sections.home.item}`}>
                <Link className={`nav-link ${sections.home.link}`}
                  to={reverse(`${routes.index}`)}>
                  Home <span className="sr-only">(current)</span>
                </Link>
              </li>
              {manage}
              <li className={`nav-item ${sections.game.item}`}>
                <Link className={`nav-link ${sections.game.link}`}
                  to={gamePk ? reverse(`${routes.play}`, { gamePk }) : '#'}
                >Now Playing
              </Link>
              </li>
              <li className={`nav-item ${sections.history.item}`}>
                <Link className={`nav-link ${sections.history.link}`}
                  to={reverse(`${routes.pastGames}`)}
                >Previous Games
              </Link>
              </li>
              <li className={`nav-item ${sections.user.item}`}>
                {
                  loggedIn ?
                    <Link
                      to={reverse(`${routes.logout}`)}
                      className={`logout nav-link  ${sections.user.link}`}
                    >Log Out</Link> :
                    <Link to={reverse('login')}
                      className={`login nav-link  ${sections.user.link}`}
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

      </div>
    );
  }
}

function titleCase(str) {
  const first = str.charAt(0).toUpperCase();
  return first + str.slice(1);
}

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user, router } = state;
  const { location } = router;
  const sections = {};
  const gamePk = user.activeGame || -1;
  const path = (location.pathname === "/") ? [""] : location.pathname.split('/');
  let url = reverse(`${routes.index}`);
  let currentSection = 'home';
  const breadcrumbs = path.map((part, idx) => {
    if (!part) {
      part = 'Home';
    } else {
      if (url !== '/') {
        url += '/';
      }
      url += part;
    }
    const crumb = {
      className: 'breadcrumb-item',
      label: titleCase(part),
      url
    };
    if (idx === (path.length - 1)) {
      crumb.className += ' active';
      crumb.url = null;
    }
    if (NavPanel.sections.includes(part)) {
      currentSection = part;
    }
    return crumb;
  });
  NavPanel.sections.forEach(area => {
    const active = currentSection === area;
    /*console.log(`${area} ${active}`);*/
    sections[area] = {
      item: active ? 'active' : '',
      link: active ? 'active' : '',
    };
  });
  if (!gamePk) {
    sections.game.link = 'disabled';
    sections.play.link = 'disabled';
    sections.manage.link = 'disabled';
    sections.tracks.link = 'disabled';
  }

  return {
    breadcrumbs,
    gamePk,
    user,
    location,
    loggedIn: userIsLoggedIn(state),
    sections,
    currentSection,
  };
};

NavPanel = connect(mapStateToProps)(NavPanel);
export { NavPanel };
