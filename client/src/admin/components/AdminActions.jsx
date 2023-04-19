import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { createSelector } from 'reselect';
import { saveAs } from 'file-saver';

import {
  BusyDialog, ConfirmDialog, ErrorMessage, FileDialog, ProgressDialog
} from '../../components';
import { DisplayDialogContext } from '../../components/DisplayDialog';

import { addMessage } from '../../messages/messagesSlice';
import { importDatabase } from '../adminSlice';
import {
  deleteGame, fetchGamesIfNeeded, importGame, invalidateGames
} from '../../games/gamesSlice';
import { fetchUserIfNeeded } from '../../user/userSlice';

import { api } from '../../endpoints';

import { getDatabaseImportState } from '../adminSelectors';
import { getGameImportState } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { GamePropType } from '../../games/types/Game';
import { ImportingPropType } from '../../types/Importing';
import { UserPropType } from '../../user/types/User';

export class AdminActionsComponent extends React.Component {
  static DATABASE_IMPORT = 1;
  static GAME_IMPORT = 2;

  static contextType = DisplayDialogContext;

  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    onDelete: PropTypes.func,
    game: GamePropType,
    importing: ImportingPropType.isRequired,
    user: UserPropType.isRequired,
    buttonClassName: PropTypes.string,
    className: PropTypes.string,
    database: PropTypes.bool
  };

  state = {
    importType: 0,
    replaceDate: true,
    error: null
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  render() {
    const { error } = this.state;
    const { children, className = "action-panel", database,
      buttonClassName = 'ml-2',
      game, user, onDelete } = this.props;

    if (user.groups.admin !== true) {
      return null;
    }

    return (
      <React.Fragment>
        <ErrorMessage error={error} />
        {children}
        <div className={className}>
          <button className={`btn btn-primary ${buttonClassName}`}
            onClick={this.onClickImportGame}>
            Import Game
          </button>
          {game && <button className={`btn btn-primary ${buttonClassName}`}
            onClick={this.exportGame}>Export game</button>}
          {(game !== undefined && onDelete !== undefined) && <button className={`btn btn-danger ${buttonClassName}`}
            onClick={this.confirmDelete}>Delete game</button>}
          {(database === true) && <button className={`btn btn-primary ${buttonClassName}`}
            onClick={this.onClickImportDatabase}>Import Database
          </button>}
          {(database === true) && <button className={`btn btn-primary ${buttonClassName}`}
            onClick={this.exportDatabase}>Export Database
          </button>}
        </div>
      </React.Fragment>);
  }

  confirmDelete = (ev) => {
    const { openDialog } = this.context;
    ev.preventDefault();
    const { game } = this.props;
    openDialog(<ConfirmDialog
      changes={[
        `Delete group ${game.id}`
      ]}
      title="Confirm delete game"
      onCancel={this.cancelDialog}
      onConfirm={this.deleteGame}
    />);
    return false;
  };

  cancelDialog = () => {
    const { closeDialog } = this.context;
    closeDialog();
  };

  deleteGame = () => {
    const { game, dispatch, onDelete } = this.props;
    const { closeDialog } = this.context;
    closeDialog();
    dispatch(deleteGame(game)).then(result => {
      const { payload } = result;
      if (payload?.error || result.error) {
        this.setState({ error: (payload.error ? payload.error : result.error) });
      } else {
        onDelete(game);
      }
    });
  };

  onClickImportDatabase = () => {
    const { openDialog } = this.context;
    this.setState(() => ({ importType: AdminActions.DATABASE_IMPORT }),
      () => openDialog(<FileDialog
        title="Select a json database file to import"
        accept='.json,application/json'
        submit='Import database'
        onCancel={this.cancelDialog}
        onFileUpload={this.onFileSelected}
      />));
  };

  onChangeReplaceDate = (e) => {
    this.setState({
      replaceDate: e.target.checked
    });
  };

  onClickImportGame = () => {
    const { openDialog } = this.context;
    const extraFields = <div className="form-control">
      <label htmlFor="field-replaceDate" className="replace-date-label">Replace game start date during import?</label>
      <input type="checkbox" id="field-replaceDate" name="replaceDate" defaultChecked onChange={this.onChangeReplaceDate}></input>
    </div>;

    this.setState(() => ({ importType: AdminActions.GAME_IMPORT }),
      () => openDialog(<FileDialog
        title='Select a gameTracks.json file to import'
        accept='.json,application/json'
        submit='Import game'
        onCancel={this.cancelDialog}
        onFileUpload={this.onFileSelected}
        extraFields={extraFields}
      />));
  };

  importComplete = () => {
    const { databaseImporting, gameImporting, dispatch } = this.props;
    const { closeDialog } = this.context;
    const { importType } = this.state;
    if (importType === AdminActions.DATABASE_IMPORT && databaseImporting?.done === true) {
      document.location.reload();
      return;
    }
    if (importType === AdminActions.GAME_IMPORT && gameImporting?.done === true) {
      dispatch(invalidateGames());
      dispatch(fetchGamesIfNeeded());
    }
    closeDialog();
    this.setState({
      importType: 0,
    });
  };

  exportDatabase = () => {
    const { dispatch } = this.props;
    const { openDialog, closeDialog } = this.context;
    openDialog(<BusyDialog
      onClose={this.cancelDialog}
      title="Exporting database"
      text="Please wait, exporting database..."
    />);
    dispatch(api.exportDatabase()).then(response => {
      const filename = `database-${Date.now()}.json`;
      return response.payload.blob().then(blob => {
        closeDialog();
        saveAs(blob, filename);
        return filename;
      });
    });
  };

  exportGame = () => {
    const { dispatch, game } = this.props;
    dispatch(api.exportGame({
      gamePk: game.pk
    })).then(response => {
      const filename = `game-${game.id}.json`;
      return response.payload.blob().then(blob => {
        saveAs(blob, filename);
        return filename;
      });
    });
  };

  onFileSelected = (file) => {
    const { closeDialog } = this.context;
    var reader = new FileReader();
    reader.onload = (ev) => this.onFileLoaded(file.name, ev);
    reader.onerror = (err) => {
      closeDialog();
      addMessage({ type: "error", text: err });
    };
    reader.readAsText(file);
  };

  onFileLoaded(filename, event) {
    const { dispatch } = this.props;
    const { openDialog } = this.context;
    const { importType, replaceDate } = this.state;
    const title = importType === AdminActions.GAME_IMPORT ?
      `Importing game from "${filename}"` :
      `Importing database from "${filename}"`;

    openDialog(<ProgressDialog
      title={title}
      progress={this.props.importing}
      onCancel={this.cancelDialog}
      onClose={this.importComplete}
    />);
    const data = JSON.parse(event.target.result);
    if (importType === AdminActions.GAME_IMPORT) {
      if (replaceDate === true && 'Games' in data) {
        const start = new Date().toISOString();
        const end = new Date(Date.now() + 12 * 3600000).toISOString();
        data.Games = data.Games.map(game => ({
          ...game,
          start,
          end
        }));
      }
      dispatch(importGame(filename, data));
    } else {
      dispatch(importDatabase(filename, data));
    }
  }
}

const getImportState = createSelector(
  [getDatabaseImportState, getGameImportState],
  (databaseImporting, gameImporting) => {
    if (databaseImporting.importing === 'database') {
      return databaseImporting;
    }
    return gameImporting;
  });

const mapStateToProps = (state, props) => {
  return {
    importing: getImportState(state, props),
    user: getUser(state, props)
  };
};

export const AdminActions = connect(mapStateToProps)(AdminActionsComponent);