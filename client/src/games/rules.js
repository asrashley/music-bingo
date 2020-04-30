import { isAscii } from 'validator';

export const validateModifyGameForm = values => {
  const errors = {};
  if (!values.title) {
    errors.title = 'Required';
  } else if (!isAscii(values.title)) {
    errors.title = 'Titles can only contain ASCII text'
  }
  if (!values.start) {
    errors.start = 'Required';
  } if (typeof(values.start) !== "string") {
    errors.start = 'Date must be stored as a string';
  }  
  if (!values.end) {
    errors.end = 'Required';
  } if (typeof (values.end) !== "string") {
    errors.end = 'Date must be stored as a string';
  }  
  if (values.start && values.end) {
    if (new Date(values.start) > new Date(values.end)) {
      errors.end = 'End must be greater than start';
    }
  }
  return errors;
};
