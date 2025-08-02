class GameObject():
    def __init__(self, shape):
        self.shape = shape

    def __getattr__(self, name):
        """Makes lines shorter by not having to type rect.pos when retrieving position"""
        if name == 'pos':
            return self.shape.pos
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Makes lines shorter by not having to type rect.pos when setting position"""
        if name == 'pos':
            self.shape.pos = value
        else:
            object.__setattr__(self, name, value)