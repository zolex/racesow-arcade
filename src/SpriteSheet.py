import pygame


class SpriteSheet:
    def __init__(self, sheet_path, sprite_width, sprite_height, margin=0, spacing=0, padding=(0, 0, 0, 0), add_flipped=False, scale=1):
        """
        sheet_path: path to sprite sheet image
        sprite_width, sprite_height: size of each sprite in the sheet
        margin: pixels around the edges of the sheet
        spacing: pixels between sprites
        padding: (top, right, bottom, left) OR True to auto-trim transparent pixels per sprite
        add_flipped: if True, also generate horizontally flipped versions of sprites
        """
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.sprites = []       # right-facing frames
        self.sprites_left = []  # left-facing frames (flipped)
        self.padding = padding  # tuple or True
        self.add_flipped = add_flipped

        # Load the sheet
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        # Calculate rows and columns
        cols = (sheet_width - 2 * margin + spacing) // (sprite_width + spacing)
        rows = (sheet_height - 2 * margin + spacing) // (sprite_height + spacing)

        # First pass: extract all candidate sprites (possibly cropped)
        all_sprites = []
        for row in range(rows):
            row_sprites = []
            for col in range(cols):
                x = margin + col * (sprite_width + spacing)
                y = margin + row * (sprite_height + spacing)
                base_rect = pygame.Rect(x, y, sprite_width, sprite_height)
                sprite = sheet.subsurface(base_rect)

                # apply global padding
                sprite = self._apply_padding(sprite, self.padding)

                if scale != 1:
                    sprite = pygame.transform.scale(sprite, (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))

                row_sprites.append(sprite)
            all_sprites.append(row_sprites)

        # Determine maximum width/height across all sprites
        max_w = 0
        max_h = 0
        for row_sprites in all_sprites:
            for sprite in row_sprites:
                w, h = sprite.get_size()
                max_w = max(max_w, w)
                max_h = max(max_h, h)

        # Second pass: pad each sprite onto a surface of max_w x max_h
        for row_sprites in all_sprites:
            padded_row = []
            padded_row_left = []
            for sprite in row_sprites:
                w, h = sprite.get_size()
                surf = pygame.Surface((max_w, max_h), pygame.SRCALPHA)
                offset_x = (max_w - w) // 2
                offset_y = (max_h - h) // 2
                surf.blit(sprite, (offset_x, offset_y))
                padded_row.append(surf)

                if self.add_flipped:
                    flipped = pygame.transform.flip(surf, True, False)
                    padded_row_left.append(flipped)

            self.sprites.append(padded_row)
            if self.add_flipped:
                self.sprites_left.append(padded_row_left)

        # Save the uniform frame size for animations
        self.frame_width = max_w
        self.frame_height = max_h

    def _apply_padding(self, sprite, padding):
        """Apply either auto-trim or fixed padding to a sprite surface."""
        if padding is True:
            cropped_rect = sprite.get_bounding_rect()
            return sprite.subsurface(cropped_rect)
        else:
            pad_top, pad_right, pad_bottom, pad_left = padding
            cropped_rect = pygame.Rect(
                pad_left,
                pad_top,
                sprite.get_width() - pad_left - pad_right,
                sprite.get_height() - pad_top - pad_bottom
            )
            return sprite.subsurface(cropped_rect)

    def get_sprite(self, row, col, direction, padding_override=None):
        """
        Return the sprite at a specific row and column.
        Optionally apply per-animation padding.
        """
        if direction == 1:
            sprite = self.sprites[row][col]
        elif direction == -1 and self.add_flipped:
            sprite = self.sprites_left[row][col]
        else:
            sprite = self.sprites[row][col]

        # If per-animation padding is specified, reapply it on-the-fly
        if padding_override is not None:
            sprite = self._apply_padding(sprite, padding_override)

        return sprite