import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";
import log from 'loglevel';

import { DateTimeInput, Input, SelectInput } from '../../components';
import { startAndEndRules } from '../rules';
import { GamePropType } from '../types/Game';
import { UserOptionsPropType } from '../../user/types/UserOptions';

function toISOString(value) {
  if (!value) {
    return "";
  }
  const iso = value.toISOString();
  const re = /([.]\d+Z)$/;
  return iso.replace(re, 'Z');
}

export function ModifyGameForm({ onSubmit, onReload, game, alert, options }) {
    const gameStart = game.start ? new Date(game.start) : null;
    const gameEnd = game.start ? new Date(game.end) : null;
    const defaultValues = {
        title: game.title,
        start: gameStart,
        end: gameEnd,
        colour: game.options.colour_scheme,
        artist: game.options.include_artist
    };
    const { register, control, handleSubmit, formState, getValues, errors, setError, reset } = useForm({
        mode: 'onChange',
        defaultValues,
    });
    const { isSubmitting } = formState;

    const submitWrapper = (data) => {
        const values = {
            title: data.title,
            start: toISOString(data.start),
            end: toISOString(data.end),
            options: {
                include_artist: data.artist,
                colour_scheme: data.colour
            }
        };
        log.debug(`Submit form  ${JSON.stringify(values)}`);
        return onSubmit(values).then((name, err) => {
            if (name !== true) {
                setError(name, err);
            }
        });
    };
    return (
        <form onSubmit={handleSubmit(submitWrapper)} className="modify-game border">
            <button className="btn btn-light refresh-icon btn-sm" onClick={onReload}>&#x21bb;</button>
            {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
            <Input
                type="text"
                className="title"
                label="Title"
                register={register}
                errors={errors}
                formState={formState}
                hint="Title for this round"
                name="title"
                required />
            <DateTimeInput
                className="start"
                register={register}
                rules={startAndEndRules(getValues)}
                errors={errors}
                control={control}
                defaultValue={gameStart}
                formState={formState}
                label="Start time"
                name="start"
                required />
            <DateTimeInput
                className="end"
                register={register}
                rules={startAndEndRules(getValues)}
                errors={errors}
                control={control}
                formState={formState}
                defaultValue={gameEnd}
                label="End time"
                name="end"
                required />
            <SelectInput
                className="colour"
                label="Colour Scheme"
                options={options.colourSchemes}
                register={register}
                errors={errors}
                formState={formState}
                hint="Colour scheme for this round"
                name="colour" />
            <Input
                type="checkbox"
                label="Include Artist"
                name="artist"
                errors={errors}
                formState={formState}
                register={register} />
            <div className="clearfix">
                <button type="submit" className="btn btn-success login-button mr-4"
                    disabled={isSubmitting}>Save Changes</button>
                <button
                    type="button"
                    className="btn btn-warning mr-4"
                    disabled={isSubmitting}
                    name="reset"
                    onClick={() => reset(defaultValues)}
                >Discard Changes</button>
            </div>
        </form>
    );
}

ModifyGameForm.propTypes = {
  alert: PropTypes.string,
  game: GamePropType.isRequired,
  options: UserOptionsPropType.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onReload: PropTypes.func.isRequired,
};

