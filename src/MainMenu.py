import copy, os, pygame, random, yaml, webbrowser
from datetime import date
from src import config
from src.Game import Game
from src.Input import Input
from src.Settings import Settings
from src.Scene import GameScene
from src.utils import resource_path, get_distance, create_split_rects, get_easter_date


class MainMenu(GameScene):

    ITEM_BACKGROUND_DEFAULT = (192, 192, 192, 222)
    ITEM_BACKGROUND_ACTIVE = (192, 0, 0, 222)
    ITEM_BACKGROUND_DISABLED = (32, 42, 42, 222)
    ITEM_BACKGROUND_SPACER = (16, 16, 16, 222)
    ITEM_TEXT_DEFAULT = (0, 0, 0)
    ITEM_TEXT_ACTIVE = (255, 128, 16)
    ITEM_TEXT_SPACER = (255, 0, 0, 192)
    ITEM_TEXT_DARK = (168, 92, 0)
    ITEM_TEXT_DISABLED = (11, 11, 11)

    font_path = resource_path(os.path.join('assets', 'console.ttf'))

    MENU_SCALE = 256
    MENU_STYLES = {
        "default": {
            "font_path": font_path,
            "font_size": 16,
            "item_padding": 8,
            "item_margin": 10,
            "text_offset": 1.66
        },
        "small": {
            "font_path": font_path,
            "font_size": 10,
            "item_padding": 3,
            "item_margin": 3,
            "text_offset": 1.66
        },
        "back": {
            "font_path": font_path,
            "font_size": 10,
            "item_padding": 1,
            "item_margin": 1,
            "item_width": "fit_text"
        },
        "spacer": {
            "font_path": font_path,
            "font_size": 5,
            "item_padding": 0,
            "item_margin": 0,
        },
        "mapping": {
            "font_path": font_path,
            "font_size": 9,
            "item_padding": 3,
            "item_margin": 2,
            "font_size_small": 7,
            "font_size_large": 18,
            "font_size_xlarge": 25,
            "text_offset": 1.33,
            "mapping_offset": 0.66,
        },
        "dialog": {
            "font_path": font_path,
            "font_size": 9,
            "item_padding": 3,
            "item_margin": 2,
            "font_size_small": 7,
            "font_size_large": 18,
            "item_width": "fit_text",
        },
        "large": {
            "font_path": font_path,
            "font_size": 32,
            "item_padding": 2,
            "item_margin": 4,
        }
    }

    DEFAULT_SETTINGS = {
        'resolution': {
            'width': 640,
            'height': 240,
        },
        'fullscreen': False,
    }

    def __init__(self, surface, clock, settings: Settings):
        super().__init__(surface, clock, settings)
        self.quit = False
        self.quit_really = False
        self.selected_item = 0
        self.select = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'select.wav'))
        self.back = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'back.wav'))
        self.ok = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'ok.wav'))
        self.next_scene: GameScene|None = None
        self.active_mapping = None
        self.input_mappings = None
        self.parent_menus = []
        self.active_menu = None
        self.quit_handler: callable = None
        self.entrypoint = None
        self.mouse_down_item = None
        self.mouse_down_pos = None
        self.last_mouse_motion = 0
        self.back_button = None
        self.using_mouse = False
        self.root_menu = None
        self.cursor = None
        self.music = [
            os.path.join(config.assets_folder, 'sounds', 'menu_1.ogg'),
            os.path.join(config.assets_folder, 'sounds', 'menu_2.ogg'),
        ]

        self.splash: pygame.Surface = self.load_splash()
        self.load_menu()
        self.load_cursor()

    def reset(self):
        self.quit = False
        self.quit_really = False
        self.selected_item = 0
        self.active_mapping = None
        self.input_mappings = None
        self.parent_menus = []
        self.active_menu = None
        self.load_menu()
        self.init_input_mappings()

    def load_cursor(self):
        today = date.today()
        easter_month, easter_day = get_easter_date()
        if today.month == easter_month and easter_day - 7 <= today.day <= easter_day + 3:
            self.settings.cursor = 'easter'
        elif today.month == 12 and 18 <= today.day <= 31:
            self.settings.cursor = 'xmas'

        if self.settings.cursor is not None:
            cursor_file = os.path.join(config.assets_folder, 'graphics', 'cursor', f'{self.settings.cursor}.png')
            cursor = pygame.image.load(cursor_file).convert_alpha()
            scale = self.settings.get_scale()
            width = cursor.get_width() / 7 * scale
            height = cursor.get_height() / 7 * scale
            self.cursor = pygame.transform.scale(cursor, (width, height))

    def draw_cursor(self):
        if self.cursor is None or not pygame.mouse.get_focused():
            return

        ticks = pygame.time.get_ticks()
        fade_start_time = self.last_mouse_motion + 1337
        fade_duration = 2000  # 2 seconds for fading

        if ticks < fade_start_time:
            self.cursor.set_alpha(255)
        elif fade_start_time <= ticks < fade_start_time + fade_duration:
            time_since_fade_start = ticks - fade_start_time
            alpha = 255 - int((time_since_fade_start / fade_duration) * 255)
            self.cursor.set_alpha(alpha)
        else:
            return

        self.surface.blit(self.cursor, pygame.mouse.get_pos())

    def play_music(self):
        if self.settings.music_enabled:
            pygame.mixer.music.load(self.music[random.choice([0, 1])])
            pygame.mixer.music.play(loops=-1, fade_ms=3886)

    def stop_music(self):
        if self.settings.music_enabled:
            pygame.mixer.music.fadeout(1337)

    def load_splash(self):
        splash = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'splash_high.png')).convert_alpha()

        # Get original dimensions
        orig_width, orig_height = splash.get_size()

        # Scale proportionally to screen width
        width = self.surface.get_width()
        scale_factor = width / orig_width
        new_height = int(orig_height * scale_factor)

        return pygame.transform.scale(splash, (width, new_height))

    def load_menu(self):
        menu_file = os.path.join(config.assets_folder, 'menu.yaml')
        with open(menu_file, 'r') as file:
            menu = yaml.safe_load(file)
            self.root_menu = menu
            self.activate_menu(menu)

    def scale_style(self, style):

        scale = self.surface.get_height() / MainMenu.MENU_SCALE
        scaled = {
            "item_padding": int(style.get('item_padding', 0) * scale),
            "item_margin": int(style.get('item_margin', 0) * scale),
            "text_offset": style.get('text_offset', 0) * scale,
            "mapping_offset": style.get('mapping_offset', 0) * scale,
        }

        if style.get('font_size') is not None:
            scaled["font_size"] = int(style['font_size'] * scale)
            scaled['font'] = pygame.font.Font(style.get('font_path', None), scaled['font_size'])

        if style.get('font_size_small') is not None:
            scaled['font_size_small'] = int(style['font_size_small'] * scale)
            scaled['font_small'] = pygame.font.Font(style.get('font_path', None), scaled['font_size_small'])

        if style.get('font_size_large') is not None:
            scaled['font_size_large'] = int(style['font_size_large'] * scale)
            scaled['font_large'] = pygame.font.Font(style.get('font_path', None), scaled['font_size_large'])

        if style.get('font_size_xlarge') is not None:
            scaled['font_size_xlarge'] = int(style['font_size_xlarge'] * scale)
            scaled['font_xlarge'] = pygame.font.Font(style.get('font_path', None), scaled['font_size_xlarge'])

        if style.get('item_width') is not None:
            scaled['item_width'] = style['item_width']
        else:
            scaled['item_width'] = int(0.8 * self.surface.get_width() / (self.surface.get_width() / self.surface.get_height()))

        return scaled

    def extract_input(self, event: pygame.event.Event, type: str):
        if type == Input.KEYBOARD:
            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL:
                    return {'mod': pygame.KMOD_CTRL}

                if event.mod & pygame.KMOD_ALT:
                    return {'mod': pygame.KMOD_ALT}

                if event.mod & pygame.KMOD_SHIFT:
                    return {'mod': pygame.KMOD_SHIFT}

                return {'key': event.key}

        if type == Input.CONTROLLER:
            if event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
                return {'button': event.button}

            if event.type == pygame.JOYAXISMOTION:
                return {'axis': event.axis, 'value': round(event.value)}

            if event.type == pygame.JOYHATMOTION:
                return {'hat': event.hat, 'value': event.value}

        return None

    def set_mapping(self, mapping: dict, event: pygame.event.Event):

        if mapping is None:
            return
            
        input = self.extract_input(event, mapping.get('type'))
        if input is None:
            return

        mapping_type = self.settings.mapping.get(mapping.get('type', {}))
        for mapping_name, existing_input in mapping_type.items():
            existing_mapping = mapping_type.get(mapping_name)
            group = None
            for item in self.active_menu.get('items'):
                if item.get('mapping') == mapping_name:
                    group = item.get('group')
                    break

            if existing_input == input and mapping.get('group') == group:
                existing_mapping.clear()

        mapping = mapping_type.get(mapping.get('mapping'), {})
        mapping.clear()
        mapping.update(input)

        self.ok.play()
        self.active_mapping = None

    def get_mapping(self, mapping):
        type = mapping.get('type')
        mapping = mapping.get('mapping')
        return self.settings.mapping.get(type, {}).get(mapping, {})

    def get_mapping_name(self, mapping):

        key = mapping.get('key')
        if key is not None:
            return f'[{pygame.key.name(key).upper()}]'

        mod = mapping.get('mod')
        if mod is not None:
            if mod & pygame.KMOD_ALT:
                return "[ALT]"
            if mod & pygame.KMOD_CTRL:
                return "[CTRL]"
            if mod & pygame.KMOD_SHIFT:
                return "[SHIFT]"

        axis = mapping.get('axis')
        value = mapping.get('value')
        if axis is not None and value is not None:
            if axis == 0 and value == -1:
                return "[AXIS LEFT]"
            if axis == 0 and value == 1:
                return "[AXIS RIGHT]"
            if axis == 1 and value == -1:
                return "[AXIS UP]"
            if axis == 1 and value == 1:
                return "[AXIS DOWN]"

        button = mapping.get('button')
        if button is not None:
            return f"[BUTTON {button}]"

        return None

    def draw_mapping_text(self, type, action, current_mapping, back_key, style):
        return self.draw_dialog_text([
            style['font'].render(f"press any {'key' if type == 'keyboard' else 'button'} on your {type} to assign", True, MainMenu.ITEM_TEXT_DEFAULT),
            style['font_xlarge'].render(f'ACTION: {action}', True, MainMenu.ITEM_TEXT_ACTIVE),
            style['font_large'].render(f"CURRENT {current_mapping}", True, MainMenu.ITEM_TEXT_DEFAULT),
            style['font_small'].render(f"press {back_key} to abort", True, MainMenu.ITEM_TEXT_DEFAULT),
        ], style)

    def draw_dialog_text(self, lines, style):
        """
        Render multiline text to a surface.
        If max_width is provided, text is word-wrapped to fit within that width.
        """
        max_line_width = max(line.get_width() for line in lines)
        surface_width = self.get_item_width(style, max_line_width)
        total_height = sum(line.get_height() for line in lines) + style['item_margin'] * 3 * (len(lines) - 1) + style['item_padding'] * 8
        surface = pygame.Surface((surface_width, total_height), pygame.SRCALPHA)

        y = style['item_padding'] * 4
        for line_surf in lines:
            x = (surface_width - line_surf.get_width()) // 2
            surface.blit(line_surf, (x, y))
            y += line_surf.get_height() + style['item_margin'] * 3

        return surface

    def draw_active_mapping(self):
        current_mapping = self.get_mapping(self.active_mapping)
        mapping_name = self.get_mapping_name(current_mapping)

        mapping_style = self.scale_style(MainMenu.MENU_STYLES.get('mapping'))
        type = self.active_mapping.get('type')
        back_key = self.settings.mapping.get(type, {}).get('back', {})
        back_name = self.get_mapping_name(back_key)
        text_surface = self.draw_mapping_text(
            type,
            self.active_mapping.get('text'),
            mapping_name,
            back_name,
            mapping_style,
        )

        item_height = text_surface.get_height()
        rect_y = self.surface.get_height() / 1.5 - item_height / 2
        rect_x = (self.surface.get_width() - mapping_style['item_width']) // 2
        text_width, text_height = text_surface.get_size()
        rect_height = item_height

        # Draw transparent rectangle
        rect_surface = pygame.Surface((mapping_style['item_width'], rect_height), pygame.SRCALPHA)
        rect_surface.fill(MainMenu.ITEM_BACKGROUND_ACTIVE)
        self.surface.blit(rect_surface, (rect_x, rect_y))

        # Center text on the rectangle
        text_x = rect_x + (mapping_style['item_width'] - text_width) // 2
        text_y = rect_y + (rect_height - text_height) // 2
        self.surface.blit(text_surface, (text_x, text_y))

    def draw_quit_really(self):
        style = self.scale_style(MainMenu.MENU_STYLES.get('dialog'))
        back_key = self.settings.mapping.get(Input.KEYBOARD, {}).get(Input.BACK, {})
        back_button = self.settings.mapping.get(Input.CONTROLLER, {}).get(Input.BACK, {})
        back_name = self.get_mapping_name(back_key)
        back_name2 = self.get_mapping_name(back_button)
        select_key = self.settings.mapping.get(Input.KEYBOARD, {}).get(Input.SELECT, {})
        select_button = self.settings.mapping.get(Input.CONTROLLER, {}).get(Input.SELECT, {})
        select_name = self.get_mapping_name(select_key)
        select_name2 = self.get_mapping_name(select_button)
        text_surface = self.draw_dialog_text([
            style['font'].render('Do you really want to', True, MainMenu.ITEM_TEXT_DEFAULT),
            style['font_large'].render('QUIT?', True, MainMenu.ITEM_TEXT_ACTIVE),
            style['font_small'].render(f'press {back_name} or {back_name2} to stay', True, MainMenu.ITEM_TEXT_DEFAULT),
            style['font_small'].render(f"press {select_name} or {select_name2} to leave", True, MainMenu.ITEM_TEXT_DARK),
        ], style)

        rect_height = text_surface.get_height()
        text_width, text_height = text_surface.get_size()
        rect_width = self.get_item_width(style, text_width)
        rect_y = self.surface.get_height() / 1.5 - rect_height / 2
        rect_x = (self.surface.get_width() - rect_width) // 2

        # Draw the dialog background
        rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        rect_surface.fill(MainMenu.ITEM_BACKGROUND_ACTIVE if self.selected_item == -1 else MainMenu.ITEM_BACKGROUND_DEFAULT)
        self.surface.blit(rect_surface, (rect_x, rect_y))

        # Center text on the rectangle
        text_x = rect_x + (rect_width - text_width) // 2
        text_y = rect_y + (rect_height - text_height) // 2
        self.surface.blit(text_surface, (text_x, text_y))

        self.back_button = {
            'action': 'quit_really',
            'bbox': pygame.Rect(rect_x, rect_y, rect_width, rect_height)
        }

    def get_item_width(self, style, text_width, default=100):
        if style.get('item_width') == 'fit_text':
            return text_width + style.get('item_padding') * 8
        else:
            return style.get('item_width', default)

    def find_sibling_by_action(self, action):
        for item in self.active_menu.get('items'):
            if item.get('action') == action:
                return item
        return None

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.splash, (0, 0))

        style_name = 'default' if self.active_menu is None else self.active_menu.get('style', 'default')
        menu_style = self.scale_style(MainMenu.MENU_STYLES.get(style_name))

        # menu title
        title = self.active_menu.get('title') if self.active_menu is not None else 'WHY SO SERIOUS?'
        title_style = self.scale_style(MainMenu.MENU_STYLES.get('large'))
        text_surface = title_style['font'].render(title, True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        aspect_ratio = text_width / text_height
        #max_width = (self.surface.get_width() - menu_style['item_width']) / 2 - title_style['item_margin'] * 2
        max_width = (self.surface.get_width() / 2) - 100 * self.settings.get_scale()
        max_height = title_style['font_size']
        if (max_width / aspect_ratio) <= max_height:
            new_width = max_width
            new_height = new_width / aspect_ratio
        else:
            new_height = max_height
            new_width = new_height * aspect_ratio
        text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
        text_x = self.surface.get_width() - new_width - title_style['item_margin']
        #text_y = self.splash.get_height() - new_height - title_style['item_margin'] * 2
        text_y = title_style['item_margin']
        self.surface.blit(text_surface, (text_x, text_y))

        if self.active_mapping is not None:
            return self.draw_active_mapping()

        if self.quit:
            return self.draw_quit_really()

        if self.active_menu is None:
            return None


        item_height = menu_style['font_size'] + menu_style['item_padding']

        menu_items = self.active_menu.get('items')
        total_height = len(menu_items) * (item_height + menu_style['item_margin']) - menu_style['item_margin']
        scale = self.surface.get_height() / MainMenu.MENU_SCALE
        start_y = self.surface.get_height() - total_height - 10 * scale

        if self.has_back_button():
            self.draw_back_button(start_y, menu_style)
        else:
            self.back_button = None

        menu_index = 0
        for item in menu_items:
            if item.get('spacer') and not item.get('text'):
                menu_index += 1
                continue

            text_color = None
            text_offset = 0
            if item.get('action') == 'switch':
                text_offset = 1.25 * scale
                text = f"{item.get('text')} [{'ON' if self.settings.get(item.get('setting')) else 'OFF'}]"
            elif item.get('action') == 'setting':
                text = f"{item.get('text')} ({self.settings.get(item.get('setting'))})"
            elif item.get('action') == 'select_option' and item.get('value') == self.settings.get(self.active_menu.get('setting')):
                text_color = MainMenu.ITEM_TEXT_DARK
                text_offset = 1.25 * scale
                text = f"[{item.get('text')}]"
            else:
                text = item.get('text')

            if item.get('depends'):
                depends = item.get('depends')
                if depends.startswith('!'):
                    depends = depends[1:]
                    item['disabled'] = self.settings.get(depends)
                else:
                    item['disabled'] = not self.settings.get(depends)

            if item.get('disabled'):
                background_color = MainMenu.ITEM_BACKGROUND_DISABLED
                text_color = MainMenu.ITEM_TEXT_DISABLED
            elif menu_index == self.selected_item:
                background_color = MainMenu.ITEM_BACKGROUND_ACTIVE
                text_color = text_color or MainMenu.ITEM_TEXT_ACTIVE
            elif item.get('spacer'):
                background_color = MainMenu.ITEM_BACKGROUND_SPACER
                text_color = text_color or MainMenu.ITEM_TEXT_SPACER
            else:
                background_color = MainMenu.ITEM_BACKGROUND_DEFAULT
                text_color = text_color or MainMenu.ITEM_TEXT_DEFAULT

            text_surface = menu_style['font'].render(text, True, text_color)
            text_width, text_height = text_surface.get_size()
            rect_height = item_height
            rect_x = (self.surface.get_width() - menu_style['item_width']) // 2
            rect_y = start_y + menu_index * (item_height + menu_style['item_margin'])
            item_width = self.get_item_width(menu_style, text_width)
            rect_surface = pygame.Surface((item_width, rect_height), pygame.SRCALPHA)
            rect_surface.fill(background_color)
            self.surface.blit(rect_surface, (rect_x, rect_y))

            text_y = rect_y + (rect_height - text_height) // 2
            if style_name == 'mapping':
                text_x = rect_x + menu_style['item_padding'] * 2
                mapping = self.get_mapping(item)
                mapping_text = self.get_mapping_name(mapping)
                mapping_surface = menu_style['font_small'].render(mapping_text, True, MainMenu.ITEM_TEXT_DARK)
                mapping_x = rect_x + menu_style['item_width'] - mapping_surface.get_width() - menu_style['item_padding'] * 2
                mapping_y = rect_y + (rect_height - mapping_surface.get_height()) // 2 + menu_style['mapping_offset']
                self.surface.blit(mapping_surface, (mapping_x, mapping_y))
            else:
                text_x = rect_x + (item_width - text_width) // 2

            self.surface.blit(text_surface, (text_x, text_y + menu_style['text_offset'] - text_offset))

            if item.get('action') == 'setting':
                self.surface.blit(menu_style['font'].render('<', True, MainMenu.ITEM_TEXT_DEFAULT), (rect_x + menu_style['item_padding'], text_y + menu_style['text_offset'] * 2))
                self.surface.blit(menu_style['font'].render('>', True, MainMenu.ITEM_TEXT_DEFAULT),(rect_x + item_width - menu_style['item_padding'] - 10 * scale, text_y + menu_style['text_offset'] * 2))


            item['bbox'] = pygame.Rect(rect_x, rect_y, item_width, rect_height)

            menu_index += 1


        return None

    def update(self):
        pass

    def has_back_button(self):
        return len(self.parent_menus) > 0 or self.entrypoint is not None

    def draw_back_button(self, menu_y, active_style):
        if self.selected_item == -1:
            text_color = MainMenu.ITEM_TEXT_ACTIVE
            background_color = MainMenu.ITEM_BACKGROUND_ACTIVE
        else:
            text_color = MainMenu.ITEM_TEXT_DEFAULT
            background_color = MainMenu.ITEM_BACKGROUND_DEFAULT

        back_style = self.scale_style(MainMenu.MENU_STYLES.get('back'))
        text_surface = back_style['font'].render('x', True, text_color)
        text_width, text_height = text_surface.get_size()
        rect_height = back_style['font_size'] + back_style['item_padding']
        item_width = self.get_item_width(back_style, text_width)
        rect_x = self.surface.get_width() // 2 + self.get_item_width(active_style, text_width) // 2 - item_width
        rect_y = menu_y - rect_height - active_style['item_margin']
        rect_surface = pygame.Surface((item_width, rect_height), pygame.SRCALPHA)
        rect_surface.fill(background_color)
        self.surface.blit(rect_surface, (rect_x, rect_y))
        text_x = rect_x + (item_width - text_width) // 2
        text_y = rect_y + back_style['item_margin'] + back_style['item_padding']
        self.surface.blit(text_surface, (text_x, text_y))

        self.back_button = {
            'action': Input.BACK,
            'text': '',
            'bbox': pygame.Rect(rect_x, rect_y, item_width, rect_height)
        }

    def handle_set_mapping(self):
        self.handle_events({
            Input.BACK: lambda v, e: self.abort_mapping(v),
            Input.ANY: lambda e: self.set_mapping(self.active_mapping, e),
        })

    def abort_mapping(self, key_down):
        if key_down:
            self.active_mapping = None
            self.back.play()

    def get_selected_item(self):
        if (self.active_menu is None and self.back_button is None) or self.selected_item is None:
            return None

        try:
            return self.active_menu.get('items')[self.selected_item] if self.selected_item >= 0 else self.back_button
        except IndexError or TypeError:
            return None

    def load_maps_menu(self):
        return {
            'menu': {
                'title': 'MAPS',
                'action': 'menu',
                'items': [
                    {
                        'action': 'map',
                        'map': 'egypt',
                        'text': 'EGYPT (alpha.1)',
                    },
                    {
                        'action': 'web_link',
                        'link': 'https://github.com/zolex/RAME/blob/alpha.1/README.md',
                        'text': 'create your own map!',
                    },
                ]
            }
        }

    def set_item_enabled(self, item_name, enabled):
        for item in self.active_menu.get('items'):
            if item.get('action') == item_name:
                item['disabled'] = not enabled
                break

    def switch_music(self):
        if self.settings.music_enabled:
            self.play_music()
        else:
            self.stop_music()

    def set_setting(self, item, value):
        setting = item.get('setting')
        self.settings.set(setting, value)
        callback = item.get('callback')
        if callback is not None:
            method = getattr(self, callback)
            if callback is not None and method is not None:
                method()

    def menu_ok(self, key_down, using_mouse = False):
        if not key_down:
            return

        self.using_mouse = using_mouse

        selected_item = self.get_selected_item()
        if selected_item is None:
            return

        if selected_item.get('action') == 'play':
            self.ok.play()
            self.activate_menu(self.load_maps_menu())

        elif selected_item.get('action') == 'switch':
            self.ok.play()
            setting = selected_item.get('setting')
            self.set_setting(selected_item, not self.settings.get(setting))

        elif selected_item.get('action') == 'select_option':
            last = len(self.parent_menus) - 1
            try:
                if self.active_menu.get('type') != 'select':
                    return
                self.set_setting(self.active_menu, selected_item.get('value'))
            except IndexError:
                return

        elif selected_item.get('action') == 'map':
            self.ok.play()
            self.stop_music()
            self.next_scene = Game(selected_item.get('map'), self.surface, self.clock, self.settings)

        elif selected_item.get('action') == 'web_link':
            self.ok.play()
            webbrowser.open(selected_item.get('link'))

        elif selected_item.get('action') == 'menu':
            self.ok.play()
            self.activate_menu(selected_item)

        elif selected_item.get('action') == 'back':
            self.menu_back_or_quit()

        elif selected_item.get('action') == 'mapping':
            self.ok.play()
            self.show_mapping(selected_item)

        elif selected_item.get('action') == 'quit':
            self.menu_back_or_quit()

    def activate_menu(self, menu_item):
        if self.active_menu is not None:
            self.active_menu['selected_item'] = self.selected_item
            self.parent_menus.append(self.active_menu)

        self.active_menu = menu_item.get('menu')

        if self.using_mouse:
            self.selected_item = None
            self.mouse_down_pos = None
            self.mouse_down_item = None
            event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': pygame.mouse.get_pos()})
            self.handle_mouse_motion(event)
        else:
            self.selected_item = menu_item.get('selected_item', 0)

        selected = self.get_selected_item()
        if selected is not None:
            while selected.get('disabled') or selected.get('spacer'):
                self.selected_item += 1
                selected = self.get_selected_item()

    def reload(self):
        display_options = pygame.SCALED
        if self.settings.fullscreen:
            display_options += pygame.FULLSCREEN

        self.surface = pygame.display.set_mode((self.settings.resolution[0], self.settings.resolution[1]), display_options)
        self.splash = self.load_splash()
        self.load_cursor()

    def update_game_settings(self):
        if isinstance(self.next_scene, Game):
            self.next_scene.update_settings()

    def show_mapping(self, menu_item):
        self.active_mapping = menu_item

    def change_resolution(self, width, height):
        self.settings.resolution[0] = int(width)
        self.settings.resolution[1] = int(height)
        self.reload()

    def change_max_fps(self, fps):
        self.settings.max_fps = int(fps)
        self.reload()

    def menu_up(self, key_down = True, using_mouse = False):
        if not key_down:
            return

        self.using_mouse = using_mouse

        if self.selected_item is None and self.active_menu is not None:
            self.selected_item = len(self.active_menu.get('items')) - 1
            return

        if self.selected_item > (-1 if self.has_back_button() else 0):
            self.selected_item -= 1
            if self.get_selected_item().get('spacer') or self.get_selected_item().get('disabled'):
                self.selected_item -= 1
            self.select.play()

    def menu_down(self, key_down = True, using_mouse = False):
        if not key_down:
            return

        self.using_mouse = using_mouse

        if self.selected_item is None:
            self.selected_item = 0
            return

        if self.selected_item < len(self.active_menu.get('items')) - 1:
            self.selected_item += 1
            if self.get_selected_item().get('spacer') or self.get_selected_item().get('disabled'):
                self.selected_item += 1
            self.select.play()

    def menu_left(self, key_down = True, using_mouse = False):
        if not key_down:
            return

        self.using_mouse = using_mouse

        item = self.get_selected_item()
        if item is not None and item.get('action') == 'setting':
            self.settings.reduce(item.get('setting'))

    def menu_right(self, key_down = True, using_mouse = False):
        if not key_down:
            return

        self.using_mouse = using_mouse

        item = self.get_selected_item()
        if item is not None and item.get('action') == 'setting':
            self.settings.increase(item.get('setting'))

    def handle_mouse_motion(self, event):
        try:
            if event.rel[0] == 0 and event.rel[1] == 0:
                return
        except AttributeError:
            pass

        self.last_mouse_motion = pygame.time.get_ticks()

        self.using_mouse = True
        if self.mouse_down_pos is not None:
            return

        selected = False
        if self.active_menu is not None:
            for item in self.active_menu.get('items'):
                if item.get('bbox') and item.get('bbox').collidepoint(event.pos) and not item.get('disabled') and not item.get('spacer'):
                    selected = True
                    self.selected_item = self.active_menu.get('items', []).index(item)
                    break

        if not selected and self.back_button is not None and self.back_button.get('bbox'):
            if self.back_button.get('bbox').collidepoint(event.pos):
                selected = True
                self.selected_item = -1

        if not selected:
            self.selected_item = None

    def handle_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item = self.get_selected_item()
            if item is not None and item['bbox'].collidepoint(event.pos):
                self.mouse_down_item = item
                self.mouse_down_pos = event.pos
            else:
                self.mouse_down_item = None
                self.mouse_down_pos = None
        elif event.type == pygame.MOUSEBUTTONUP:

            if self.mouse_down_pos is not None and get_distance(event.pos, self.mouse_down_pos) > 10 * self.settings.get_scale():
                self.mouse_down_item = None
                self.mouse_down_pos = None
                self.handle_mouse_motion(event)
                return

            item = self.get_selected_item()
            if item is not None and not item.get('disabled') and item == self.mouse_down_item and item.get('bbox').collidepoint(event.pos):
                if item.get('action') == 'setting':
                    left, right = create_split_rects(item.get('bbox'))
                    if left.collidepoint(event.pos):
                        self.menu_left(True, True)
                    elif right.collidepoint(event.pos):
                        self.menu_right(True, True)
                elif item.get('action') == 'quit_really':
                    self.quit_really = True
                else:
                    self.menu_ok(True, True)
            elif self.back_button is not None and self.back_button.get('action') == 'quit_really' and not self.back_button.get('bbox').collidepoint(event.pos):
                self.abort_quit(True)

            self.mouse_down_item = None
            self.mouse_down_pos = None

    def init_input_mappings(self):
        self.input_mappings = {
            Input.UP: lambda v, e: self.menu_up(v),
            Input.DOWN: lambda v, e: self.menu_down(v),
            Input.LEFT: lambda v, e: self.menu_left(v),
            Input.RIGHT: lambda v, e: self.menu_right(v),
            Input.SELECT: lambda v, e: self.menu_ok(v),
            Input.BACK: lambda v, e: self.menu_back_or_quit(v),
            pygame.MOUSEMOTION: lambda e: self.handle_mouse_motion(e),
            pygame.MOUSEBUTTONDOWN: lambda e: self.handle_click(e),
            pygame.MOUSEBUTTONUP: lambda e: self.handle_click(e),
            pygame.K_UP: lambda v, e: self.menu_up(v),
            pygame.K_DOWN: lambda v, e: self.menu_down(v),
            pygame.K_LEFT: lambda v, e: self.menu_left(v),
            pygame.K_RIGHT: lambda v, e: self.menu_right(v),
            pygame.K_RETURN: lambda v, e: self.menu_ok(v),
            pygame.K_ESCAPE: lambda v, e: self.menu_back_or_quit(v),
        }

    def set_quit(self, key_down: bool = True):
        super().set_quit(key_down)
        self.active_menu = None

    def set_quit_really(self):
        self.quit_really = True

    def menu_back_or_quit(self, key_down=True):
        if not key_down:
            return

        if self.active_mapping is not None:
            self.active_mapping = None
            return

        if len(self.parent_menus) > 0:
            self.back.play()
            self.active_menu = self.parent_menus.pop()
            self.selected_item = None if self.using_mouse else self.active_menu.get('selected_item', 0)
        else:
            self.quit_handler()

    def abort_quit(self, key_down):
        if key_down:
            self.quit = False
            self.activate_menu(self.root_menu)
            self.play_music()

    def handle_quit_really(self):
        self.stop_music()
        self.handle_events({
            Input.BACK: lambda v, e: self.abort_quit(v),
            Input.SELECT: lambda v, e: setattr(self, 'quit_really', True),
            pygame.MOUSEBUTTONDOWN: lambda e: self.handle_click(e),
            pygame.MOUSEBUTTONUP: lambda e: self.handle_click(e),
            pygame.MOUSEMOTION: lambda e: self.handle_mouse_motion(e),
        })

    def game_loop(self, entrypoint: list[str] = None, force_quit = False):

        if force_quit:
            self.quit_handler = lambda: self.set_quit_really()
        else:
            self.quit_handler = lambda: self.set_quit()

        if entrypoint is not None:
            self.entrypoint = entrypoint
            self.reset()
            for action in entrypoint:
                for item in self.active_menu.get('items'):
                    if item.get('text') == action:
                        self.activate_menu(item)
                        break
            self.parent_menus = []
            self.selected_item = 0

        if self.settings.music_enabled:
            self.play_music()

        while True:

            # draw first because we need the positions to handle mouse events
            self.clock.tick(self.settings.max_fps)
            self.draw()
            self.draw_cursor()

            pygame.display.update()

            if self.quit:
                self.handle_quit_really()
            elif self.active_mapping is not None:
                self.handle_set_mapping()
            else:
                self.handle_events(self.input_mappings, self.quit_handler)

            if self.next_scene is not None and entrypoint is None:
                next_scene = copy.copy(self.next_scene)
                next_scene.set_next_scene(self)
                self.next_scene = None
                return next_scene

            if self.quit_really:
                break
