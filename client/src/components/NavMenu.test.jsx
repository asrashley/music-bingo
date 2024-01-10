import { fireEvent } from "@testing-library/dom";
import { screen } from '@testing-library/react'
import { renderWithProviders } from "../../tests";

import { DropDownMenuItem, DropDownMenu, NavMenuComponent } from './NavMenu';

describe('NavMenuComponent', () => {
    const gameMenu = [{
        title: 'game title one',
        href: '/game/one',

    }, {
        title: 'game title two',
        href: '/game/two',
    }];
    const userMenu = [{
        title: 'User title one',
        href: '/user/one',

    }, {
        title: 'user title two',
        href: '/user/two',
    }];
    const notActiveItem = {
        item: '',
        link: '',
    };
    const sections = {
        Home: notActiveItem,
        Game: notActiveItem,
        Clips: notActiveItem,
        History: {
            item: 'active',
            link: 'active',
        },
        User: notActiveItem,
    };

    it('DropdownMenuItem', () => {
        const onClick = vi.fn();
        const title = 'Menu Item Title';
        const { container, getByText } = renderWithProviders(
            <DropDownMenuItem onClick={onClick} href="/href-link" title={title} />);
        expect(container.querySelector('a[href="/href-link"]')).not.toBeNull();
        fireEvent.click(getByText(title));
        expect(onClick).toHaveBeenCalled();
    });

    it('DropDownMenu', async () => {
        const title = "Menu Title";
        const section = {
            item: 'active',
            link: 'active',
        };
        const { getByText } = renderWithProviders(
            <DropDownMenu items={gameMenu} section={section} title={title} />);
        getByText(title);
        gameMenu.forEach(item => {
            getByText(item.title);
        })
        fireEvent.click(getByText(title));
        await screen.findAllByText(title);
        expect(document.querySelector('.dropdown-menu.show')).not.toBeNull();
        fireEvent.click(screen.getByText(gameMenu[1].title));
        await screen.findAllByText(title);
        expect(document.querySelector('.dropdown-menu.show')).toBeNull();
    });

    describe('NavMenuComponent', () => {
        it('matches snapshot', () => {
            const user = {
                pk: 5,
                loggedIn: true,
                email: 'Fred.Flintstone@unit.test',
                username: 'Fred Flintstone',
                groups: {},
            };
            const props = {
                className: 'menu-class',
                sections,
                user,
                gameMenu,
                userMenu,
            };
            const { asFragment, getByText, queryByText } = renderWithProviders(<NavMenuComponent {...props} />);
            getByText(user.username);
            expect(queryByText('Clips')).toBeNull();
            expect(asFragment()).toMatchSnapshot();
        });

        it('shows clip menu for users in the creators group', () => {
            const user = {
                loggedIn: true,
                username: 'a.user',
                pk: 6,
                email: 'a.user@unit.test',
                groups: {
                    users: true,
                    creators: true,
                },
            };
            const props = {
                className: 'menu-class',
                sections,
                user,
                gameMenu,
                userMenu,
            };
            const { getByText } = renderWithProviders(<NavMenuComponent {...props} />);
            getByText(user.username);
            getByText('Clips');
        });

        it('shows log in invite', () => {
            const user = {
                loggedIn: false,
                username: 'not.shown',
                pk: 8,
                email: '',
                groups: {
                },
            };
            const props = {
                className: 'menu-class',
                sections,
                user,
                gameMenu,
                userMenu,
            };
            const { getByText, queryByText } = renderWithProviders(<NavMenuComponent {...props} />);
            expect(queryByText('Clips')).toBeNull();
            expect(queryByText('not.shown')).toBeNull();
            getByText('Log in');
        });
    });
});