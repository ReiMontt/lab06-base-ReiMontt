"""Terminal-based Chopsticks view

Do not modify this file or copy-paste it into your code; simply import
`ChopsticksTerminalView` via `from view import ChopsticksTerminalView`
in your code while ensuring that `view.py` is in the same directory as
your code.

You are expected to go through and understand how the public methods
of `ChopsticksTerminalView` should be used. No need to do so for any
of the private methods.

Note that the screen is cleared whenever an invalid option is selected.

See PEP 257 (https://peps.python.org/pep-0257/) for Python docstring
conventions. Kindly note the following rule in particular:

> The docstring is a phrase ending in a period. It prescribes the function
> or method’s effect as a command (“Do this”, “Return that”), not as a
> description; e.g. don’t write “Returns the pathname …”.
"""

import os
import sys
from collections.abc import Sequence, Mapping


from required_types import PlayerId, Action, HandInfo


class ChopsticksTerminalView:
    def clear_screen(self) -> None:
        """Clear the terminal."""

        cmd = 'cls' if sys.platform in {'win32', 'cygwin', 'msys'} else 'clear'
        os.system(cmd)

    def show_round_number(self, round_number: int) -> None:
        """Print the round number on screen."""

        print(f'Round {round_number}\n')

    def show_current_player(self, pid: PlayerId) -> None:
        """Print the current player on screen."""

        print(f'Current player: Player {pid}\n')

    def show_all_hands(self,
                       all_hands: Mapping[PlayerId, Sequence[HandInfo]],
                       current_player_id: PlayerId) -> None:
        """Print the content of each player's hand on screen.

        Hands will be shown in the iteration order dictated by the underlying
        data type of the given `Mapping`.
        """

        for pid, hands in all_hands.items():
            current_player_str = ' (current)' \
                if pid == current_player_id else ''
            print(f'Player {pid}{current_player_str}:')

            for hand in hands:
                print(f'- {self._get_hand_str(hand, show_player=False)}')

            print()

    def ask_for_action(self) -> Action:
        """Ask the user for an action until a valid one is given."""

        while True:
            actions = list(Action)
            print('Actions:')
            self._print_choices([str(a) for a in actions])

            print()
            if (action := self._ask_for_choice('Select action', actions)) is None:
                self.clear_screen()
                continue

            return action

    def ask_for_tap_pair(self, sources: list[HandInfo],
                         targets: list[HandInfo]) -> tuple[HandInfo, HandInfo]:
        """Ask the user for a source-target tap pair until a valid one is given.

        The first `HandInfo` returned corresponds to the source hand (i.e., the
        "attacking" hand) while the second corresponds to the target hand (i.e.,
        the "defending" hand).

        The selection process starts from scratch on invalid input.
        """

        while True:
            target_start_num = len(sources) + 1
            self._print_tap_pair_header(sources, targets, target_start_num)

            if (source := self._ask_for_choice('Select hand to tap with',
                                               sources)) is None:
                self.clear_screen()
                continue

            if (target := self._ask_for_choice('Select target hand to tap',
                                               targets, start=target_start_num)) is None:
                self.clear_screen()
                continue

            return source, target

    def ask_for_split_source(self, sources: list[HandInfo]) -> HandInfo:
        """Ask the user for a split source until a valid one is given.

        The selection process starts from scratch on invalid input."""

        while True:
            print('Hand to split:')
            self._print_choices(self._get_hand_strs(sources))
            print()

            if (source := self._ask_for_choice('Select hand to split',
                                               sources)) is None:
                self.clear_screen()
                continue

            return source

    def ask_for_split_assignments(self,
                                  source: HandInfo,
                                  targets: list[HandInfo],
                                  ) -> tuple[HandInfo, list[HandInfo]]:
        """Ask the user for split assignments until a valid set is given.

        The first `HandInfo` returned corresponds to a _new_ `HandInfo`
        object that represents.

        Each `HandInfo` in the returned `list[HandInfo]` corresponds to
        _new_ `HandInfo` objects with their fingers up updated with
        their corresponding split assignments.

        None of the `HandInfo` arguments will be mutated.

        This method uses the `.to()` method of `HandInfo` to create new
        `HandInfo` objects and expects `.to()` to return `None` when
        an invalid number of fingers up is passed to it.

        The selection process starts from scratch on invalid input."""

        while True:
            self._print_split_assignment_header(source, targets)

            if (result := self._ask_for_valid_assignments(source, targets)) is not None:
                return result

    def show_winner(self, winner_id: PlayerId) -> None:
        """Print the winner on screen."""

        print(f'Player {winner_id} is the winner!')

    def show_draw(self) -> None:
        """Print the draw message on screen."""

        print('The game ended in a draw')

    def show_tap_no_targets(self) -> None:
        """Print the error message corresponding to not having valid tap targets.

        Requires the user to press Enter before continuing.
        """

        self._print_error('Cannot tap; no valid targets')

    def show_split_no_targets(self) -> None:
        """Print the error message corresponding to not having valid split targets.

        Requires the user to press Enter before continuing.
        """

        self._print_error('Cannot split; no valid targets')

    def _print_tap_pair_header(self, sources: Sequence[HandInfo],
                               targets: Sequence[HandInfo],
                               target_start_num: int) -> None:
        print('Hands to tap with:')
        self._print_choices(self._get_hand_strs(sources))
        print()
        print('Possible targets:')
        self._print_choices(self._get_hand_strs(targets),
                            start=target_start_num)
        print()

    def _ask_for_valid_assignments(self,
                                   source: HandInfo,
                                   targets: list[HandInfo]
                                   ) -> tuple[HandInfo, list[HandInfo]] | None:
        if (result :=
                self._ask_for_transfers_to_targets(source.fingers_up, targets)) is None:
            return None

        fingers_left, new_targets = result

        if fingers_left == source.fingers_up:
            self._print_error('Must transfer at least one finger')
            return None

        if (new_source := source.to(fingers_left)) is None:
            self._print_error(
                'Source hand must have valid number of fingers left')
            return None

        return new_source, new_targets

    def _ask_for_transfers_to_targets(self,
                                      fingers_left: int,
                                      targets: Sequence[HandInfo],
                                      ) -> tuple[int, list[HandInfo]] | None:
        new_targets: list[HandInfo] = []

        for hand in targets:
            if fingers_left > 0:
                if (fingers_to_transfer :=
                        self._ask_for_fingers_to_transfer(hand, fingers_left)) is None:
                    return None

                fingers_left -= fingers_to_transfer
                new_fingers_up = hand.fingers_up + fingers_to_transfer \
                    if not hand.is_inactive() else fingers_to_transfer

                if (new_hand := hand.to(new_fingers_up)) is None:
                    self._print_error(
                        'Number of resulting fingers must not exceed total')
                    return None

                if new_hand.is_inactive():
                    self._print_error(
                        'Number of resulting fingers must not equal total')
                    return None

                new_targets.append(new_hand)

            else:
                new_targets.append(hand)

        return fingers_left, new_targets

    def _ask_for_fingers_to_transfer(self, hand: HandInfo, fingers_left: int) -> int | None:
        try:
            fingers_to_transfer = int(
                self._input('Number of fingers to transfer to'
                            f' {self._get_hand_str(hand, show_player=False)}'
                            f' [0-{fingers_left}]: '))

            if fingers_to_transfer < 0 or fingers_to_transfer > fingers_left:
                raise ValueError()
        except ValueError:
            self._print_error('Invalid choice')
            return None
        else:
            return fingers_to_transfer

    def _print_split_assignment_header(self, source: HandInfo,
                                       targets: Sequence[HandInfo]):
        print(f'Hand to split: {self._get_hand_str(source)}')
        print()

        print('Hands to split to:')
        for hand in targets:
            print(f'- {self._get_hand_str(hand)}')
        print()

    def _ask_for_choice[T](self, msg: str, choices: list[T],
                           start: int = 1) -> T | None:
        min_choice = start
        max_choice = start + len(choices) - 1

        try:
            range_str = f'{min_choice}-{max_choice}' \
                if min_choice != max_choice else f'{min_choice}'
            inp = int(self._input(f'{msg} [{range_str}]: '))

            if inp < min_choice or inp > max_choice:
                raise ValueError()

            return choices[inp-min_choice]

        except (ValueError, IndexError):
            self._print_error('Invalid choice; pick one of'
                              f' {', '.join(str(c)
                                            for c in range(min_choice, max_choice + 1))}')

    def _print_choices(self, strs: Sequence[str], start: int = 1) -> None:
        for k, s in enumerate(strs, start=start):
            print(f'- [{k}] {s}')

    def _get_hand_str(self, hand: HandInfo, show_player: bool = True) -> str:
        player_str = f' of Player {hand.player_id}' if show_player else ''
        inactive_str = '; inactive' if hand.is_inactive() else ''

        return (f'Hand {hand.hand_id}{player_str}'
                f' ({self._get_hand_status_str(hand)}{inactive_str})')

    def _get_hand_strs(self, hands: Sequence[HandInfo]) -> list[str]:
        return [self._get_hand_str(hand) for hand in hands]

    def _get_hand_status_str(self, hand: HandInfo) -> str:
        return f'{hand.fingers_up}/{hand.total_fingers}'

    def _print_error(self, msg: str) -> None:
        print(f'\nERROR: {msg}\n')
        input('Press Enter to continue...')
        self.clear_screen()

    def _input(self, msg: str) -> str:
        return input(msg).strip()
