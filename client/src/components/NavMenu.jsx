import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { reverse } from 'named-urls';
import { Link } from 'react-router-dom';

import { routes } from '../routes/routes';

import { MenuItemPropType, SectionItemPropType } from '../types/Menu';
import { UserPropType } from '../user/types/User';

export function DropDownMenuItem({ href, title, onClick }) {
    return (
        <li>
            <Link className="dropdown-item" onClick={onClick} to={href}>{title}</Link>
        </li>
    );
}
DropDownMenuItem.propTypes = {
    href: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
};

export function DropDownMenu({ title, items, section }) {
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
                {items.map(({ title, href }, idx) => <DropDownMenuItem
                    key={`${idx}-${title}`} title={title} href={href} onClick={() => setExpanded(false)} />)}
            </ul>
        </li>
    );
}
DropDownMenu.propTypes = {
    section: SectionItemPropType.isRequired,
    title: PropTypes.string.isRequired,
    items: PropTypes.arrayOf(MenuItemPropType),
};

export function NavMenuComponent({
    className, gameMenu, sections, user, userMenu }) {
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
                    <DropDownMenu
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
                    {user.loggedIn ? <DropDownMenu
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
    className: PropTypes.string.isRequired,
    gameMenu: PropTypes.arrayOf(MenuItemPropType),
    sections: PropTypes.objectOf(SectionItemPropType),
    user: UserPropType.isRequired,
    userMenu: PropTypes.arrayOf(MenuItemPropType),
};
