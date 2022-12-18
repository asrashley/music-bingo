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

function HorizontalPopularityGraph({popularity, onRotate}) {
  return (
    <table className="horiz-popularity-graph">
      <thead>
        <tr>
          <th className="title">Theme</th>
          <th className="count">Popularity
            <button className="btn btn-light rotate-icon" onClick={onRotate}>&nbsp;</button>
          </th>
        </tr>
      </thead>
      <tbody>
        {popularity.map((theme, idx) => <ThemeRow key={idx} index={idx} theme={theme} />)}
      </tbody>
    </table>
  );
}

function Bar({theme, index, scale}) {
  const barStyle = {
    height: `${100 * theme.count / theme.maxCount}%`,
    backgroundColor: colours[index % colours.length],
  };
  const nameStyle = {
    color: colours[index % colours.length],
  };
  const themeStyle = {
    fontSize: `${scale}em`
  };
  return (
    <div className="theme" style={themeStyle}>
      <div className="bar-wrap"><div className="bar" style={barStyle}>{theme.count}</div></div>
      <div className="name" style={nameStyle}>{theme.title}</div>
    </div>
  );
}

function VerticalPopularityGraph({popularity, onRotate}) {
  const scale = popularity.length > 30 ? (45 / popularity.length) : 1.0;
  return (
    <div className="vert-popularity-graph">
      <button className="btn btn-light rotate-icon" onClick={onRotate}>&nbsp;</button>
      {popularity.map((theme, idx) =>
                      <Bar
                        key={idx}
                        index={idx}
                        theme={theme}
                        scale={scale}
                        length={popularity.length}
                      />)}
    </div>
  );
}

export class PopularityGraph extends React.Component {
  static propTypes = {
    popularity: PropTypes.array.isRequired,
    toggleOrientation: PropTypes.func.isRequired,
  };

  render() {
    const { popularity, toggleOrientation, options } = this.props;
    if (options.vertical) {
      return <VerticalPopularityGraph popularity={popularity}
                                      onRotate={toggleOrientation}/>;
    }
    return <HorizontalPopularityGraph popularity={popularity}
                                      onRotate={toggleOrientation}/>;
  }
}
