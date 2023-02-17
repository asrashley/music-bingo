import React from 'react';
import PropTypes from 'prop-types';
import { saveAs } from 'file-saver';

import {
  BusyDialog, ConfirmDialog, FileDialog, ProgressDialog
} from '../../components';

import { addMessage } from '../../messages/messagesSlice';
import { importDatabase } from '../../admin/adminSlice';
import {
  deleteGame, fetchGamesIfNeeded, importGame, invalidateGames
} from '../gamesSlice';

import { api } from '../../endpoints';

import { GamePropType } from '../types/Game';

export function AdminActionPanel({ deleteGame, exportGame, importGame, game }) {
  return (
    <div className="action-panel">
      <button className="btn btn-primary ml-2" onClick={importGame}>
        Import a game
      </button>
      {(game && exportGame) && <button className="btn btn-primary ml-2"
        onClick={exportGame}>Export game</button>}
      {(game && deleteGame) && <button className="btn btn-danger ml-2"
        onClick={deleteGame}>Delete game</button>}
    </div>
  );
}

AdminActionPanel.propTypes = {
  game: GamePropType,
  deleteGame: PropTypes.func,
  exportGame: PropTypes.func,
  importGame: PropTypes.func.isRequired,
};

function ErrorMessage({ error }) {
  if (!error) {
    return null;
  }
  return (
    <div className="alert alert-warning" role="alert">
      <span className="error-message">{error}</span>
    </div>
    );
}
ErrorMessage.propTypes = {
  error: PropTypes.string
};

export class AdminGameActions extends React.Component {
  static DATABASE_IMPORT = 1;
  static GAME_IMPORT = 2;

  static propTypes = {
    databaseImporting: PropTypes.object,
    dispatch: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    game: GamePropType,
    gameImporting: PropTypes.object,
    importing: PropTypes.object,
  };

  state = {
    ActiveDialog: null,
    dialogData: null,
    importType: 0,
    error: null
  };

  render() {
    const { ActiveDialog, dialogData, error } = this.state;
    const { children, game, importing } = this.props;

    return (
      <React.Fragment>
        <ErrorMessage error={error} />
        {children}
        <AdminActionPanel
          game={game}
          deleteGame={this.confirmDelete}
          exportGame={this.exportGame}
          importGame={this.onClickImportGame}
        />;
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} {...importing} /> }
      </React.Fragment>);
  }

  confirmDelete = (ev) => {
    ev.preventDefault();
    const { game } = this.props;
    this.setState({
      ActiveDialog: ConfirmDialog,
      dialogData: {
        changes: [
          `Delete group ${game.id}`
        ],
        title: "Confirm delete game",
        onCancel: this.cancelDialog,
        onConfirm: this.deleteGame,
      }
    });
    return false;
  };

  cancelDialog = () => {
    this.setState({
      ActiveDialog: null,
      dialogData: null,
      importType: 0,
    });
  };

  deleteGame = () => {
    const { game, dispatch, onDelete } = this.props;
    this.setState({ ActiveDialog: null, dialogData: null });
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
    this.setState({
      ActiveDialog: FileDialog,
      dialogData: {
        title: 'Select a json database file to import',
        accept: '.json,application/json',
        submit: 'Import database',
        onCancel: this.cancelDialog,
        onFileUpload: this.onFileSelected
      },
      importType: AdminGameActions.DATABASE_IMPORT
    });
  };

  onChangeReplaceDate = (e) => {
    const { dialogData } = this.state;
    this.setState({
      dialogData: {
        ...dialogData,
        replaceDate: e.target.checked
      }
    });
  }

  onClickImportGame = () => {
    const extraFields = <div className="form-control">
      <label htmlFor="replaceDate" className="replace-date-label">Replace game start date during import?</label>
      <input type="checkbox" name="replaceDate" defaultChecked onChange={this.onChangeReplaceDate}></input>
    </div>;

    this.setState({
      ActiveDialog: FileDialog,
      dialogData: {
        title: 'Select a gameTracks.json file to import',
        accept: '.json,application/json',
        submit: 'Import game',
        onCancel: this.cancelDialog,
        onFileUpload: this.onFileSelected,
        replaceDate: true,
        extraFields
      },
      importType: AdminGameActions.GAME_IMPORT
    });
  };

  importComplete = () => {
    const { databaseImporting, gameImporting, dispatch } = this.props;
    const { importType } = this.state;
    if (importType === AdminGameActions.DATABASE_IMPORT && databaseImporting?.done === true) {
        document.location.reload();
        return;
    }
    if (importType === AdminGameActions.GAME_IMPORT && gameImporting?.done === true) {
      dispatch(invalidateGames());
      dispatch(fetchGamesIfNeeded());
    }
    this.setState({
      ActiveDialog: null,
      dialogData: null,
      importType: 0,
    });
  };

  exportDatabase = () => {
    const { dispatch } = this.props;
    this.setState(() => ({
      ActiveDialog: BusyDialog,
      dialogData: {
        onClose: this.cancelDialog,
        title: "Exporting database",
        text: "Please wait, exporting database...",
      }
    }), () => {
      dispatch(api.exportDatabase()).then(response => {
        const filename = `database-${Date.now()}.json`;
        return response.payload.blob().then(blob => {
          this.setState({ ActiveDialog: null, dialogData: null });
          saveAs(blob, filename);
          return filename;
        });
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
    var reader = new FileReader();
    reader.onload = (ev) => this.onFileLoaded(file.name, ev);
    reader.onerror = (err) => {
      this.setState({ activeDialog: null, activeDialogData: null });
      addMessage({ type: "error", text: err });
    };
    reader.readAsText(file);
  };

  onFileLoaded(filename, event) {
    const { dispatch } = this.props;
    const { importType } = this.state;
    const { replaceDate } = this.state.dialogData;
    const title = importType === AdminGameActions.GAME_IMPORT ?
      `Importing game from "${filename}"` :
      `Importing database from "${filename}"`;

    this.setState({
      ActiveDialog: ProgressDialog,
      dialogData: {
        title,
        onCancel: this.cancelDialog,
        onClose: this.importComplete
      }
    });
    const data = JSON.parse(event.target.result);
    if (importType === AdminGameActions.GAME_IMPORT) {
      if (replaceDate === true && 'Games' in data) {
        const start = new Date().toISOString();
        const end = new Date(Date.now() + 12*3600000).toISOString();
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


