import React from 'react';
import PropTypes from 'prop-types';
import { reduxForm, Field, SubmissionError } from 'redux-form';

import { DateTimeInput, Input } from '../../components';
import { validateModifyGameForm } from '../rules';
import { modifyGame } from '../gamesSlice';

const toISOString = value => value ? value.toISOString() : "";

class ModifyGameForm extends React.Component {
  static propTypes = {
    alert: PropTypes.string,
    handleSubmit: PropTypes.func.isRequired,
    submitting: PropTypes.bool,
    pristine: PropTypes.bool,
    valid: PropTypes.bool,
  };

  render() {
    const { alert, handleSubmit, submitting, pristine, valid, reset, load, lastUpdated} = this.props;
    return (
      <form onSubmit={handleSubmit} data-updated={lastUpdated}
        className={`modify-game border ${pristine ? '' : 'off-was-validated'}`}>
        {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
        <Field type="text" className="title"
          component={Input}
          label="Title"
          hint="Title for this round"
          name="title" required />
        <Field className="start"
          component={DateTimeInput}
          label="Start time"
          name="start"
          normalize={toISOString}
          required />
        <Field className="end"
          component={DateTimeInput}
          label="End time"
          name="end"
          normalize={toISOString}
          required />
        <div className="clearfix">
          <button type="submit" className="btn btn-success login-button mr-4" onClick={handleSubmit}
            disabled={pristine || submitting || !valid}>Save Changes</button>
          <button className="btn btn-danger" disabled={pristine || submitting}
            onClick={reset}>Discard Changes</button>
        </div>
      </form>
    );
  }
}

ModifyGameForm = reduxForm({
  form: 'ModifyGame',
  validate: validateModifyGameForm,
})(ModifyGameForm);

class ModifyGame extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    game: PropTypes.object.isRequired,
  };

  saveGameChanges = (values) => {
    const { dispatch, game } = this.props;
    dispatch(modifyGame({
      ...game,
      ...values
    }));
  };

  render() {
    const { game } = this.props;
    return (
        <ModifyGameForm initialValues={game}
          onSubmit={this.saveGameChanges}
          lastUpdated={game.lastUpdated} />
    );
  }
}

export {
  ModifyGame,
  ModifyGameForm
};