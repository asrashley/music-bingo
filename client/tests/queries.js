import { buildQueries } from '@testing-library/react';
import log from 'loglevel';

/* custom query that looks for a "data-last-update" attribute in the container and compares that to
  the value provided to the query. It can be used to check if a component has been updated or
  to wait for it to re-render
  */
const queryAllByLastUpdate = (container, lastUpdate, options = {}) => {
    const { comparison } = {
        comparison: 'equals',
        ...options
    };
    log.trace(`queryAllByLastUpdate lastUpdate=${lastUpdate} comparison=${comparison} container="${container.nodeName}.${container.className}" ${container.id}`);
    return Array.from(container.querySelectorAll('[data-last-update]'))
        .filter((elt) => {
            const update = parseInt(elt.dataset.lastUpdate, 10);
            log.trace(`${elt.nodeName}.${elt.className} lastUpdate = ${update}`);
            if (isNaN(update)) {
                return false;
            }
            switch (comparison) {
                case 'equals':
                    return update === lastUpdate;
                case 'greaterThan':
                    return update > lastUpdate;
                case 'greaterThanOrEquals':
                    return update >= lastUpdate;
                case 'lessThan':
                    return update < lastUpdate;
                case 'lessThanOrEquals':
                    return update <= lastUpdate;
                default:
                    return true;
            }
        });
};

const [queryByLastUpdate, getAllLastUpdate, getByLastUpdate, findAllLastUpdate, findByLastUpdate] = buildQueries(
    queryAllByLastUpdate,
    (container, selector) => `Found multiple elements from ${container} with last update selector: ${selector}`,
    (container, selector, opts = {}) => {
        const { comparison = 'equals' } = opts;
        return (`Unable to find an element from ${container.nodeName}.${container.className} with last update ${comparison} ${selector}`);
    }
);

export const lastUpdatedQueries = {
    queryByLastUpdate,
    getAllLastUpdate,
    getByLastUpdate,
    findAllLastUpdate,
    findByLastUpdate
};

/* custom query that uses a CSS selector to find elements */
const queryAllBySelector = (container, selector) => {
    log.trace(`queryAllBySelector ${selector}`);
    return Array.from(container.querySelectorAll(selector));
};

const [queryBySelector, getAllBySelector, getBySelector, findAllBySelector, findBySelector] = buildQueries(
    queryAllBySelector,
    (container, selector) => `Found multiple elements from ${container} with selector: ${selector}`,
    (container, selector) => `Unable to find an element from ${container} with selector: ${selector}`,
);

export const bySelectorQueries = {
    queryBySelector,
    getAllBySelector,
    getBySelector,
    findAllBySelector,
    findBySelector
};
