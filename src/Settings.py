import os, tempfile, yaml

class Settings:
    def __init__(self):
        self.settings_file = os.path.join(tempfile.gettempdir(), 'racesow_acrade.yaml')
        self.width = 640
        self.height = 320
        self.fullscreen = False
        self.max_fps = 120

    def get_scale(self):
        return self.height / 320

    def load(self):
        if not os.path.isfile(self.settings_file):
            return

        with open(self.settings_file, 'r') as file:
            data = yaml.safe_load(file)

        self.width = data.get('resolution', {}).get('width', 640)
        self.height = data.get('resolution', {}).get('height', 320)
        self.fullscreen = data.get('fullscreen', False)
        self.max_fps = data.get('max_fps', 120)

    def save(self):
        settings = {
            "resolution": {
                "width": self.width,
                "height": self.height,
            },
            "fullscreen": self.fullscreen,
            "max_fps": self.max_fps,
        }

        with open(self.settings_file, "w") as file:
            yaml.dump(settings, file, default_flow_style=False)
