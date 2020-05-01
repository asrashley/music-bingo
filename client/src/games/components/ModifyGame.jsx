import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";

import { DateTimeInput, Input } from '../../components';
import { startAndEndRules } from '../rules';
import { modifyGame } from '../gamesSlice';

function toISOString(value) {
  return value ? value.toISOString() : "";
}

function ModifyGameForm({ onSubmit, game, alert }) {
  const { register, control, handleSubmit, formState, getValues, errors, setError, reset } = useForm({
    mode: 'onChange',
    defaultValues: {
      title: game.title,
      start: game.start ? new Date(game.start): null,
      end: game.end ? new Date(game.end) : null,
    },
  });
  const { isSubmitting } = formState;

  const submitWrapper = (data) => {
    const values = {
      title: data.title,
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
        defaultValue={game.start}
        formState={formState}
        label="Start time"
        name="start"
        required />
      <DateTimeInput className="end"
        register={register(startAndEndRules(getValues))}
        errors={errors}
        control={control}
        formState={formState}
        defaultValue={game.end}
        label="End time"
        name="end"
        required />
      <div className="clearfix">
        <button type="submit" className="btn btn-success login-button mr-4" onClick={handleSubmit}
          disabled={isSubmitting}>Save Changes</button>
        <button className="btn btn-danger" disabled={isSubmitting}
          onClick={reset}>Discard Changes</button>
      </div>
    </form>
  );
}

ModifyGameForm.propTypes = {
  alert: PropTypes.string,
  game: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

class ModifyGame extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    game: PropTypes.object.isRequired,
  };

  saveGameChanges = (values) => {
    const { dispatch, game } = this.props;
    return dispatch(modifyGame({
      ...game,
      ...values
    }));
  };

  render() {
    const { game } = this.props;
    const key = `${game.pk}${game.lastUpdated}`;
    return (
      <ModifyGameForm game={game} key={key}
        onSubmit={this.saveGameChanges}
        lastUpdated={game.lastUpdated} />
    );
  }
}

export {
  ModifyGame,
  ModifyGameForm
};