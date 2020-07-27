import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";
import { saveAs } from 'file-saver';

import { ConfirmDialog, DateTimeInput, Input, SelectInput } from '../../components';

import { startAndEndRules } from '../rules';
import { modifyGame, deleteGame } from '../gamesSlice';
import { api } from '../../endpoints';

function toISOString(value) {
  return value ? value.toISOString() : "";
}

function ModifyGameForm({ onSubmit, onReload, game, alert, options }) {
  const gameStart = game.start ? new Date(game.start) : null;
  const gameEnd = game.start ? new Date(game.end) : null;
  const { register, control, handleSubmit, formState, getValues, errors, setError, reset } = useForm({
    mode: 'onChange',
    defaultValues: {
      title: game.title,
      start: gameStart,
      end: gameEnd,
      colour: game.options.colour_scheme,
    },
  });
  const { isSubmitting } = formState;

  const submitWrapper = (data) => {
    const values = {
      title: data.title,
      colour_scheme: data.colour,
      start: toISOString(data.start),
      end: toISOString(data.end),
    };
    return onSubmit(values).then(result => {
      if (result !== true) {
        setError(result);
      }
    });
  };
  return (
    <form onSubmit={handleSubmit(submitWrapper)} className="modify-game border">
      <button className="btn btn-light refresh-icon btn-sm" onClick={onReload}>&#x21bb;</button>
      {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
      <Input
        type="text"
        className="title"
        label="Title"
        register={register}
        errors={errors}
        formState={formState}
        hint="Title for this round"
        name="title" required />
      <DateTimeInput className="start"
        register={register(startAndEndRules(getValues))}
        errors={errors}
        control={control}
        defaultValue={gameStart}
        formState={formState}
        label="Start time"
        name="start"
        required />
      <DateTimeInput className="end"
        register={register(startAndEndRules(getValues))}
        errors={errors}
        control={control}
        formState={formState}
        defaultValue={gameEnd}
        label="End time"
        name="end"
        required />
      <SelectInput
        className="colour"
        label="Colour Scheme"
        options={options.colourSchemes}
        register={register}
        errors={errors}
        formState={formState}
        hint="Colour scheme for this round"
        name="colour"  />
      <div className="clearfix">
        <button type="submit" className="btn btn-success login-button mr-4" onClick={handleSubmit}
          disabled={isSubmitting}>Save Changes</button>
        <button className="btn btn-warning mr-4" disabled={isSubmitting}
          onClick={reset}>Discard Changes</button>
      </div>
    </form>
  );
}

ModifyGameForm.propTypes = {
  alert: PropTypes.string,
  game: PropTypes.object.isRequired,
  options: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onReload: PropTypes.func.isRequired,
};

class ModifyGame extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    game: PropTypes.object.isRequired,
    options: PropTypes.object.isRequired,
    onDelete: PropTypes.func.isRequired,
    onReload: PropTypes.func.isRequired,
  };

  state = {
    ActiveDialog: null,
    dialogData: null,
    error: null,
  };

  confirmSave = (values) => {
    const { dispatch, game } = this.props;
    const self = this;
    const changes = [];
    for (let key in values) {
      if (values[key] !== game[key]) {
        changes.push(`Change ${key} to ${values[key]}`);
      }
    }
    return new Promise(resolve => {
      const saveGameChanges = () => {
        self.setState({ ActiveDialog: null, dialogData: null });
        resolve(dispatch(modifyGame({
          ...game,
          ...values
        })));
      };
      self.setState({
        ActiveDialog: ConfirmDialog,
        dialogData: {
          changes,
          title: "Confirm change game",
          onCancel: () => {
            self.cancelDialog();
            resolve(false);
          },
          onConfirm: saveGameChanges,
        }
      });
    });
  };

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
    this.setState({ ActiveDialog: null, dialogData: null });
  };

  deleteGame = () => {
    const { game, dispatch, onDelete } = this.props;
    this.setState({ ActiveDialog: null, dialogData: null });
    dispatch(deleteGame(game)).then(result => {
      if (result === true) {
        return onDelete(game);
      }
      this.setState({ error: result.error });
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
  }

  render() {
    const { game, onReload, options } = this.props;
    const { ActiveDialog, dialogData, error } = this.state;

    const key = `${game.pk}${game.lastUpdated}`;
    return (
      <React.Fragment>
        {error && <div className="alert alert-warning"
          role="alert"><span className="error-message">{error}</span></div>}
        <ModifyGameForm game={game} key={key}
          onSubmit={this.confirmSave}
          onReload={onReload}
          options={options}
          lastUpdated={game.lastUpdated} />
        <div class="action-panel">
          <button className="btn btn-primary ml-2" 
             onClick={this.exportGame}>Export game
          </button>   
          <button className="btn btn-danger ml-2" 
             onClick={this.confirmDelete}>Delete game
          </button>
        </div>  
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} />}
      </React.Fragment>
    );
  }
}

export {
  ModifyGame,
  ModifyGameForm
};
