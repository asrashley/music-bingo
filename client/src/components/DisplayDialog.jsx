import { Fragment, createContext, useCallback, useContext, useMemo, useState } from 'react';
import PropTypes from 'prop-types';

const initialState = {
  ActiveDialog: null,
  dialogProps: null
};

export const DisplayDialogContext = createContext(initialState);

export const useDisplayDialogContext = () => useContext(DisplayDialogContext);

export function DisplayDialog({ children }) {
  const [activeDialog, setActiveDialog] = useState(null);
  const [currentId, setCurrentId] = useState(null);

  const openDialog = useCallback((dialog, { id } = {}) => {
    setActiveDialog(dialog);
    if (id === undefined) {
      id = Date.now();
    }
    setCurrentId(id);
    return id;
  }, []);

  const closeDialog = useCallback(() => {
    setActiveDialog(null);
    setCurrentId(null);
  }, []);

  const getCurrentId = useCallback(() => currentId, [currentId]);

  const contextValue = useMemo(() => ({
    openDialog,
    closeDialog,
    getCurrentId
  }), [openDialog, closeDialog, getCurrentId]);

  return (
    <Fragment>
      <DisplayDialogContext.Provider value={contextValue}>
        {children}
      </DisplayDialogContext.Provider>
      {activeDialog}
    </Fragment>
  );
}
/*      {ActiveDialog !== null && <ActiveDialog {...dialogProps} />}
*/
DisplayDialog.propTypes = {
  children: PropTypes.node
};

