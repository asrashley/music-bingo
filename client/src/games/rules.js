import { isAscii } from 'validator';

export const titleRules = {
  required: true,
  validate: {
    isAscii: (value) => isAscii(value) || 'Titles can only contain ASCII text',
  }
};

export const startAndEndRules = (getValues) => ({
  validate: (value) => {
    if (!value) {
      return 'Required';
    }
    const { start, end } = getValues();
    if (start && end) {
      if (start >= end) {
        return 'End must be greater than start';
      }
    }
    return true;
  }
});
