import { reverse } from 'named-urls';

import { routes } from '../routes/routes';
import { getUser } from '../user/userSelectors';

const adminMenuItems = [{
    title: 'Modify Users',
    href: reverse(`${routes.listUsers}`),
}, {
    title: 'Modify Settings',
    href: reverse(`${routes.settingsIndex}`),
}, {
    title: 'Guest links',
    href: reverse(`${routes.guestLinks}`),
}];

const loggedInUserMenuItems = [{
    title: 'User Profile',
    href: reverse(`${routes.user}`),
}, {
    title: 'Modify My Account',
    href: reverse(`${routes.changeUser}`),
}, {
    title: 'Log out',
    href: reverse(`${routes.logout}`),
}];

const adminLoggedIn = [
    ...adminMenuItems,
    ...loggedInUserMenuItems,
];

const guestMenuItems = [{
    title: 'Log In',
    href: reverse(`${routes.login}`),
}];

export function getUserMenuItems(state, props) {
    const user = getUser(state, props);
    if (!user.loggedIn) {
        return guestMenuItems;
    }
    if (user.groups.admin === true) {
        return adminLoggedIn;
    }
    return loggedInUserMenuItems;
}
