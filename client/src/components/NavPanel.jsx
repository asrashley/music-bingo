import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import routes from '../routes';
import { initialState } from '../app/initialState';

class NavPanel extends React.Component {
  render() {
    const { user, location } = this.props;
    const gamePk = user.activeGame;
    let section = 'home';
    const sections = {
      home: { item: '', link: ''},
      game: { item: '', link: ''},
      manage: { item: '', link: ''},
      play: { item: '', link: '' },
      user: { item: '', link: ''},
    };
    Object.keys(sections).forEach(area => {
      const re = RegExp(`/${area}`);
      if (re.test(location.pathname)) {
        section = area;
      }
    });
    sections[section].item = 'active';
    sections[section].link = 'active';
    if (!gamePk) {
      sections.game.link = 'disabled';
      sections.play.link = 'disabled';
      sections.manage.link = 'disabled';
    }
    let manage = '';
    if (user.groups.admin === true) {
      manage = (
        <li className={`nav-item ${sections.manage.item}`}>
        <Link className={`nav-link ${sections.manage.link}`}
          to={gamePk ? reverse(`${routes.manage}`, { gamePk }) : '#'}
        >Manage Game
              </Link>
      </li>);
    }

    const className = "navbar navbar-expand-lg navbar-light  " + Object.keys(user.groups).join(" ");
    return(
      <nav className={className}>
        <Link className="navbar-brand" to={reverse(`${routes.index}`)}>Musical Bingo</Link>
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
            <li className={`nav-item ${sections.game.item}`}>
              <Link className={`nav-link ${sections.game.link}`}
                            to={gamePk ? reverse(`${routes.game}`, { gamePk }) : '#'}
              >Choose Tickets
              </Link>
            </li>
            {manage}
            <li className={`nav-item ${sections.play.item}`}>
              <Link  className={`nav-link ${sections.play.link}`}
                      to={gamePk ? reverse(`${routes.play}`, { gamePk}) : '#'}
              >Play
              </Link>
            </li>
            <li className={`nav-item ${sections.user.item}`}>
              {
                (user === undefined)  ?
                  (<Link to={reverse('login')}
                         className={`login nav-link  ${sections.user.link}`}
                   >Log in</Link>) :
                (<Link
                    to={reverse(`${routes.logout}`)}
                   className={`logout nav-link  ${sections.user.link}`}
                 >Log Out</Link>)
              }
            </li>
          </ul>
        </div>
      </nav>
    );
  }
}

NavPanel.propTypes = {
  user: PropTypes.object.isRequired,
  };
//gamePk: PropTypes.number,

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user, router } = state;
  const { location } = router;
  return {
    user,
    location,
  };
};

NavPanel = connect(mapStateToProps)(NavPanel);
export { NavPanel };
