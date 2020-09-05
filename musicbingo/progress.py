"""
Container for storing the progress of a background thread
"""

import sys


class Progress:
    """represents the progress of a background thread"""

    def __init__(self, text: str = '', pct: float = 0.0, num_phases: int = 1) -> None:
        self._text = text
        self._pct = pct
        self._pct_text: str = ''
        self._cur_phase: int = 1
        self._num_phases = num_phases
        self.abort = False

    def get_text(self) -> str:
        """get description of progress"""
        return self._text

    def set_text(self, text: str) -> None:
        """set description of progress"""
        if text != self._text:
            self._text = text
            self.on_change_text(text)

    def on_change_text(self, text: str) -> None:
        """called when description changes"""

    text = property(get_text, set_text)

    def get_phase_percent(self) -> float:
        """Get current percentage complete of current phase"""
        return self._pct

    def set_phase_percent(self, pct: float) -> None:
        """Set current percentage complete of current phase"""
        if pct != self._pct:
            self._pct = pct
            self.on_change_phase_percent(pct)
            self.on_change_total_percent(self.total_percentage)

    def on_change_phase_percent(self, pct: float) -> None:
        """called when percentage complete of this phase changes"""

    def on_change_total_percent(self, total_percentage: float) -> None:
        """called when total percentage complete changes"""

    @property
    def total_percentage(self) -> float:
        """get total percentage complete across all phases"""
        return (
            (self._pct / float(self._num_phases) +
             (100.0 * float(self._cur_phase) / float(self._num_phases))))

    pct = property(get_phase_percent, set_phase_percent)

    def get_percentage_text(self) -> str:
        """get text description of current percentage"""
        return self._pct_text

    def set_percentage_text(self, text: str) -> None:
        """set text description of current progress"""
        if text != self._pct_text:
            self._pct_text = text
            self.on_change_percentage_text(text)

    def on_change_percentage_text(self, text: str) -> None:
        """called when percentage description changes"""

    pct_text = property(get_percentage_text, set_percentage_text)

    def get_current_phase(self) -> int:
        """Get number of current phase"""
        return self._cur_phase

    def set_current_phase(self, phase: int) -> None:
        """Set number of current phase"""
        if phase != self._cur_phase:
            self._cur_phase = phase
            self.on_change_phase(self._cur_phase, self._num_phases)

    def on_change_phase(self, cur_phase: int, num_phases: int) -> None:
        """called when current phase changes"""

    current_phase = property(get_current_phase, set_current_phase)

    def get_num_phases(self) -> int:
        """get total number of phases"""
        return self._num_phases

    def set_num_phases(self, num: int) -> None:
        """set total number of phases"""
        if num != self._num_phases:
            self._num_phases = num
            self.on_change_phase(self._cur_phase, self._num_phases)

    num_phases = property(get_num_phases, set_num_phases)


class TextProgress(Progress):
    """displays progress on console"""

    def on_change_total_percent(self, total_percentage: float) -> None:
        sys.stdout.write('\r' + 80 * ' ')
        sys.stdout.write('\r{1:0.3f}: {0}'.format(
            self._text, total_percentage))
        sys.stdout.flush()

    def on_change_phase(self, cur_phase: int, num_phases: int) -> None:
        sys.stdout.write('\n')
        sys.stdout.flush()
