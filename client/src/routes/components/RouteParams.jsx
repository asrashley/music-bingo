import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux'
import { useLocation, useParams } from 'react-router-dom';

import { onRouteParamsChanged } from '../routesSlice';

export function RouteParams() {
    const dispatch = useDispatch();
    const [keyLocation, setKeyLocation] = useState('');
    const params = useParams();
    const { key, hash, pathname, state: routeState } = useLocation();

    useEffect(() => {
        if (keyLocation !== key) {
            setKeyLocation(key);
            dispatch(onRouteParamsChanged({ params, hash, pathname, routeState }));
        }
    }, [dispatch, hash, key, keyLocation, params, pathname, routeState]);

    return null;
}
