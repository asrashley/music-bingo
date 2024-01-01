import { getPathname, getBreadcrumbs } from './routesSelectors';
import { routes } from './routes';

const testCases = {
  '/': [
    {
      className: "breadcrumb-item active",
      label: 'Home',
      url: null,
    }
  ],
  '/register': [
    {
      className: "breadcrumb-item",
      label: "Home",
      url: "/"
    }, {
      className: "breadcrumb-item active",
      label: "Register",
      url: null
    }
  ],
  '/user/modify': [
    {
      className: "breadcrumb-item",
      label: "Home",
      url: "/"
    }, {
      className: "breadcrumb-item",
      label: "User",
      url: "/user"
    }, {
      className: "breadcrumb-item active",
      label: "Modify",
      url: null
    }
  ],
  '/game/2023-03-01/23': [
    {
      className: "breadcrumb-item",
      label: "Home",
      url: "/"
    }, {
      className: "breadcrumb-item",
      label: "Game",
      url: "/game"
    }, {
      className: "breadcrumb-item",
      label: "2023-03-01",
      url: "/game/2023-03-01"
    }, {
      className: "breadcrumb-item active",
      label: "23",
      url: null
    }
  ]
};

describe('routes selectors', () => {
  it('index route is defined', () => {
    expect(routes.index).toBe('/');
  });

  it.each(Object.keys(testCases))('generates breadcrumb context for "%s"', (pathname) => {
    const state = {
      router: {
        location: {
          pathname
        }
      }
    };
    expect(getPathname(state)).toEqual(pathname);
    expect(getBreadcrumbs(state)).toEqual(testCases[pathname]);
  });
});