
const utcFields = ['getUTCHours', 'getUTCMinutes',
  'getUTCSeconds', 'getUTCDate',
  'getUTCMonth', 'getUTCFullYear'];

const localFields = utcFields.map(f => f.replace('UTC', ''));

export const DateTime = ({
  date,
  useUTC = false,
  withTimezone = false,
  withDate = true,
  withTime = true,
  ampm = false,
  ...params }) => {
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
  const result = [];
  if (withTime) {
    let postfix = '';
    if (ampm === true) {
      postfix = fields[0] >= 12 ? ' pm' : ' am';
      fields[0] = parseInt(fields[0]) % 12;
      if (fields[0] === 0) {
        fields[0] = 12;
      }
    }
    result.push(`${fields[0]}:${fields[1]}:${fields[2]}${postfix}`);
  }
  if (withDate) {
    result.push(`${fields[3]}/${fields[4]}/${fields[5]}`);
  }
  if (withTimezone === true && withTime) {
    let tz = '';
    if (useUTC === false) {
      const offset = date.getTimezoneOffset();
      if (offset === 0) {
        tz = 'GMT';
      } else {
        tz = 'BST';
      }
    } else {
      tz = 'UTC';
    }
    result.push(tz);
  }
  return result.join(' ');
};

export function formatDuration(ms_dur) {
  let seconds = Math.floor(ms_dur / 1000);
  const digit = Math.floor(ms_dur / 100) % 10;
  let minutes = Math.floor(seconds / 60) % 60;
  const hours = Math.floor(seconds / 3600);
  seconds = seconds % 60;
  seconds = `0${seconds}`.slice(-2);
  minutes = `0${minutes}`.slice(-2);
  if (hours) {
    return `${hours}:${minutes}:${seconds}.${digit}`;
  }
  return `${minutes}:${seconds}.${digit}`;
}