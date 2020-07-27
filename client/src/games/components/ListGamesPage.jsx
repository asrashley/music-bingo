import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { BingoGamesTable } from './BingoGamesTable';
import { FileDialog, ProgressDialog } from '../../components';

import { getUser } from '../../user/userSelectors';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, importGame, invalidateGames } from '../gamesSlice';
import { addMessage } from '../../messages/messagesSlice';

import {
  getActiveGamesList, getPastGamesOrder, getImporting
} from '../gamesSelectors';

import '../styles/games.scss';

import routes from '../../routes';
import { initialState } from '../../app/initialState';

function ActionPanel({onClickImport}) {
  return (
    <div class="action-panel">
      <button className="btn btn-primary" onClick={onClickImport}>
        Import a game
      </button>
    </div>
  );
}

class ListGamesPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: PropTypes.object.isRequired,
    games: PropTypes.array,
    pastGames: PropTypes.array,
  };

  state = {
    ActiveDialog: null,
    dialogData: null,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()));
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  onReload = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  }

  onClickImport = () => {
    this.setState({
      ActiveDialog: FileDialog,
      dialogData: {
        title: 'Select a gameTracks.json file',
        accept: '.json,application/json',
        submit: 'Import game',
        onCancel: this.cancelDialog,
        onFileUpload: this.onFileUpload
      }
    });
  }

  cancelDialog = () => {
    this.setState({
      ActiveDialog: null,
      dialogData: null
    });
  }

  onFileUpload = (file) => {
    var reader = new FileReader();
    reader.onload = this.onFileLoaded.bind(this, file.name);
    reader.onerror = (err) => {
      this.setState({ activeDialog: null, activeDialogData: null });
      addMessage({ type: "error", text: err });
    };
    reader.readAsText(file);
  }

  onFileLoaded(filename, event) {
    const { dispatch } = this.props;

    this.setState({
      ActiveDialog: ProgressDialog,
      dialogData: {
        title: `Importing game from "${filename}"`,
        onClose: this.cancelDialog
      }
    });
    const data = JSON.parse(event.target.result);
    dispatch(importGame(filename, data));
  }

  render() {
    const { games, user, pastOrder, importing } = this.props;
    const { ActiveDialog } = this.state;
    let { dialogData } = this.state;
    let text = 'If you are feeling nostalgic, why not browe the ';
    if (games.length === 0) {
      text = 'There are no upcoming Bingo games, but in the meantime you could browse the';
    }
    if (ActiveDialog === ProgressDialog) {
      dialogData = {
        ...dialogData,
        ...importing
      };
    }
    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        {(user.groups.admin === true) && <ActionPanel onClickImport={this.onClickImport} />}
        <BingoGamesTable games={games} onReload={this.onReload}
          title="Available Bingo games" />
        {pastOrder.length > 0 && <p>{text}
          <Link to={reverse(`${routes.pastGames}`)} > list of previous Bingo rounds</Link></p>}
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
    games: getActiveGamesList(state),
    pastOrder: getPastGamesOrder(state),
    importing: getImporting(state),
  };
};

ListGamesPage = connect(mapStateToProps)(ListGamesPage);

export {
  ListGamesPage
};
