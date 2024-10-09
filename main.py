from model import ChopsticksGame
from view import ChopsticksTerminalView
from required_types import Action
import sys

def main():
    players = int(sys.argv[1])  # Number of players
    hands = int(sys.argv[2])    # Number of hands per player
    fingers = int(sys.argv[3])  # Total fingers per hand

    game = ChopsticksGame(players, hands, fingers)
    view = ChopsticksTerminalView()

    while not game.is_game_over():
        current_player = game.get_current_player()
        
        if not current_player.is_active():
            game.next_player()
            continue

        view.clear_screen()
        
        # Rounds start from 1 instead of 0
        view.show_round_number(game.current_round)

        # Show current player as player number starting from 1
        view.show_current_player(current_player._player_id)

        # Display all players' hands (Player numbers also start from 1)
        view.show_all_hands({p._player_id: p.get_all_hands() for p in game.players},
                            current_player._player_id )

        # Ask for action (TAP or SPLIT)
        action = view.ask_for_action()

        if action == Action.TAP:
            # Ask for source and target hands
            source_hand, target_hand = view.ask_for_tap_pair(current_player.get_active_hands(),
                                                             [hand for p in game.players
                                                              if p != current_player
                                                              for hand in p.get_active_hands()])
            # Perform the tap action
            new_target_hand = source_hand.tap(target_hand)
            target_hand = new_target_hand

        elif action == Action.SPLIT:
            # Ask for the source hand for splitting
            source_hand = view.ask_for_split_source(current_player.get_active_hands())
            
            # Get the hands eligible to receive the split
            targets = [hand for hand in current_player.get_all_hands() if hand != source_hand]
            
            # Ask for how to split fingers
            new_source_hand, new_target_hands = view.ask_for_split_assignments(source_hand, targets)
            source_hand = new_source_hand

        # Proceed to the next player
        game.next_player()

    # Display winner or draw at the end of the game
    winner = game.get_winner()
    if winner:
        view.show_winner(winner)  # Winner displayed as Player 1, 2, etc.
    else:
        view.show_draw()

if __name__ == "__main__":
    main()
