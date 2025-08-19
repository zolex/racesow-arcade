import pygame

class SpriteAnim:
    def __init__(self, sprite_sheet, default_fps=10):
        self.sheet = sprite_sheet
        self.animations = {}  # {group: {direction: {name: {sequences, fps, loop, callback}}}}
        self.group = 'no_weapon'  # logical state of the character
        self.current_animation = None
        self.current_sequence = None
        self.frame_index = 0
        self.timer = 0
        self.default_fps = default_fps

    def add(self, name, group, frames, fps=None, loop=True, callback=None, padding=None):
        """
        name: animation name
        frames: either list of (row, col) tuples or dict of sequences {sequence_name: list of (row, col)}
        group: logical state name
        fps: frames per second
        loop: whether animation loops
        callback: function to call when non-looping animation finishes
        """

        if group not in self.animations:
            self.animations[group] = {1: {}, -1: {}}

        # Normalize frames to dict of sequences
        if isinstance(frames, dict):
            sequences = frames
        else:
            sequences = {"default": frames}

        for direction in [1, -1]:
            seq_sprites = {}
            for seq_name, seq_frames in sequences.items():
                sprite_list = []
                for r, c in seq_frames:
                    sprite_list.append(self.sheet.get_sprite(r, c, direction, padding))
                seq_sprites[seq_name] = sprite_list

            self.animations[group][direction][name] = {
                "sequences": seq_sprites,
                "fps": fps or self.default_fps,
                "loop": loop,
                "callback": callback,
            }

    def play(self, name, reset=True):
        """Directly play a specific animation by name."""
        anim_new = self.animations[self.group][1][name]  # any direction for keys
        sequence_names_new = list(anim_new["sequences"].keys())

        if self.current_animation != name:
            # switching to a new animation
            if self.current_sequence in sequence_names_new:
                frames_new = anim_new["sequences"][self.current_sequence]

                if self.frame_index >= len(frames_new) - 1:
                    # if we were at the last frame → advance to next sequence
                    current_idx = sequence_names_new.index(self.current_sequence)
                    if current_idx + 1 < len(sequence_names_new):
                        self.current_sequence = sequence_names_new[current_idx + 1]
                    else:
                        self.current_sequence = sequence_names_new[0]

                    self.frame_index = 0
                    self.timer = 0
                # else → keep frame_index & timer
            else:
                # no compatible sequence → fallback to first
                self.current_sequence = sequence_names_new[0]
                if reset:
                    self.frame_index = 0
                    self.timer = 0

            self.current_animation = name

        else:
            # replaying the same animation
            if not anim_new["loop"]:
                current_idx = sequence_names_new.index(self.current_sequence)
                if current_idx + 1 < len(sequence_names_new):
                    self.current_sequence = sequence_names_new[current_idx + 1]
                else:
                    self.current_sequence = sequence_names_new[0]

                # reset when replaying a non-looping animation
                self.frame_index = 0
                self.timer = 0

    def update(self, dt, direction=1, fps=None):
        if self.current_animation is None:
            return

        anim = self.animations[self.group][direction][self.current_animation]
        frames = anim["sequences"][self.current_sequence]

        self.timer += dt
        frame_duration = 1000 / (fps or anim["fps"])

        while self.timer >= frame_duration:
            self.timer -= frame_duration
            self.frame_index += 1

            if self.frame_index >= len(frames):
                sequence_names = list(anim["sequences"].keys())
                current_idx = sequence_names.index(self.current_sequence)

                if anim["loop"]:
                    # looped animation: always cycle sequences
                    if current_idx + 1 < len(sequence_names):
                        self.current_sequence = sequence_names[current_idx + 1]
                    else:
                        self.current_sequence = sequence_names[0]
                    self.frame_index = 0

                else:
                    # non-looping: freeze on last frame of current sequence
                    self.frame_index = len(frames) - 1
                    if anim["callback"]:
                        anim["callback"]()
                    return

    def get_frame(self, direction=1):
        if self.current_animation is None:
            return None
        anim = self.animations[self.group][direction][self.current_animation]
        frames = anim["sequences"][self.current_sequence]
        return frames[self.frame_index]