# game_engine/AgrGameEngine.py

from models.Player import Player
from models.Team import Team
from models.Deck import Deck
from models.Effect import HolyShieldEffect
from views.ConsoleInterface import ConsoleInterface
from models.Action import AttackAction, MagicAction, SynthesisAction, PurchaseAction, RefineAction, HolyLightCardAction, NoResponseAction, CounterCardAction
from game_engine.EventManager import EventManager

class AgrGameEngine:
    def __init__(self, config):
        self.interface = ConsoleInterface()
        self.event_manager = EventManager()
        self.setup_game(config)
        self.setup_damage_timeline()
        self.setup_game_timeline()
        self.current_turn = 0
        self.running = True

    def setup_game(self, config):
        # Initialize teams
        self.red_team = Team(is_red=True)
        self.blue_team = Team(is_red=False)
        
        # Initialize single deck
        self.deck = Deck(config['deck_path'])
        
        # Initialize players
        self.players = []
        for pid in range(1, config['num_players'] + 1):
            # Assign players to teams based on config
            if pid in config.get('red_players', []):
                team = self.red_team
            else:
                team = self.blue_team
            player = Player(player_id=pid, team=team, deck=self.deck, interface=self.interface)
            player.draw_initial_hand()
            self.players.append(player)
            team.add_player(player)

    def setup_damage_timeline(self):
        """
        Sets up the damage timeline by subscribing relevant methods to each step.
        This template allows easy addition of character-specific methods to the timeline.
        """
        # Step 1: Attack Activation
        self.event_manager.subscribe("damage_timeline_step_1", self.on_attack_activation)
        
        # Step 2: Hit Determination
        self.event_manager.subscribe("damage_timeline_step_2", self.on_hit_determination)
        
        # Step 3: Damage Calculation
        self.event_manager.subscribe("damage_timeline_step_3", self.on_damage_calculation)
        
        # Step 4: Healing Response
        self.event_manager.subscribe("damage_timeline_step_4", self.on_healing_response)
        
        # Step 5: Actual Damage Application
        self.event_manager.subscribe("damage_timeline_step_5", self.on_actual_damage_application)
        
        # Step 6: Damage Reception
        self.event_manager.subscribe("damage_timeline_step_6", self.on_damage_reception)
        
        # Add more subscriptions for other characters or effects here

    def setup_game_timeline(self):
        """
        Sets up the game timeline by subscribing relevant methods to each event.
        """
        # Game start events
        self.event_manager.subscribe("game_start", self.on_game_start)
        
        # Round start events
        self.event_manager.subscribe("round_start", self.on_round_start)
        
        # Before action events
        self.event_manager.subscribe("before_action", self.on_before_action)
        
        # Action phase events
        self.event_manager.subscribe("action_phase", self.on_action_phase)
        
        # Round end events
        self.event_manager.subscribe("round_end", self.on_round_end)
        
        # Turn end events
        self.event_manager.subscribe("turn_end", self.on_turn_end)
        
        # Add more subscriptions for other game events here

    def start_game(self):
        print("\n=== Game Start ===\n")
        self.event_manager.emit("game_start")
        while self.running:
            current_player = self.players[self.current_turn]
            self.display_public_information()
            print(f"\n--- Player {current_player.id}'s Turn ---")
            
            # Begin player's turn
            self.event_manager.emit("round_start", player=current_player)
            self.event_manager.emit("before_action", player=current_player)
            self.event_manager.emit("action_phase", player=current_player)
            self.event_manager.emit("round_end", player=current_player)
            if self.check_game_end():
                break
            
            self.next_turn()

    def handle_attack_or_counter(self, attacker, defender, card, is_counter=False):
        action_type = "counterattack" if is_counter else "attack"
        print(f"\nPlayer {attacker.id} performs an {action_type} on Player {defender.id} with {card.name}.")

        valid_counter_cards = defender.get_valid_counter_cards(card)
        defender_action = self.interface.prompt_defender_action(defender, attacker, has_counter=bool(valid_counter_cards))
        
        if defender_action == "counterattack" and valid_counter_cards:
            counter_card = self.interface.prompt_card_selection(valid_counter_cards)
            if counter_card:
                print(f"Player {defender.id} counters with {counter_card.name}.")
                if counter_card.is_holy_light():
                    print(f"The attack is canceled by {counter_card.name}. No jewels are gained.")
                    return
                self.event_manager.emit(
                    "counter",
                    attacker=defender,
                    defender=attacker,
                    card=counter_card,
                    is_counter=True
                )
                return
            else:
                print("No counter card selected. Defender takes the hit.")
                self.apply_damage(attacker, defender, card, is_counter)
        elif defender_action == "take_damage" or not valid_counter_cards:
            print(f"{'Defender has no valid counter cards. ' if not valid_counter_cards else ''}Defender takes the hit.")
            self.apply_damage(attacker, defender, card, is_counter)
        else:
            print("Invalid defender action. Defender takes the hit.")
            self.apply_damage(attacker, defender, card, is_counter)

    def apply_damage(self, attacker, defender, card, is_counter=False):
        base_damage = getattr(card, 'damage_value', 2)
        total_damage = base_damage
        defender.take_damage(total_damage)
        
        if is_counter:
            if attacker.team.jewels.can_add(crystal_add=1):
                attacker.team.jewels.add_jewel(crystal_add=1)
                print(f"{attacker.team} gains 1 Crystal for a successful counterattack.")
            else:
                print(f"{attacker.team} cannot add more jewels. Jewels are full.")
        else:
            if attacker.team.jewels.can_add(gem_add=1):
                attacker.team.jewels.add_jewel(gem_add=1)
                print(f"{attacker.team} gains 1 Gem for a successful attack.")
            else:
                print(f"{attacker.team} cannot add more jewels. Jewels are full.")

    def process_damage_timeline(self, attack_event, start_step=1):
        """
        Processes the damage timeline starting from the specified step.
        
        :param attack_event: A dictionary containing details about the attack.
                             Expected keys: 'attacker', 'defender', 'card', 'damage_type'
        :param start_step: The step to start processing from (1 to 6).
        """
        print(f"\n=== Processing Damage Timeline for Attack: {attack_event} ===")
        
        steps = [
            "damage_timeline_step_1",
            "damage_timeline_step_2",
            "damage_timeline_step_3",
            "damage_timeline_step_4",
            "damage_timeline_step_5",
            "damage_timeline_step_6"
        ]
        
        for step in steps[start_step-1:]:
            self.event_manager.emit(step, attack_event=attack_event)
        
        # After processing, check for game end conditions
        self.check_game_end()

    def on_attack_activation(self, attack_event):
        """
        Handles Step 1: Attack Activation
        """
        attack_type = attack_event.get('attack_type', 'attack')
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        card = attack_event.get('card')
        amount = attack_event.get('amount', 2)
        # damage_type = attack_event.get('damage_type', 'attack')
        print(f"[Step 1] {attacker.id} {attack_type} {defender.id} with {card.name}.")
        # Additional logic for attack activation can be added here

    def on_hit_determination(self, attack_event):
        """
        Handles Step 2: Hit Determination
        """
        attacker = attack_event['attacker']
        defender = attack_event['defender']
        if attack_event.get('forced hit', False):
            attack_event['hit'] = True
            print(f"[Step 2] {attacker.id}'s attack forced hit {defender.id}.")
            return

        valid_counter_actions = defender.get_valid_counter_actions(attack_event)
        if valid_counter_actions:
            print(f"[Step 2] {defender.id} has valid counter actions: {valid_counter_actions}.")
            defender_action = self.interface.prompt_defender_action(defender, attacker, valid_counter_actions)
            if isinstance(defender_action, CounterCardAction):
                attack_event['hit'] = False
                print(f"[Step 2] {defender.id} counters with {defender_action.card.name}.")
                defender_action.execute(defender, self)
            elif isinstance(defender_action, HolyLightCardAction):
                attack_event['hit'] = False
                print(f"[Step 2] {defender.id} uses Holy Light to cancel the attack.")
            elif isinstance(defender_action, HolyShieldEffect):
                attack_event['hit'] = False
                print(f"[Step 2] {defender.id} uses Holy Shield to cancel the attack.")
                defender_action.execute(defender, self)
            elif isinstance(defender_action, NoResponseAction):
                attack_event['hit'] = True
                print(f"[Step 2] {defender.id} takes the hit.")
        else:
            attack_event['hit'] = True
            print(f"[Step 2] {defender.id} takes the hit.")

    def on_damage_calculation(self, attack_event):
        """
        Handles Step 3: Damage Calculation
        """
        if not attack_event.get('hit'):
            attack_event['damage_amount'] = 0
            print("[Step 3] No damage to calculate due to missed attack.")
            return
        
        print(f"[Step 3] Calculated damage: {attack_event['damage_amount']}.")

    def on_healing_response(self, attack_event):
        """
        Handles Step 4: Healing Response
        """
        if attack_event['damage_amount'] <= 0:
            print("[Step 4] No healing response needed.")
            return
        
        defender = attack_event['defender']
        damage = attack_event['damage_amount']
        print(f"[Step 4] {defender.id} has {damage} damage to respond to.")
        
        # Defender decides to use healing
        healing_used = defender.respond_to_damage(damage)
        attack_event['healing_used'] = healing_used.get('healing', 0)
        print(f"[Step 4] {defender.id} uses {attack_event['healing_used']} healing.")

    def on_actual_damage_application(self, attack_event):
        """
        Handles Step 5: Actual Damage Application
        """
        damage = attack_event['damage_amount'] - attack_event.get('healing_used', 0)
        damage = max(damage, 0)  # Prevent negative damage
        attack_event['final_damage'] = damage
        print(f"[Step 5] {attack_event['defender']} will receive {damage} damage after healing.")

    def on_damage_reception(self, attack_event):
        """
        Handles Step 6: Damage Reception
        """
        final_damage = attack_event.get('final_damage', 0)
        if final_damage > 0:
            defender = attack_event['defender']
            defender.take_damage(final_damage, damage_type=attack_event.get('attack_type', 'attack'))
            attacker_team = attack_event['attacker'].team
            if attack_event.get('attack_type', 'attack') == 'attack':
                attacker_team.jewels.add_jewel(gem_add=1)
                print(f"Attacker's team gains 1 Gem for a successful attack.")
            elif attack_event.get('attack_type', 'attack') == 'counter':
                attacker_team.jewels.add_jewel(crystal_add=1)
                print(f"Attacker's team gains 1 Crystal for a successful counterattack.")
        else:
            print("[Step 6] No actual damage to apply.")

    def execute_attack(self, attack_type, attacker, defender, card, damage_amount, can_not_counter=False, start_step=1):
        attack_event = {
            'attack_type': attack_type,
            'attacker': attacker,
            'defender': defender,
            'card': card,
            'damage_amount': damage_amount,
            'can_not_counter': can_not_counter,
        }
        self.process_damage_timeline(attack_event, start_step=start_step)

    def check_game_end(self):
        """
        Checks if game end conditions are met.
        """
        for team in [self.red_team, self.blue_team]:
            if team.has_won():
                print(f"\n=== {team} has won the game! ===")
                self.running = False
                break

    def end_game(self, winning_team):
        """
        Ends the game and declares the winning team.
        
        :param winning_team: The team that has met the victory conditions.
        """
        print(f"Game Over! {winning_team} wins!")
        # Additional logic to handle game end (e.g., resetting, saving scores)

    def display_public_information(self):
        print("\n--- Public Information ---")
        print(f"{self.red_team}")
        print(f"{self.blue_team}")
        print("--------------------------\n")

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
        print(f"--- Next Turn: Player {self.players[self.current_turn].id} ---")

    def on_game_start(self):
        """
        Handles game start events.
        """
        print("Game has started. Initializing game state.")
        # Add logic for game start events here

    def on_round_start(self, player):
        """
        Handles round start events.
        """
        print(f"Round start for Player {player.id}.")
        # Add logic for round start events here
        player.round_start()

    def on_before_action(self, player):
        """
        Handles before action events.
        """
        print(f"Before action phase for Player {player.id}.")
        # Add logic for before action events here
        player.before_action()

    def on_action_phase(self, player):
        """
        Handles action phase events.
        """
        print(f"Action phase for Player {player.id}.")
        # Add logic for action phase events here
        player.perform_actions(self)

    def on_round_end(self, player):
        """
        Handles round end events.
        """
        print(f"Round end for Player {player.id}.")
        # Add logic for round end events here
        player.round_end()

    def on_turn_end(self, player):
        """
        Handles turn end events.
        """
        print(f"Turn end for Player {player.id}.")
        # Add logic for turn end events here
        
