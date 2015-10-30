class Scene(object):
    """Base class for all the game scenes."""

    def __init__(self):
        # the next property is accessed every iteration of the main
        # loop, to get the scene.  When we want to change to a new
        # scene, we simply set self.next = LevelCompleteScene() (for
        # example).  This should be done in the update() method below.
        self.next = self

    def process_input(self, events, dt):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass
