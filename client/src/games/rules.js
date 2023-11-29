import { isAscii } from 'validator';

export const titleRules = {
  required: true,
  validate: {
    isAscii: (value) => isAscii(value) || 'Titles can only contain ASCII text',
  }
};


export const startAndEndDateRules = (getValues) => ({
  validate: (value) => {
    if (!value) {
      return 'Required';
    }
    const { startDate, endDate } = getValues();
    if (startDate && endDate) {
      if (startDate > endDate) {
        return 'End date must be greater than start';
      }
    }
    return true;
  }
});

export const startAndEndTimeRules = (getValues) => ({
  validate: (value) => {
    if (!value) {
      return 'Required';
    }
    const { startDate, startTime, endDate, endTime } = getValues();
    if (startDate && endDate && startDate === endDate &&
      startTime && endTime && startTime > endTime) {
      return 'End time must be greater than start';
    }
    return true;
  }
});
