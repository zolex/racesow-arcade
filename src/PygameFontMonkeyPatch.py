import sys

def ApplyPygameFontMonkeyPatch():
    # Only apply the patch if pygame.font is broken (e.g., on Python 3.14+)
    try:
        import pygame.font
        # If we can access Font and it's not a dummy, we don't need the patch
        if hasattr(pygame.font, 'Font') and not hasattr(pygame.font, 'FontWrapper'):
            # Double check it actually works
            try:
                test_font = pygame.font.Font(None, 24)
                return # It works, no patch needed
            except (NotImplementedError, ImportError, RuntimeError):
                pass # Something is wrong, proceed to patch
    except (ImportError, AttributeError):
        pass

    # monkey-patch for compatibility conflict between Python 3.14 and pygame 2.6.1
    # caused by a circular dependency in pygame modules. Python 3.14's import changes exposed this issue, which was not present in earlier Python versions.
    # we can get rid of this when pygame has fixed the issue.

    try:
        import pygame._freetype
        pygame._freetype.init()

        class FontWrapper(pygame._freetype.Font):
            def render(self, text, antialias, color, background=None):
                return super().render(text, color, background)[0]

            def set_bold(self, bold):
                self.strong = bold

            def get_bold(self):
                return self.strong

            def set_italic(self, italic):
                self.oblique = italic

            def get_italic(self):
                return self.oblique

            def set_underline(self, underline):
                self.underline = underline

            def get_underline(self):
                return self.underline

            def set_strikethrough(self, strikethrough):
                # freetype doesn't have strikethrough
                pass

            def get_strikethrough(self):
                return False

            def get_height(self):
                return int(self.get_sized_height())

            def get_linesize(self):
                return int(self.get_sized_height())

            def get_ascent(self):
                return int(self.get_sized_ascender())

            def get_descent(self):
                return int(self.get_sized_descender())

        # Create a dummy module-like object for pygame.font
        class FontModule:
            Font = FontWrapper
            def init(self): pygame._freetype.init()
            def quit(self): pygame._freetype.quit()
            def get_init(self): return pygame._freetype.get_init()
            def get_default_font(self): return pygame._freetype.get_default_font()

        font_module = FontModule()
        sys.modules['pygame.font'] = font_module
        pygame.font = font_module
    except ImportError:
        pass
