import React from 'react';
import { useDispatch } from 'react-redux';
import { AdminActions } from '../../admin/components/AdminActions';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

export function GameAdminActions() {
    const dispatch = useDispatch();
    const onReload = () => {
        dispatch(invalidateGames());
        dispatch(fetchGamesIfNeeded());
    };

    return (
        <AdminActions alwaysShowChildren={true}>
            <button
                className="btn btn-primary"
                onClick={onReload}>
                Reload
            </button>
        </AdminActions>
    );
}
