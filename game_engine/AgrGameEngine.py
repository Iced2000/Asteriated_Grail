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
        self.networked = config.get('networked', False)
        if self.networked:
            self.interface = NetworkedConsoleInterface(game_server=config.get('game_server', None), debug=config.get('debug', False))
        else:
            self.interface = LocalConsoleInterface(debug=config.get('debug', False))
        self.event_manager = EventManager(self.interface)
        self.setup_game(config)
        self.current_turn = 0
        self.running = True
        
        self.setup_event_handlers()

    def setup_game(self, config):
        # Initialize teams
        self.red_team = Team(is_red=True, interface=self.interface)
        self.blue_team = Team(is_red=False, interface=self.interface)
        
        # Initialize single deck
        self.deck = Deck(config['deck_path'], interface=self.interface)
        
        # Initialize players
        self.players = []
        for player_config in config['player']:
            team = self.red_team if player_config['team'] == 'red' else self.blue_team
            character_config = {
                'character_type': player_config['character_type'],
                'player_id': player_config['pid'],
                'team': team,
                'deck': self.deck,
                'interface': self.interface,
                'event_manager': self.event_manager,
                'game_engine': self
            }
            player = CharacterFactory.create_character(character_config)
            player.draw_initial_hand()
            self.players.append(player)
            team.add_player(player)

    def setup_event_handlers(self):
        for event_type, handlers in GameTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self.event_manager.subscribe(event_type, handler, priority=priority, name=handler_name)

        for event_type, handlers in DamageTimeline.items():
            for priority, handler_name in enumerate(handlers):
                handler = getattr(self, handler_name, None)
                if handler:
                    self.event_manager.subscribe(event_type, handler, priority=priority, name=handler_name)

    def on_game_initialization(self, event):
        self.interface.send_message("Game initialization started.", debug=True)
        # Add logic for game initialization here

    def on_before_round_start(self, event):
        player = event.data['player']
        self.interface.send_message(f"Starting round for Player {player.id}.", debug=True)
        # Add logic for before round start here

    def on_round_start_phase(self, event):
        player = event.data['player']
        self.interface.send_message(f"Round start phase for Player {player.id}.", debug=True)
        # Add logic for round start phase here

    def on_before_action_phase(self, event):
        player = event.data['player']
        self.interface.send_message(f"Before action phase for Player {player.id}.", debug=True)
        # Add logic for before action phase here

    def on_action_phase_start(self, event):
        player = event.data['player']
        self.interface.send_message(f"Action phase started for Player {player.id}.", debug=True)
        # Add logic for action phase start here

    def on_during_action_phase(self, event):
        player = event.data['player']
        self.interface.send_message(f"During action phase for Player {player.id}.", debug=True)
        player.perform_actions()
        # Add logic for during action phase here

    def on_after_action_phase(self, event):
        player = event.data['player']
        self.interface.send_message(f"After action phase for Player {player.id}.", debug=True)
        player.after_action(event)
        
    def on_turn_end_phase(self, event):
        player = event.data['player']
        self.interface.send_message(f"Turn end phase for Player {player.id}.", debug=True)
        player.reset_actions()

    # Damage Timeline
    def on_attack_activation(self, event):
        attack_event = event.data['attack_event']
        attack_type = attack_event['attack_type']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        card = attack_event.get('card', None)
        self.interface.send_message(f"[Step 1] {attacker.id} {attack_type} {defender.id} with {card}.", broadcast=True)

    def on_hit_determination(self, event):
        attack_event = event.data['attack_event']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        if attack_event.get('forced hit', False):
            attack_event['hit'] = True
            self.interface.send_message(f"[Step 2] {attacker.id}'s attack forced hit {defender.id}.", broadcast=True)
            self.event_manager.emit("damage_timeline_step_2_hit", attack_event=attack_event)
            return

        valid_counter_actions = defender.get_valid_counter_actions(attack_event)
        if len(valid_counter_actions) < 0:
            raise Exception("No valid counter actions found.")
        
        defender.hand.show_hand()
        defender_action = self.interface.prompt_action_selection(valid_counter_actions, defender.id)
        if isinstance(defender_action, (CounterCardAction, MagicBulletCounterCardAction, HolyLightCardAction)):
            attack_event['hit'] = False
            self.interface.send_message(f"[Step 2] {defender.id} counters with {defender_action.card.name}.", broadcast=True)
            self.event_manager.emit("damage_timeline_step_2_miss", attack_event=attack_event)
            defender_action.execute()
            return False
        
        elif isinstance(defender_action, NoResponseAction):
            defender_holy_shield_effect = defender.effects.get_effects(HolyShieldEffect)
            if defender_holy_shield_effect:
                attack_event['hit'] = False
                self.interface.send_message(f"[Step 2] {defender.id} has Holy Shield, attack is blocked.", broadcast=True)
                self.event_manager.emit("damage_timeline_step_2_miss", attack_event=attack_event)
                defender_holy_shield_effect.execute()
                return False
            else:
                attack_event['hit'] = True
                self.interface.send_message(f"[Step 2] {defender.id} takes the hit.", broadcast=True)
                self.event_manager.emit("damage_timeline_step_2_hit", attack_event=attack_event)
        else:
            raise Exception(f"Invalid action type: {type(defender_action)}")

    def on_hit_determination_hit(self, event):
        attack_event = event.data['attack_event']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        self.interface.send_message(f"[Step 2] {attacker.id}'s attack hits {defender.id}.", debug=True)

    def on_hit_determination_miss(self, event):
        attack_event = event.data['attack_event']
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        self.interface.send_message(f"[Step 2] {attacker.id}'s attack misses {defender.id}.", debug=True)

    def on_damage_calculation(self, event):
        attack_event = event.data['attack_event']
        if attack_event.get('hit', True) is False:
            raise Exception("Damage calculation should only happen when there is a hit.")
        
        self.interface.send_message(f"[Step 3] Calculated damage: {attack_event['damage_amount']}.", debug=True)

    def on_healing_response(self, event):
        attack_event = event.data['attack_event']
        if attack_event['damage_amount'] <= 0:
            self.interface.send_message("[Step 4] No healing response needed.", debug=True)
            return
        
        defender = attack_event['defender']
        damage = attack_event['damage_amount']
        self.interface.send_message(f"[Step 4] {defender.id} has {damage} damage to respond to.", debug=True)
        
        healing_used = defender.respond_to_damage(damage)
        attack_event['healing_used'] = healing_used.get('healing', 0)
        self.interface.send_message(f"[Step 4] {defender.id} uses {attack_event['healing_used']} healing.", broadcast=True)

    def on_actual_damage_application(self, event):
        attack_event = event.data['attack_event']
        damage = attack_event['damage_amount'] - attack_event.get('healing_used', 0)
        if damage < 0:
            raise Exception("Damage should not be negative.")
        attack_event['final_damage'] = damage
        self.interface.send_message(f"[Step 5] {attack_event['defender']} will receive {damage} damage after healing.", debug=True)

    def on_damage_reception(self, event):
        attack_event = event.data['attack_event']
        final_damage = attack_event.get('final_damage', 0)
        if final_damage > 0:
            defender = attack_event['defender']
            defender.take_damage(final_damage, damage_type=attack_event.get('attack_type', 'attack'))
        else:
            self.interface.send_message("[Step 6] No actual damage to apply.", debug=True)
        
        attacker_team = attack_event['attacker'].team
        if attack_event.get('attack_type', 'attack') == 'attack':
            attacker_team.jewels.add_jewel(gem_add=1)
            self.interface.send_message(f"Attacker's team gains 1 Gem for a successful attack.", debug=True)
        elif attack_event.get('attack_type', 'attack') == 'counter':
            attacker_team.jewels.add_jewel(crystal_add=1)
            self.interface.send_message(f"Attacker's team gains 1 Crystal for a successful counterattack.", debug=True)


    def start_game(self):
        self.interface.send_message("\n=== Game Start ===\n", debug=True)
        self.event_manager.emit("game_initialization")
        while self.running:
            current_player = self.players[self.current_turn]
            self.display_public_information()
            self.interface.send_message(f"\n--- Player {current_player.id}'s Turn ---", broadcast=True)
            
            # Begin player's turn
            self.event_manager.emit("before_round_start", player=current_player)
            self.event_manager.emit("round_start_phase", player=current_player)
            continue_turn = self.event_manager.emit("before_action_phase", player=current_player)
            if continue_turn:
                self.event_manager.emit("action_phase_start", player=current_player)
                self.event_manager.emit("during_action_phase", player=current_player)
            self.event_manager.emit("turn_end_phase", player=current_player)
            self.next_turn()
       
    # Game Logic
    def process_damage_timeline(self, attack_event, start_step=1):
        """
        Processes the damage timeline starting from the specified step.
        
        :param attack_event: A dictionary containing details about the attack.
                             Expected keys: 'attacker', 'defender', 'card', 'damage_type'
        :param start_step: The step to start processing from (1 to 6).
        """
        self.interface.send_message(f"\n=== Processing Damage Timeline for Attack: {attack_event} ===", debug=True)
        
        steps = [
            "damage_timeline_step_1",
            "damage_timeline_step_2",
            "damage_timeline_step_3",
            "damage_timeline_step_4",
            "damage_timeline_step_5",
            "damage_timeline_step_6"
        ]
        
        for step in steps[start_step-1:]:
            if not self.event_manager.emit(step, attack_event=attack_event):
                self.interface.send_message(f"Damage timeline processing stopped at {step}.", debug=True)
                break

    def display_public_information(self):
        self.interface.send_message("\n--- Public Information ---", broadcast=True)
        self.interface.send_message(f"{self.red_team}", broadcast=True)
        self.interface.send_message(f"{self.blue_team}", broadcast=True)
        self.interface.send_message("--------------------------\n", broadcast=True)

    def get_opposite_team(self, team):
        """
        Returns the opposing team based on the given team.
        """
        if team.is_red:
            return self.blue_team
        else:
            return self.red_team

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)
        self.interface.send_message(f"--- Next Turn: Player {self.players[self.current_turn].id} ---", broadcast=True)
    
    def get_magic_bullet_target(self, player):
        current_player_index = self.players.index(player)
        num_players = len(self.players)
        
        for i in range(1, num_players):
            next_player_index = (current_player_index + i) % num_players
            next_player = self.players[next_player_index]
            
            if next_player.team != player.team:
                return next_player
        
        raise ValueError("No player from a different team found")
    
    def get_attack_target(self, player, counter=False, attacker=None):
        if counter:
            candidates = [p for p in self.players if p.team != player.team and p.can_be_attacked and p != attacker]
        else:
            candidates = [p for p in self.players if p.team != player.team and p.can_be_attacked]
        
        if not candidates:
            raise ValueError("No available opponents to counter. Action canceled.")
        
        return candidates

    def get_seats_order(self, player):
        current_player_index = self.players.index(player)
        num_players = len(self.players)
        seats = []
        for i in range(1, num_players):
            next_player_index = (current_player_index + i) % num_players
            seats.append(self.players[next_player_index].id)
        return seats
