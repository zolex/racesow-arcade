import pygame
from importlib import import_module

class StateMachine:
    """Manages states"""
    def __init__(self, initial_state, owner_object):
        self.state = initial_state
        self.owner_object = owner_object

    def _create_state_instance(self, event_name):
        """Dynamically import and instantiate a state class by its name."""
        module = import_module(f"src.Player.State.{event_name}")
        state_cls = getattr(module, event_name, None)
        if state_cls is None:
            return None
        return state_cls()

    def transition(self, event):
        #if event != self.state.__class__.__name__:
            #print("--------------------------------")
            #print("TRY", event, "FROM", self.state.__class__.__name__)
        if self.state.can_transition(event):

            new_state = self._create_state_instance(event)
            if not new_state or new_state == self.state:
                return

            #print("ALLOW", event)

            can_exit = self.state.can_exit(self.owner_object)
            #print("CAN_EXIT", can_exit)

            can_enter = new_state.can_enter(self.owner_object)
            #print("CAN_ENTER", can_enter)

            if can_exit and can_enter:
                self.state.on_exit(self.owner_object)
                old_state = self.get_state()
                self.state = new_state
                self.state.on_enter(self.owner_object, old_state)
                print("ENTER", type(new_state).__name__, pygame.time.get_ticks())

    def update(self):
        self.state.update(self.owner_object)

    def get_state(self):
        return self.state.__class__.__name__