from src.Camera import Camera
from src.Settings import Settings

class CameraFixed(Camera):
    def __init__(self, settings: Settings):
        super(CameraFixed, self).__init__(settings)
        self.offset_x = self.settings.get_scale() * 60
        self.offset_y  = settings.resolution[1] / 2

    def update(self, player):
        if player.direction == 1:
            self.x = player.x + player.w - self.offset_x
        else:
            self.x = player.x - self.w + self.offset_x + player.w
        self.y = player.y + player.h - self.offset_y
