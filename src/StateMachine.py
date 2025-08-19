class StateMachine:
    """Manages states"""
    def __init__(self, initial_state, owner_object):
        self.state = initial_state
        self.owner_object = owner_object

    def on_event(self, event):
        """Updates current state and runs on_exit and on_enter"""
        new_state = self.state.on_event(event)
        if new_state is not self.state:
            if self.state.can_exit(self.owner_object) and new_state.can_enter(self.owner_object):
                self.state.on_exit(self.owner_object)
                self.state = new_state
                self.state.on_enter(self.owner_object)

    def update(self):
        self.state.update(self.owner_object)

    def get_state(self):
        return self.state.__class__.__name__