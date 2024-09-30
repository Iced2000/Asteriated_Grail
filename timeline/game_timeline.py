GameTimeline = {
    "game_initialization": [
        'on_game_initialization',
    ],
    "before_round_start": [
        'on_before_round_start',
    ],
    "round_start_phase": [
        'on_round_start_phase',
    ],
    "before_action_phase": [
        'on_before_action_phase',
        *[f'poison_trigger_player_{i}' for i in range(1, 7)],
        *[f'weakness_trigger_player_{i}' for i in range(1, 7)],
    ],
    "action_phase_start": [
        'on_action_phase_start',
    ],
    "during_action_phase": [
        'on_during_action_phase',
    ],
    "after_action_phase": [
        *[f'on_after_action_phase_player_{i}' for i in range(1, 7)],
    ],
    "turn_end_phase": [
        'on_turn_end_phase',
        *[f'reset_actions_player_{i}' for i in range(1, 7)],
    ],
}