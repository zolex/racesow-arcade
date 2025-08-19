class State:
    """State Class"""
    def on_event(self, event):
        """Handles events delegated to this state"""
        pass

    def can_enter(self, owner_object):
        """Determines if state can enter"""
        return True

    def on_enter(self, owner_object):
        """Performs actions when entering state"""
        pass

    def update(self, owner_object):
        """Performs actions specific to state when active"""
        pass

    def on_exit(self, owner_object):
        """Performs actions when exiting state"""
        pass

    def can_exit(self, owner_object):
        """Determines if state can exit"""
        return True
