import React from 'react';
import PropTypes from 'prop-types';

import '../styles/games.scss';

const colours = [
  '#FF0000',
  '#008000',
  '#00EFEF',
  '#808000',
  '#BFBF00',
  '#808080',
  '#008080',
  '#00EF00',
  '#C0C0C0',
  '#800000',
  '#0000FF',
  '#000080',
  '#FF00FF',
  '#800080',
];

function ThemeRow({index, theme}) {
  const style = {
    width: `${100 * theme.count / theme.maxCount}%`,
    backgroundColor: colours[index % colours.length],
  };
  return (
    <tr className="theme">
      <td className="title" style={{color: colours[index % colours.length]}}>{theme.title}</td>
      <td className="count"><div className="bar" style={style}>{theme.count}</div> </td>
    </tr>
  );
}

function HorizontalPopularityGraph({popularity}) {
  return (
    <table className="horiz-popularity-graph">
      <thead><tr><th className="title">Theme</th><th className="count">Popularity</th></tr></thead>
      <tbody>
        {popularity.map((theme, idx) => <ThemeRow key={idx} index={idx} theme={theme} />)}
      </tbody>
    </table>
  );
}

function Bar({theme, index}) {
  const barStyle = {
    height: `${100 * theme.count / theme.maxCount}%`,
    backgroundColor: colours[index % colours.length],
  };
  const nameStyle = {
    color: colours[index % colours.length],
  };
  return (
    <div className="theme">
      <div className="bar-wrap"><div className="bar" style={barStyle}>{theme.count}</div></div>
      <div className="name" style={nameStyle}>{theme.title}</div>
    </div>
  );
}

function VerticalPopularityGraph({popularity}) {
  return (
    <div className="vert-popularity-graph">
      {popularity.map((theme, idx) => <Bar key={idx} index={idx} theme={theme} />)}
    </div>
  );
}

export class PopularityGraph extends React.Component {
  static propTypes = {
    popularity: PropTypes.array.isRequired,
  };

  state = {
    vertical: true,
  };

  render() {
    const { vertical } = this.state;
    const { popularity } = this.props;
    if (vertical) {
      return <VerticalPopularityGraph popularity={popularity}/>;
    }
    return <HorizontalPopularityGraph popularity={popularity} />;
  }
}
