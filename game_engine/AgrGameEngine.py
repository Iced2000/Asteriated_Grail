# game_engine/AgrGameEngine.py

from models.Player import Player
from models.Team import Team
from models.Deck import Deck
from models.Effect import HolyShieldEffect
from views.ConsoleInterface import LocalConsoleInterface, NetworkedConsoleInterface
from models.Action import (HolyLightCardAction, NoResponseAction, 
                           CounterCardAction, MagicBulletCounterCardAction)
from game_engine.EventManager import EventManager
from timeline import GameTimeline, DamageTimeline
from factories.character_factory import CharacterFactory


class AgrGameEngine:
    def __init__(self, config):
        self._networked = config.get('networked', False)
        if self._networked:
            self._interface = NetworkedConsoleInterface(game_server=config.get('game_server', None), 
                                                        debug=config.get('debug', False))
        else:
            self._interface = LocalConsoleInterface(debug=config.get('debug', False))
        self._event_manager = EventManager(self._interface)
        self._setup_game(config)
        self._current_turn = 0
        self._running = True
        self._setup_event_handlers()

    def _setup_game(self, config):
        # Initialize teams
        self._red_team = Team(is_red=True, game_engine=self)
        self._blue_team = Team(is_red=False, game_engine=self)
        
        # Initialize single deck
        self._deck = Deck(config['deck_path'], interface=self._interface)
        
        # Initialize players
        self._players = []
        for player_config in config['player']:
            team = self._red_team if player_config['team'] == 'red' else self._blue_team
            character_config = {
                'character_type': player_config['character_type'],
                'player_id': player_config['pid'],
                'team': team,
                'game_engine': self
            }
            player = CharacterFactory.create_character(character_config)
            player.draw_initial_hand()
            self._players.append(player)
            team.add_player(player)
        
        self._red_team.add_jewel(3, 2)
        self._blue_team.add_jewel(3, 2)

    def _setup_event_handlers(self):
        for event_type, handlers in GameTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self._event_manager.subscribe(event_type, handler, priority=priority, name=handler_name)

        for event_type, handlers in DamageTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self._event_manager.subscribe(event_type, handler, priority=priority, name=handler_name)

    def start_game(self):
        self._interface.send_message("\n=== Game Start ===\n", debug=True)
        self._event_manager.emit("game_initialization")
        while self._running:
            current_player = self._players[self._current_turn]
            self.display_public_information()
            self._interface.send_message(f"\n--- Player {current_player.get_id()}'s Turn ---", broadcast=True)
            
            # Begin player's turn
            self._event_manager.emit("before_round_start", player=current_player)
            self._event_manager.emit("round_start_phase", player=current_player)
            continue_turn = self._event_manager.emit("before_action_phase", player=current_player)
            if continue_turn:
                self._event_manager.emit("action_phase_start", player=current_player)
                self._event_manager.emit("during_action_phase", player=current_player)
            self._event_manager.emit("turn_end_phase", player=current_player)
            self._next_turn()
    
    # Game Timeline
    def _on_game_initialization(self, event):
        self._interface.send_message("Game initialization started.", debug=True)
        # Add logic for game initialization here

    def _on_before_round_start(self, event):
        player = event.data['player']
        self._interface.send_message(f"Starting round for Player {player.get_id()}.", debug=True)
        # Add logic for before round start here

    def _on_round_start_phase(self, event):
        player = event.data['player']
        self._interface.send_message(f"Round start phase for Player {player.get_id()}.", debug=True)
        # Add logic for round start phase here

    def _on_before_action_phase(self, event):
        player = event.data['player']
        self._interface.send_message(f"Before action phase for Player {player.get_id()}.", debug=True)
        # Add logic for before action phase here

    def _on_action_phase_start(self, event):
        player = event.data['player']
        self._interface.send_message(f"Action phase started for Player {player.get_id()}.", debug=True)
        # Add logic for action phase start here

    def _on_during_action_phase(self, event):
        player = event.data['player']
        self._interface.send_message(f"During action phase for Player {player.get_id()}.", debug=True)
        player.perform_actions()
        # Add logic for during action phase here

    def _on_after_action_phase(self, event):
        player = event.data['player']
        self._interface.send_message(f"After action phase for Player {player.get_id()}.", debug=True)
        player.after_action(event)
        
    def _on_turn_end_phase(self, event):
        player = event.data['player']
        self._interface.send_message(f"Turn end phase for Player {player.get_id()}.", debug=True)
        player.reset_actions()
    
    def end_game(self, is_red_team_win):
        self._interface.send_message(f"Game ended. {'Red Team' if is_red_team_win else 'Blue Team'} wins.", broadcast=True)
        self._running = False

    # Damage Timeline
    def _on_attack_activation(self, event):
        attack_event = event.data['attack_event']
        attack_type = attack_event['attack_type']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        card = attack_event.get('card', None)
        self._interface.send_message(f"[Step 1] {attacker.get_id()} {attack_type} {defender.get_id()} with {card}.", broadcast=True)

    def _on_hit_determination(self, event):
        attack_event = event.data['attack_event']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        if attack_event.get('forced hit', False):
            attack_event['hit'] = True
            self._interface.send_message(f"[Step 2] {attacker.get_id()}'s attack forced hit {defender.get_id()}.", broadcast=True)
            self._event_manager.emit("damage_timeline_step_2_hit", attack_event=attack_event)
            return

        valid_counter_actions = defender.get_valid_counter_actions(attack_event)
        if len(valid_counter_actions) < 0:
            raise Exception("No valid counter actions found.")
        
        defender.show_hand()
        defender_action = self._interface.prompt_action_selection(valid_counter_actions, defender.get_id())
        if isinstance(defender_action, (CounterCardAction, MagicBulletCounterCardAction, HolyLightCardAction)):
            attack_event['hit'] = False
            self._interface.send_message(f"[Step 2] {defender.get_id()} counters with {defender_action}.", broadcast=True)
            self._event_manager.emit("damage_timeline_step_2_miss", attack_event=attack_event)
            defender_action.execute()
            return False
        
        elif isinstance(defender_action, NoResponseAction):
            defender_holy_shield_effect = defender.get_effects(HolyShieldEffect)
            if defender_holy_shield_effect:
                attack_event['hit'] = False
                self._interface.send_message(f"[Step 2] {defender.get_id()} has Holy Shield, attack is blocked.", broadcast=True)
                defender_holy_shield_effect[0].execute()
                self._event_manager.emit("damage_timeline_step_2_miss", attack_event=attack_event)
                return False
            else:
                attack_event['hit'] = True
                self._interface.send_message(f"[Step 2] {defender.get_id()} takes the hit.", broadcast=True)
                self._event_manager.emit("damage_timeline_step_2_hit", attack_event=attack_event)
        else:
            raise Exception(f"Invalid action type: {type(defender_action)}")

    def _on_hit_determination_hit(self, event):
        attack_event = event.data['attack_event']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        self._interface.send_message(f"[Step 2] {attacker.get_id()}'s attack hits {defender.get_id()}.", debug=True)

    def _on_hit_determination_miss(self, event):
        attack_event = event.data['attack_event']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        self._interface.send_message(f"[Step 2] {attacker.get_id()}'s attack misses {defender.get_id()}.", debug=True)

    def _on_damage_calculation(self, event):
        attack_event = event.data['attack_event']
        if attack_event.get('hit', True) is False:
            raise Exception("Damage calculation should only happen when there is a hit.")
        
        self._interface.send_message(f"[Step 3] Calculated damage: {attack_event['damage_amount']}.", debug=True)

    def _on_healing_response(self, event):
        attack_event = event.data['attack_event']
        if attack_event['damage_amount'] <= 0:
            self._interface.send_message("[Step 4] No healing response needed.", debug=True)
            return
        
        defender = attack_event['defender']
        damage = attack_event['damage_amount']
        self._interface.send_message(f"[Step 4] {defender.get_id()} has {damage} damage to respond to.", debug=True)
        
        healing_used = defender.respond_to_damage(damage)
        attack_event['healing_used'] = healing_used.get('healing', 0)
        self._interface.send_message(f"[Step 4] {defender.get_id()} uses {attack_event['healing_used']} healing.", broadcast=True)

    def _on_actual_damage_application(self, event):
        attack_event = event.data['attack_event']
        damage = attack_event['damage_amount'] - attack_event.get('healing_used', 0)
        if damage < 0:
            raise Exception("Damage should not be negative.")
        attack_event['final_damage'] = damage
        self._interface.send_message(f"[Step 5] {attack_event['defender'].get_id()} will receive {damage} damage after healing.", debug=True)

    def _on_damage_reception(self, event):
        attack_event = event.data['attack_event']
        final_damage = attack_event.get('final_damage', 0)
        if final_damage > 0:
            defender = attack_event['defender']
            defender.take_damage(final_damage, damage_type=attack_event.get('attack_type', 'attack'))
        else:
            self._interface.send_message("[Step 6] No actual damage to apply.", debug=True)
        
        attacker_team = attack_event['attacker'].get_team()
        if attack_event.get('attack_type', 'attack') == 'attack':
            attacker_team.add_jewel(gem_add=1)
            self._interface.send_message(f"Attacker's team gains 1 Gem for a successful attack.", debug=True)
        elif attack_event.get('attack_type', 'attack') == 'counter':
            attacker_team.add_jewel(crystal_add=1)
            self._interface.send_message(f"Attacker's team gains 1 Crystal for a successful counterattack.", debug=True)

    # Game Logic
    def process_damage_timeline(self, attack_event, start_step=1):
        """
        Processes the damage timeline starting from the specified step.
        
        :param attack_event: A dictionary containing details about the attack.
                             Expected keys: 'attacker', 'defender', 'card', 'damage_type'
        :param start_step: The step to start processing from (1 to 6).
        """
        self._interface.send_message(f"\n=== Processing Damage Timeline for Attack: {attack_event} ===", debug=True)
        
        steps = [
            "damage_timeline_step_1",
            "damage_timeline_step_2",
            "damage_timeline_step_3",
            "damage_timeline_step_4",
            "damage_timeline_step_5",
            "damage_timeline_step_6"
        ]
        
        for step in steps[start_step-1:]:
            if not self._event_manager.emit(step, attack_event=attack_event):
                self._interface.send_message(f"Damage timeline processing stopped at {step}.", debug=True)
                break
    
    def _next_turn(self):
        self._current_turn = (self._current_turn + 1) % len(self._players)
        self._interface.send_message(f"--- Next Turn: Player {self._players[self._current_turn].get_id()} ---", broadcast=True)
    
    def display_public_information(self):
        self._interface.send_message("\n--- Public Information ---", broadcast=True)
        self._interface.send_message(f"{self._red_team}", broadcast=True)
        self._interface.send_message(f"{self._blue_team}", broadcast=True)
        self._interface.send_message("--------------------------\n", broadcast=True)

    def get_opposite_team(self, team):
        """
        Returns the opposing team based on the given team.
        """
        if team.is_red():
            return self._blue_team
        else:
            return self._red_team

    def get_magic_bullet_target(self, player):
        current_player_index = self._players.index(player)
        num_players = len(self._players)
        
        for i in range(1, num_players):
            next_player_index = (current_player_index + i) % num_players
            next_player = self._players[next_player_index]
            
            if next_player.get_team() != player.get_team():
                return next_player
        
        raise ValueError("No player from a different team found")
    
    def get_attack_target(self, player, counter=False, attacker=None):
        candidates = []
        for p in self._players:
            if p.get_team() != player.get_team():
                if not counter and p.can_be_targeted('attack'):
                    candidates.append(p)
                elif counter and p != attacker and p.can_be_targeted('counter'):
                    candidates.append(p)
        if not candidates:
            raise ValueError("No available opponents to counter. Action canceled.")
        
        return candidates
    
    def get_magic_target(self, player, card):
        candidates = []
        if card.is_poison():
            magic_type = 'poison'
        elif card.is_weakness():
            magic_type = 'weakness'
        elif card.is_holy_shield():
            magic_type = 'holy_shield'
        else:
            raise ValueError("Invalid card type for magic action.")
        
        for p in self._players:
            if p.can_be_targeted(magic_type):
                candidates.append(p)
        if not candidates:
            raise ValueError(f"No available opponents to {magic_type}. Action canceled.")
        
        return candidates

    def get_seats_order(self, player):
        current_player_index = self._players.index(player)
        num_players = len(self._players)
        seats = []
        for i in range(1, num_players):
            next_player_index = (current_player_index + i) % num_players
            seats.append(self._players[next_player_index].get_id())
        return seats
    
    def get_interface(self):
        return self._interface
    
    def get_event_manager(self):
        return self._event_manager
    
    def get_deck(self):
        return self._deck
    

