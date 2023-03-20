import React from 'react';
import PropTypes from 'prop-types';
import { isEqual } from "lodash";

import { ConfirmDialog } from '../../components';
import { DisplayDialogContext } from '../../components/DisplayDialog';

import { AdminActions } from '../../admin/components/AdminActions';
import { addMessage } from '../../messages/messagesSlice';
import { modifyGame } from '../gamesSlice';

import { ModifyGameForm } from './ModifyGameForm';

import { GamePropType } from '../types/Game';
import { UserOptionsPropType } from '../../user/types/UserOptions';
import { ImportingPropType } from '../../types/Importing';

function objectChanges(modified, original) {
  const changes = [];
  for (let key in modified) {
    if (!isEqual(modified[key], original[key])) {
      if (typeof (modified[key]) === "object") {
        objectChanges(modified[key], original[key]).forEach(change => changes.push(change));
      } else {
        changes.push(`Change ${key} to ${modified[key]}`);
      }
    }
  }
  return changes;
}

export class ModifyGame extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    game: GamePropType.isRequired,
    importing: ImportingPropType,
    options: UserOptionsPropType.isRequired,
    onReload: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired
  };

  static contextType = DisplayDialogContext;

  confirmSave = (values) => {
    const { dispatch, game } = this.props;
    const { closeDialog, openDialog } = this.context;
    const self = this;
    const changes = objectChanges(values, game);
    return new Promise(resolve => {
      const saveGameChanges = () => {
        closeDialog();
        dispatch(modifyGame({
          ...game,
          ...values
        }));
        dispatch(addMessage({
          type: 'success',
          text: `Changes to game "${game.id}" saved successfully`
        }));
        resolve(true);
      };
      openDialog(<ConfirmDialog
        changes={changes}
        title="Confirm change game"
        onCancel={() => {
          self.cancelDialog();
          resolve('title', { type: 'custom', message: 'save cancelled' });
        }}
        onConfirm={saveGameChanges}
      />);
    });
  };

  render() {
    const { game, onDelete, onReload, options } = this.props;
    const key = `${game.pk}${game.lastUpdated}`;
    return (
      <React.Fragment>
        <AdminActions game={game} onDelete={onDelete} />
        <ModifyGameForm game={game} key={key}
          onSubmit={this.confirmSave}
          onReload={onReload}
          options={options}
          lastUpdated={game.lastUpdated} />
      </React.Fragment>
    );
  }
}
