class State:
    """State Class"""
    def on_event(self, event):
        """Handles events delegated to this state"""
        pass

    def on_enter(self, owner_object):
        """Performs actions when entering state"""
        pass

    def update(self, owner_object):
        """Performs actions specific to state when active"""
        pass

    def on_exit(self, owner_object):
        """Performs actions when exiting state"""
        pass