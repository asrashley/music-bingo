import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";
import log from 'loglevel';

import { Input, SelectInput } from '../../components';
import { startAndEndDateRules, startAndEndTimeRules } from '../rules';
import { GamePropType } from '../types/Game';
import { UserOptionsPropType } from '../../user/types/UserOptions';

function toISOString(date, time) {
    if (!date && !time) {
        return "";
    }
    if (!time) {
        return `${date}T00:00:00Z`;
    }
    if (time.length === 5) {
        return `${date}T${time}:00Z`;
    }
    return `${date}T${time}Z`;
}

function splitDateTime(dateTime) {
    if (!dateTime) {
        return [null, null];
    }
    return [dateTime.slice(0, 10), dateTime.slice(11, 16)];
}

export function ModifyGameForm({ onSubmit, onReload, game, alert, options }) {
    const [startDate, startTime] = splitDateTime(game.start);
    const [endDate, endTime] = splitDateTime(game.end);
    const defaultValues = {
        title: game.title,
        startDate,
        startTime,
        endDate,
        endTime,
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
            start: toISOString(data.startDate, data.startTime),
            end: toISOString(data.endDate, data.endTime),
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
            <button
                data-testid="refresh-game-button"
                className="btn btn-light refresh-icon btn-sm"
                onClick={onReload}>&#x21bb;</button>
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
            <div className="form-group row">
                <Input
                    type="date"
                    className="start"
                    groupClassName="col-5"
                    register={register}
                    rules={startAndEndDateRules(getValues)}
                    errors={errors}
                    control={control}
                    defaultValue={startDate}
                    formState={formState}
                    label="Start Date"
                    name="startDate"
                    required />
                <Input
                    type="time"
                    className="start"
                    groupClassName="col-5"
                    register={register}
                    rules={startAndEndTimeRules(getValues)}
                    errors={errors}
                    control={control}
                    defaultValue={startTime}
                    formState={formState}
                    label="Start Time"
                    name="startTime"
                    required />
            </div>
            <div className="form-group row">
                <Input
                    type="date"
                    className="end"
                    groupClassName="col-5"
                    register={register}
                    rules={startAndEndDateRules(getValues)}
                    errors={errors}
                    control={control}
                    defaultValue={endDate}
                    formState={formState}
                    label="End Date"
                    name="endDate"
                    required />
                <Input
                    type="time"
                    className="end"
                    groupClassName="col-5"
                    register={register}
                    rules={startAndEndTimeRules(getValues)}
                    errors={errors}
                    control={control}
                    defaultValue={endTime}
                    formState={formState}
                    label="End Time"
                    name="endTime"
                    required />
            </div>
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

