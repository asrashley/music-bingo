import { titleRules, startAndEndRules } from './rules';

function applyRule(rule, value) {
  if (typeof (rule.validate) === 'function') {
    return rule.validate(value);
  }
  for (let key in rule.validate) {
    const rv = rule.validate[key](value);
    if (rv !== true) {
      return rv;
    }
  }
  return true;
}

describe('Games input field rules', () => {
  it('checks title only has ascii characters', () => {
    expect(applyRule(titleRules, 'the quick brown fox')).toBe(true);
    expect(applyRule(titleRules, 'with number 123')).toBe(true);
    const tdec = new TextDecoder();
    const u8arr = new Uint8Array([240, 160, 174, 183]);
    const unicode = tdec.decode(u8arr);
    expect(applyRule(titleRules, unicode)).toBe('Titles can only contain ASCII text');
  });

  it('checks game start and end times', () => {
    expect(applyRule(startAndEndRules(() => null), null)).toBe('Required');
    expect(applyRule(startAndEndRules(() => ({start:2, end: 5})), 2)).toBe(true);
    expect(applyRule(startAndEndRules(() => ({ start: 2, end: 5 })), 5)).toBe(true);
    expect(applyRule(startAndEndRules(() => ({ start: 2, end: null })), 5)).toBe(true);
    expect(applyRule(startAndEndRules(() => ({ start: null, end: 5 })), 5)).toBe(true);
    expect(applyRule(startAndEndRules(() => ({ start: 5, end: 2 })), 5)).toBe("End must be greater than start");
  });
});