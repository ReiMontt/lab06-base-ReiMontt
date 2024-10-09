from required_types import PlayerId, HandId, Action, HandInfo


class ChopsticksHand(HandInfo):
    def __init__(self, player_id: PlayerId, hand_id: HandId, total_fingers: int):
        self._player_id = player_id
        self._hand_id = hand_id
        self._fingers_up = 1  # Hands start with 1 finger up
        self._total_fingers = total_fingers

    @property
    def hand_id(self) -> HandId:
        return self._hand_id

    @property
    def player_id(self) -> PlayerId:
        return self._player_id

    @property
    def fingers_up(self) -> int:
        return self._fingers_up

    @property
    def total_fingers(self) -> int:
        return self._total_fingers

    def is_active(self) -> bool:
        # A hand is active if it has between 1 and total_fingers - 1 fingers up
        return 0 < self._fingers_up < self._total_fingers

    def is_inactive(self) -> bool:
        return not self.is_active()

    def to(self, fingers_up: int) -> HandInfo | None:
        # Update fingers up with a valid number between 0 and total_fingers
        if 0 <= fingers_up <= self._total_fingers:
            new_hand = ChopsticksHand(self._player_id, self._hand_id, self._total_fingers)
            new_hand._fingers_up = fingers_up
            return new_hand
        return None

    def tap(self, target: HandInfo) -> HandInfo:
        # Perform a tap action, summing the current hand's fingers with the target hand's
        new_fingers_up = (target.fingers_up + self.fingers_up) % target.total_fingers
        return target.to(new_fingers_up) or target


class Player:
    def __init__(self, player_id: PlayerId, num_hands: int, total_fingers: int):
        self._player_id = player_id
        # Initialize hands, using hand IDs starting from 1
        self.hands = [ChopsticksHand(player_id, HandId(i + 1), total_fingers) for i in range(num_hands)]

    def is_active(self) -> bool:
        # A player is active if at least one of their hands is active
        return any(hand.is_active() for hand in self.hands)

    def get_active_hands(self) -> list[HandInfo]:
        # Return a list of all active hands
        return [hand for hand in self.hands if hand.is_active()]

    def get_all_hands(self) -> list[HandInfo]:
        # Return all hands (active or inactive)
        return self.hands

    def update_hand(self, hand: HandInfo) -> None:
        # Update a specific hand by its hand_id with new hand state
        for i, h in enumerate(self.hands):
            if h.hand_id == hand.hand_id:
                self.hands[i] = hand
                break


class ChopsticksGame:
    def __init__(self, num_players: int, num_hands: int, total_fingers: int):
        # Initialize players, using player IDs starting from 1
        self.players = [Player(PlayerId(i + 1), num_hands, total_fingers) for i in range(num_players)]
        self.total_fingers = total_fingers
        self.current_round = 0  # The game starts at round 0
        self.winner = None

    def get_current_player(self) -> Player:
        # Get the player whose turn it is
        return self.players[self.current_round % len(self.players)]

    def next_player(self) -> Player:
        # Move to the next player's turn
        self.current_round += 1
        return self.players[self.current_round % len(self.players)]

    def tap(self, source_hand: HandInfo, target_hand: HandInfo) -> None:
        # Update the target hand after a tap
        target_player = self.players[target_hand.player_id - 1]
        new_hand = source_hand.tap(target_hand)
        target_player.update_hand(new_hand)

    def split(self, source_hand: HandInfo, target_hand: HandInfo, transfer_fingers: int) -> None:
        # Split the fingers between two hands
        if source_hand.fingers_up >= transfer_fingers:
            new_source_hand = source_hand.to(source_hand.fingers_up - transfer_fingers)
            new_target_hand = target_hand.to(target_hand.fingers_up + transfer_fingers)
            current_player = self.players[source_hand.player_id - 1]
            current_player.update_hand(new_source_hand)
            current_player.update_hand(new_target_hand)

    def is_game_over(self) -> bool:
        # The game is over if there is only one active player remaining
        active_players = [player for player in self.players if player.is_active()]
        return len(active_players) == 1

    def get_winner(self) -> PlayerId | None:
        # If the game is over, return the player ID of the winner
        if self.is_game_over():
            for player in self.players:
                if player.is_active():
                    return player._player_id
        return None
