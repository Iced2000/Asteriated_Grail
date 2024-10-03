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
        'poison_trigger',
        'weakness_trigger',
    ],
    "action_phase_start": [
        'on_action_phase_start',
    ],
    "during_action_phase": [
        'on_during_action_phase',
    ],
    "after_action_phase": [
        'on_after_action_phase',
    ],
    "turn_end_phase": [
        'on_turn_end_phase',
    ],
}