GameTimeline = {
    "game_initialization": [
        '_on_game_initialization',
    ],
    "before_round_start": [
        '_on_before_round_start',
    ],
    "round_start_phase": [
        '_on_round_start_phase',
    ],
    "before_action_phase": [
        '_on_before_action_phase',
        '_poison_trigger',
        '_weakness_trigger',
    ],
    "action_phase_start": [
        '_on_action_phase_start',
    ],
    "during_action_phase": [
        '_on_during_action_phase',
    ],
    "after_action_phase": [
        '_on_after_action_phase',
    ],
    "turn_end_phase": [
        '_on_turn_end_phase',
    ],
}