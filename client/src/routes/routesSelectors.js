import { createSelector } from 'reselect';

import { routes } from './routes';
import { appSections } from './appSections';

const getRouter = (state) => state.router;
const getRoutesState = (state) => state.routes;

export const getPathname = createSelector([getRouter], router => router.location.pathname);

export const getRouteParams = createSelector([getRoutesState], routes => routes.params);

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

export const getBreadcrumbs = createSelector([getPathname],
  (pathname) => {
    const path = (pathname === "/") ? [""] : pathname.split('/');
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

export const getCurrentAppSection = createSelector(
  [getBreadcrumbs], (breadcrumbs) => {
    let currentSection = 'Home';
    breadcrumbs.forEach(part => {
      if (appSections.includes(part.label)) {
        currentSection = part.label;
      }
    });
    return currentSection;
  });
