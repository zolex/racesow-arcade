import pygame

class SpriteAnim:
    def __init__(self, sprite_sheet):
        self.sheet = sprite_sheet
        self.animations = {}  # {group: {direction: {name: {sequences, fps, loop, callback}}}}
        self.group = 'no_weapon'  # logical state of the character
        self.current_animation = None
        self.current_sequence = None
        self.frame_index = 0
        self.timer = 0

        self.previous_anim = None
        self.previous_frame = None

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
            sequences = {name: frames}

        for direction in [1, -1]:
            sprite = None
            seq_sprites = {}
            for seq_name, seq_frames in sequences.items():
                sprite_list = []
                for r, c in seq_frames:
                    sprite = self.sheet.get_sprite(r, c, direction, padding)
                    sprite_list.append(sprite)
                seq_sprites[seq_name] = sprite_list

            self.animations[group][direction][name] = {
                "sequences": seq_sprites,
                "width": sprite.get_width(),
                "height": sprite.get_height(),
                "fps": fps,
                "loop": loop,
                "callback": callback,
            }

    def previous(self, direction=1):
        if self.previous_anim is not None and self.previous_frame is not None:
            self.play(self.previous_anim, direction, reset=False, start_frame=self.previous_frame)
            self.previous_anim = None
            self.previous_frame = None

    def play(self, name, direction, callback=None, reset=True, start_frame=0):
        """play a specific animation by name."""
        #print("play anim", name, direction)
        self.previous_anim = self.current_animation
        self.previous_frame = self.frame_index
        anim_new = self.animations[self.group][direction][name]  # any direction for keys
        sequence_names_new = list(anim_new["sequences"].keys())
        if callback is not None:
            anim_new["callback"] = callback
            anim_new["callback_called"] = False

        # switching to a new animation
        if self.current_animation != name:
            # if the current sequence name also exists in the new animation (e.g., left → left)
            if self.current_sequence in sequence_names_new:
                frames_new = anim_new["sequences"][self.current_sequence]
                # if we were at the last frame, advance to the next sequence
                if self.frame_index >= len(frames_new) - 1:
                    current_idx = sequence_names_new.index(self.current_sequence)
                    if current_idx + 1 < len(sequence_names_new):
                        self.current_sequence = sequence_names_new[current_idx + 1]
                    else:
                        self.current_sequence = sequence_names_new[0]

                    self.frame_index = start_frame
                    self.timer = 0
                # else → keep frame_index & timer

            # no compatible sequence → fallback to first
            else:
                self.current_sequence = sequence_names_new[0]
                if reset:
                    self.frame_index = start_frame
                    self.timer = 0

            self.current_animation = name

        # one-shot: progress to the next sequence of the same animation (e.g., left → right)
        elif not anim_new["loop"]:
            current_idx = sequence_names_new.index(self.current_sequence)
            if current_idx + 1 < len(sequence_names_new):
                self.current_sequence = sequence_names_new[current_idx + 1]
            else:
                self.current_sequence = sequence_names_new[0]

            self.frame_index = 0
            self.timer = 0

    def update(self, dt, direction, visual_direction, fps):
        if self.current_animation is None:
            return

        anim = self.animations[self.group][direction][self.current_animation]
        frames = anim["sequences"][self.current_sequence]

        self.timer += dt
        frame_duration = 1000 / (anim["fps"] or fps)

        while self.timer >= frame_duration:
            # loops: based on playback direction
            # one-shots: always play forward
            step = 1 if not anim["loop"] else (1 if direction == visual_direction else -1)
            self.frame_index += step
            self.timer -= frame_duration

            # bounds check
            if self.frame_index >= len(frames) or self.frame_index < 0:
                sequence_names = list(anim["sequences"].keys())
                current_idx = sequence_names.index(self.current_sequence)

                # loop: cycle sequences
                if anim["loop"]:
                    if current_idx + 1 < len(sequence_names):
                        self.current_sequence = sequence_names[current_idx + 1]
                    else:
                        self.current_sequence = sequence_names[0]

                    # reset to start or end depending on playback direction
                    self.frame_index = 0 if step > 0 else len(frames) - 1

                # one-shot: freeze at last valid frame
                else:
                    self.frame_index = len(frames) - 1
                    if anim["callback"] and not anim.get("callback_called", False):
                        anim["callback"]()
                        anim["callback_called"] = True
                    return

    def get_frame(self, direction=1):
        if self.current_animation is None:
            return None, 0, 0
        anim = self.animations[self.group][direction][self.current_animation]
        frames = anim["sequences"][self.current_sequence]
        try:
            return frames[self.frame_index], anim["width"], anim["height"]
        except IndexError:
            return frames[0], anim["width"], anim["height"]