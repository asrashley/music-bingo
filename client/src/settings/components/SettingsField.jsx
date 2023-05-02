import React from 'react';
import PropTypes from 'prop-types';

import { Input, SelectInput } from '../../components';
import { SettingsFieldPropType } from '../types/SettingsField';

export default function SettingsField({
  field, formState, isSubmitting, register
}) {
  const { help, name, title, type } = field;
  const rules = {
    validate: {}
  };
  let inputType = "text";
  if (type === 'int') {
    inputType = 'number';
    rules.validate = {
      minValue: (v) => (field.minValue === null || v >= field.minValue) || `Minimum value is ${field.minValue}`,
      maxValue: (v) => (field.maxValue === null || v <= field.maxValue) || `Maximum value is ${field.maxValue}`
    };
  } else if (type === 'bool') {
    inputType = 'checkbox';
  }

  return (
    <div className={`border settings-field ${name}`}>
      <div className="setting-name"><label htmlFor={`field-${name}`}>{title}</label></div>
      <div className="setting-edit">
        {(type === 'enum') ? (
          <SelectInput
            name={name}
            type="text"
            hint={help}
            register={register}
            formState={formState}
            options={field.choices}
            disabled={isSubmitting}
          />
        ) : (
          <Input
            name={name}
            type={inputType}
            hint={help}
            register={register}
            rules={rules}
            formState={formState}
            disabled={isSubmitting}
          />
        )}
      </div>
    </div>
  );
}

SettingsField.propTypes = {
  field: SettingsFieldPropType.isRequired,
  formState: PropTypes.object.isRequired,
  isSubmitting: PropTypes.bool,
  register: PropTypes.func.isRequired,
};
