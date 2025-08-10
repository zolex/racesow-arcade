import os, pygame, random, yaml, webbrowser
from src import config
from src.Game import Game
from src.Settings import Settings
from src.Scene import GameScene
from src.utils import resource_path


class MainMenu(GameScene):

    ITEM_BACKGROUND_DEFAULT = (255, 255, 255, 128)  # semi-transparent white
    ITEM_BACKGROUND_ACTIVE = (255, 0, 0, 192)  # semi-transparent red
    ITEM_TEXT_DEFAULT = (0, 0, 0)
    ITEM_TEXT_ACTIVE = (255, 128, 16)
    ITEM_TEXT_DARK = (168, 92, 0)

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
            "font_size": 11,
            "item_padding": 3,
            "item_margin": 4,
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
            "font_size": 30,
            "item_padding": 4,
            "item_margin": 8,
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
        self.splash: pygame.Surface = self.load_splash()
        self.selected_item = 0
        self.select = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'select.wav'))
        self.back = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'back.wav'))
        self.ok = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'ok.wav'))
        self.parent_menus = []
        self.active_menu = None
        self.load_menu()

        self.active_mapping = None

        self.music = [
            os.path.join(config.assets_folder, 'sounds', 'menu_1.ogg'),
            os.path.join(config.assets_folder, 'sounds', 'menu_2.ogg'),
        ]

        self.play_music()

        self.controllers: list[pygame.joystick.Joystick] = []
        pygame.joystick.init()
        for i in range(0, pygame.joystick.get_count()):
            controller = pygame.joystick.Joystick(i)
            self.controllers.append(controller)

    def play_music(self):
        pygame.mixer.music.load(self.music[random.choice([0, 1])])
        pygame.mixer.music.play(loops=-1, fade_ms=2000)

    def stop_music(self):
        pygame.mixer.music.fadeout(2000)

    def load_splash(self):
        splash = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'splash.jpg')).convert_alpha()

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
            scaled['item_width'] = int(0.9 * self.surface.get_width() / (self.surface.get_width() / self.surface.get_height()))

        return scaled

    def extract_input(self, event: pygame.event.Event, type: str):

        if type == 'keyboard':
            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL:
                    return {'mod': pygame.KMOD_CTRL}

                if event.mod & pygame.KMOD_ALT:
                    return {'mod': pygame.KMOD_ALT}

                if event.mod & pygame.KMOD_SHIFT:
                    return {'mod': pygame.KMOD_SHIFT}

                return {'key': event.key}

        if type == 'controller':
            if event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
                return {'button': event.button}

            if event.type == pygame.JOYAXISMOTION:
                return {'axis': event.axis, 'value': round(event.value)}

            if event.type == pygame.JOYHATMOTION:
                return {'hat': event.hat, 'value': event.value}

        return None

    def set_mapping(self, mapping: dict, event: pygame.event.Event):

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

    def draw_quit_confirmation(self):
        style = self.scale_style(MainMenu.MENU_STYLES.get('dialog'))
        back_key = self.settings.mapping.get('keyboard', {}).get('back', {})
        back_button = self.settings.mapping.get('controller', {}).get('back', {})
        back_name = self.get_mapping_name(back_key)
        back_name2 = self.get_mapping_name(back_button)
        select_key = self.settings.mapping.get('keyboard', {}).get('select', {})
        select_button = self.settings.mapping.get('controller', {}).get('select', {})
        select_name = self.get_mapping_name(select_key)
        select_name2 = self.get_mapping_name(select_button)
        text_surface = self.draw_dialog_text([
            style['font'].render('Are you sure, you want to', True, MainMenu.ITEM_TEXT_DEFAULT),
            style['font_large'].render('QUIT?', True, MainMenu.ITEM_TEXT_ACTIVE),
            style['font_small'].render(f'press {back_name} or {back_name2} to stay', True, MainMenu.ITEM_TEXT_DEFAULT),
            style['font_small'].render(f"press {select_name} or {select_name2} to leave", True, MainMenu.ITEM_TEXT_DARK),
        ], style)

        rect_height = text_surface.get_height()
        text_width, text_height = text_surface.get_size()
        rect_width = self.get_item_width(style, text_width)
        rect_y = self.surface.get_height() / 1.5 - rect_height / 2
        rect_x = (self.surface.get_width() - rect_width) // 2

        # Draw transparent rectangle
        rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        rect_surface.fill(MainMenu.ITEM_BACKGROUND_ACTIVE)
        self.surface.blit(rect_surface, (rect_x, rect_y))

        # Center text on the rectangle
        text_x = rect_x + (rect_width - text_width) // 2
        text_y = rect_y + (rect_height - text_height) // 2
        self.surface.blit(text_surface, (text_x, text_y))

    def get_item_width(self, style, text_width, default=100):
        if style.get('item_width') == 'fit_text':
            return text_width + style.get('item_padding') * 8
        else:
            return style.get('item_width', default)

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.splash, (0, 0))

        if self.active_menu is None:
            return None

        # menu title
        title_style = self.scale_style(MainMenu.MENU_STYLES.get('large'))
        text_surface = title_style['font'].render(self.active_menu.get('title'), True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        text_x = self.settings.width - text_width - title_style['item_margin']
        self.surface.blit(text_surface, (text_x, title_style['item_margin']))

        if self.active_mapping is not None:
            return self.draw_active_mapping()

        if self.quit:
            return self.draw_quit_confirmation()


        style_name = self.active_menu.get('style', 'default')
        style = self.scale_style(MainMenu.MENU_STYLES.get(style_name))
        item_height = style['font_size'] + style['item_padding']

        menu_items = self.active_menu.get('items')
        total_height = len(menu_items) * (item_height + style['item_margin']) - style['item_margin']
        scale = self.surface.get_height() / MainMenu.MENU_SCALE
        start_y = self.surface.get_height() - total_height - 10 * scale

        if self.has_back_button():
            self.draw_back_button(start_y, style)



        menu_index = 0
        for item in menu_items:
            if item.get('spacer'):
                menu_index += 1
                continue

            if menu_index == self.selected_item:
                background_color = MainMenu.ITEM_BACKGROUND_ACTIVE
                text_color = MainMenu.ITEM_TEXT_ACTIVE
            else:
                background_color = MainMenu.ITEM_BACKGROUND_DEFAULT
                text_color = MainMenu.ITEM_TEXT_DEFAULT

            text_surface = style['font'].render(item.get('text'), True, text_color)
            text_width, text_height = text_surface.get_size()
            rect_height = item_height
            rect_x = (self.surface.get_width() - style['item_width']) // 2
            rect_y = start_y + menu_index * (item_height + style['item_margin'])
            item_width = self.get_item_width(style, text_width)
            rect_surface = pygame.Surface((item_width, rect_height), pygame.SRCALPHA)
            rect_surface.fill(background_color)
            self.surface.blit(rect_surface, (rect_x, rect_y))

            text_y = rect_y + (rect_height - text_height) // 2
            if style_name == 'mapping':
                text_x = rect_x + style['item_padding'] * 2
                mapping = self.get_mapping(item)
                mapping_text = self.get_mapping_name(mapping)
                mapping_surface = style['font_small'].render(mapping_text, True, MainMenu.ITEM_TEXT_DARK)
                mapping_x = rect_x + style['item_width'] - mapping_surface.get_width() - style['item_padding'] * 2
                mapping_y = rect_y + (rect_height - mapping_surface.get_height()) // 2 + style['mapping_offset']
                self.surface.blit(mapping_surface, (mapping_x, mapping_y))
            else:
                text_x = rect_x + (item_width - text_width) // 2

            self.surface.blit(text_surface, (text_x, text_y + style['text_offset']))

            menu_index += 1

        return None

    def update(self):
        pass

    def has_back_button(self):
        return len(self.parent_menus) > 0

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

    def handle_quit_really(self, keyboard, controller):
        self.stop_music()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                back_key = keyboard.get('back', {}).get('key')
                if event.key == back_key:
                    self.back.play()
                    self.play_music()
                    self.quit = False
                    return

                select_key = keyboard.get('select', {}).get('key')
                if event.key == select_key:
                    self.quit_really = True
                    return

            elif event.type  == pygame.JOYBUTTONDOWN:
                back_button = controller.get('back', {}).get('button')
                if event.button == back_button:
                    self.back.play()
                    self.play_music()
                    self.quit = False
                    return

                select_button = controller.get('select', {}).get('key')
                if event.button == select_button:
                    self.quit_really = True
                    return

            elif event.type == pygame.JOYAXISMOTION:
                back_axis = controller.get('back', {}).get('axis')
                back_value = controller.get('back', {}).get('value')
                if event.axis == back_axis and round(event.value) == back_value:
                    self.back.play()
                    self.play_music()
                    self.quit = False
                    return

                select_axis = controller.get('select', {}).get('axis')
                select_value = controller.get('select', {}).get('value')
                if event.axis == select_axis and round(event.value) == select_value:
                    self.quit_really = True
                    return

            elif event.type == pygame.JOYHATMOTION:
                back_hat = controller.get('back', {}).get('hat')
                back_value = controller.get('back', {}).get('value')
                if event.hat == back_hat and event.value == back_value:
                    self.back.play()
                    self.play_music()
                    self.quit = False
                    return

                select_hat = controller.get('select', {}).get('hat')
                select_value = controller.get('select', {}).get('value')
                if event.hat == select_hat and event.value == select_value:
                    self.quit_really = True
                    return

    def handle_inputs(self):

        keyboard = self.settings.mapping.get('keyboard', {})
        controller = self.settings.mapping.get('controller', {})

        if self.quit:
            self.handle_quit_really(keyboard, controller)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True

            if event.type == pygame.KEYDOWN:
                if self.active_mapping is not None:
                    back_key = keyboard.get('back', {}).get('key')
                    if event.key == back_key:
                        self.active_mapping = None
                        self.back.play()
                        return
                    self.set_mapping(self.active_mapping, event)

                elif event.key == keyboard.get('back', {}).get('key'):
                    self.menu_back_or_quit()

                elif event.key == keyboard.get('up', {}).get('key') or event.key == pygame.K_UP:
                    self.menu_up()

                elif event.key == keyboard.get('down', {}).get('key') or event.key == pygame.K_DOWN:
                    self.menu_down()

                elif event.key == keyboard.get('select', {}).get('key') or event.key == pygame.K_RETURN:
                    self.menu_ok()

            elif event.type  == pygame.JOYBUTTONDOWN:
                if self.active_mapping is not None:
                    back_button = controller.get('back', {}).get('button')
                    if event.button == back_button:
                        self.active_mapping = None
                        self.back.play()
                        return
                    self.set_mapping(self.active_mapping, event)

                elif event.button == controller.get('back', {}).get('button'):
                    self.menu_back_or_quit()

                elif event.button == controller.get('up', {}).get('button'):
                    self.menu_up()

                elif event.button == controller.get('down', {}).get('button'):
                    self.menu_down()

                elif event.button == controller.get('select', {}).get('button'):
                    self.menu_ok()

            elif event.type == pygame.JOYAXISMOTION:
                if self.active_mapping is not None:
                    back_axis = controller.get('back', {}).get('axis')
                    back_value = controller.get('back', {}).get('value')
                    if event.axis == back_axis and round(event.value) == back_value:
                        self.active_mapping = None
                        self.back.play()
                        return
                    self.set_mapping(self.active_mapping, event)

                elif event.axis == controller.get('back', {}).get('axis') and round(event.value) == controller.get('back', {}).get('value'):
                    self.menu_back_or_quit()

                elif event.axis == controller.get('up', {}).get('axis') and round(event.value) == controller.get('up', {}).get('value'):
                    self.menu_up()

                elif event.axis == controller.get('down', {}).get('axis') and round(event.value) == controller.get('down', {}).get('value'):
                    self.menu_down()

                elif event.axis == controller.get('down', {}).get('axis') and round(event.value) == controller.get('select', {}).get('value'):
                    self.menu_ok()

            elif event.type == pygame.JOYHATMOTION:
                if self.active_mapping is not None:
                    back_hat = controller.get('back', {}).get('hat')
                    back_value = controller.get('back', {}).get('value')
                    if event.hat == back_hat and event.value == back_value:
                        self.active_mapping = None
                        self.back.play()
                        return
                    self.set_mapping(self.active_mapping, event)

                elif event.hat == controller.get('back', {}).get('hat') and event.value == controller.get('back', {}).get('value'):
                    self.menu_back_or_quit()

                elif event.hat == controller.get('up', {}).get('hat') and event.value == controller.get('up', {}).get('value'):
                    self.menu_up()

                elif event.hat == controller.get('down', {}).get('hat') and event.value == controller.get('select', {}).get('value'):
                    self.menu_down()

                elif event.hat == controller.get('down', {}).get('hat') and event.value == controller.get('select', {}).get('value'):
                    self.menu_ok()

    def get_selected_item(self):
        return self.active_menu.get('items')[self.selected_item] if self.selected_item >= 0 else {'action': 'back'}

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

    def menu_ok(self):
        selected_item = self.get_selected_item()

        if selected_item.get('action') == 'play':
            self.ok.play()
            self.activate_menu(self.load_maps_menu())

        elif selected_item.get('action') == 'map':
            self.ok.play()
            self.stop_music()
            Game(selected_item.get('map'), self.surface, self.clock, self.settings).game_loop(self)
            self.play_music()

        elif selected_item.get('action') == 'web_link':
            self.ok.play()
            webbrowser.open(selected_item.get('link'))

        elif selected_item.get('action') == 'menu':
            self.ok.play()
            self.activate_menu(selected_item)

        elif selected_item.get('action') == 'back':
            self.menu_back_or_quit()

        elif selected_item.get('action') == 'resolution':
            self.ok.play()
            self.change_resolution(selected_item.get('width'), selected_item.get('height'))

        elif selected_item.get('action') == 'fps':
            self.ok.play()
            self.change_max_fps(selected_item.get('fps'))

        elif selected_item.get('action') == 'switch_fullscreen':
            self.ok.play()
            self.switch_fullscreen()

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
        self.selected_item = menu_item.get('selected_item', 0)

        if menu_item.get('action') == 'menu':
            items = menu_item.get('menu').get('items')
            for item in items:
                if item.get('action') == 'resolution' and self.settings.width == int(item.get('width')) and self.settings.height == int(item.get('height')):
                    self.selected_item = items.index(item)
                    break
                elif item.get('action') == 'fps' and self.settings.max_fps == int(item.get('fps')):
                    self.selected_item = items.index(item)
                    break

    def reload(self):
        display_options = pygame.SCALED
        if self.settings.fullscreen:
            display_options += pygame.FULLSCREEN

        self.surface = pygame.display.set_mode((self.settings.width, self.settings.height), display_options)
        self.splash = self.load_splash()

    def show_mapping(self, menu_item):
        self.active_mapping = menu_item

    def switch_fullscreen(self):
        self.settings.fullscreen = not self.settings.fullscreen
        self.reload()

    def change_resolution(self, width, height):
        self.settings.width = int(width)
        self.settings.height = int(height)
        self.reload()

    def change_max_fps(self, fps):
        self.settings.max_fps = int(fps)
        self.reload()

    def menu_back_or_quit(self):
        if self.active_mapping is not None:
            self.active_mapping = None
            return

        if len(self.parent_menus) > 0:
            self.back.play()
            self.active_menu = self.parent_menus.pop()
            self.selected_item = self.active_menu.get('selected_item', 0)
        else:
            self.quit = True

    def menu_up(self):
        if self.selected_item > (-1 if self.has_back_button() else 0):
            self.selected_item -= 1
            if self.get_selected_item().get('spacer'):
                self.selected_item -= 1
            self.select.play()

    def menu_down(self):
        if self.selected_item < len(self.active_menu.get('items')) - 1:
            self.selected_item += 1
            if self.get_selected_item().get('spacer'):
                self.selected_item += 1
            self.select.play()

    def game_loop(self):
        while True:
            self.handle_inputs()
            self.tick()
            self.update()
            self.draw()
            pygame.display.update()
            if self.quit_really:
                break