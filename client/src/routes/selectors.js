import { createSelector } from 'reselect';

import routes from './index';

const getRouter = (state) => state.router;

export const getLocation = createSelector([getRouter], router => router.location);

function titleCase(str) {
  const first = str.charAt(0).toUpperCase();
  return first + str.slice(1);
}

function breadcrumbTitle(name) {
  if (/^[\d-]+$/.test(name)) {
    return name;
  }
  return name.split('-').map(p => titleCase(p)).join(' ');
}

export const getBreadcrumbs = createSelector([getLocation],
  (location) => {
    const path = (location.pathname === "/") ? [""] : location.pathname.split('/');
    let url = routes.index;
    return path.map((part, idx) => {
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
        label: breadcrumbTitle(part),
        url
      };
      if (idx === (path.length - 1)) {
        crumb.className += ' active';
        crumb.url = null;
      }
      return crumb;
    });
  });
