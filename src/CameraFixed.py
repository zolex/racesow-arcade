from src.Camera import Camera
from src.Settings import Settings

class CameraFixed(Camera):
    def __init__(self, settings: Settings):
        super(CameraFixed, self).__init__(settings)
        self.offset_x = self.settings.get_scale() * 60
        self.offset_y  = settings.resolution[1] / 2

    def update(self, player):
        if player.direction == 1:
            self.pos.x = player.pos.x + player.shape.w - self.offset_x
        else:
            self.pos.x = player.pos.x - self.w + self.offset_x + player.shape.w
        self.pos.y = player.pos.y + player.shape.h - self.offset_y
