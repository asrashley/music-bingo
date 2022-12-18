
const utcFields = ['getUTCHours', 'getUTCMinutes',
  'getUTCSeconds', 'getUTCDate',
  'getUTCMonth', 'getUTCFullYear'];

const localFields = utcFields.map(f => f.replace('UTC', ''));

export const DateTime = ({ date, useUTC = false, withTimezone = false, withDate = true, withTime = true, ...params }) => {
  if (typeof (date) === "string" || typeof(date) === "number") {
    date = new Date(date);
  };
  let fields = (useUTC === false) ? localFields : utcFields;
  fields = fields.map((f) => {
    const val = date[f]();
    if (/Year/.test(f)) {
      return `${val}`;
    }
    if (/Month/.test(f)) {
      return `0${val + 1}`.slice(-2);
    }
    return `0${val}`.slice(-2);
  });
  let tz = '';
  if (withTimezone === true) {
    if (useUTC === false) {
      const offset = date.getTimezoneOffset();
      if (offset === 0) {
        tz = ' GMT';
      } else {
        tz = ' BST';
      }
    } else {
      tz = ' UTC';
    }
  }
  const time = withTime ? `${fields[0]}:${fields[1]}:${fields[2]}` : '';
  const dstr = withDate ? `${fields[3]}/${fields[4]}/${fields[5]}` : '';
  if (!withTime) {
    tz = '';
  }
  return `${time} ${dstr} ${tz}`;
};
