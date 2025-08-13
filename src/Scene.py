import pygame
from abc import ABC, abstractmethod
from typing import final
from src.Settings import Settings


class GameScene(ABC):

    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock, settings: Settings):
        self.surface: pygame.Surface = surface
        self.clock: pygame.time.Clock = clock
        self.settings: Settings = settings
        self.delta_time: float = 0.0
        self.next_scene = None
        self.quit = False
        self.keyboard = self.settings.mapping.get('keyboard', {})
        self.controller = self.settings.mapping.get('controller', {})

        self.controllers: list[pygame.joystick.Joystick] = []
        pygame.joystick.init()
        for i in range(0, pygame.joystick.get_count()):
            controller = pygame.joystick.Joystick(i)
            self.controllers.append(controller)

    @final
    def set_next_scene(self, next_scene):
        self.next_scene = next_scene

    @abstractmethod
    def game_loop(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    @final
    def set_quit(self, key_down: bool = True):
        if key_down:
            self.quit = True

    @abstractmethod
    def init_input_mappings(self):
        pass

    def handle_events(self, mappings: dict, quit_callback: callable = None):

        for event in pygame.event.get():
            if event.type == pygame.QUIT and quit_callback is not None:
                quit_callback()
                break

            for mapping, callback in mappings.items():

                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    mapped_key = self.keyboard.get(mapping, {}).get('key')
                    if event.key == mapped_key or event.key == mapping:
                        callback(event.type == pygame.KEYDOWN, event)
                        break

                    mapped_mod = self.keyboard.get(mapping, {}).get('mod')
                    if mapped_mod and (event.mod & mapped_mod or (isinstance(mapping, int) and event.mod & mapping)):
                        callback(event.type == pygame.KEYDOWN, event)
                        break

                elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    mapped_button = self.controller.get(mapping, {}).get('button')
                    if event.button == mapped_button or event.button == mapping:
                        callback(event.type == pygame.JOYBUTTONDOWN, event)
                        break

                elif event.type == pygame.JOYAXISMOTION:
                    mapped_axis = self.controller.get(mapping, {}).get('axis')
                    mapped_value = self.controller.get(mapping, {}).get('value')
                    if event.axis == mapped_axis:
                        callback(round(event.value) == mapped_value, event)
                        break

                elif event.type == pygame.JOYHATMOTION:
                    mapped_hat = self.controller.get(mapping, {}).get('hat')
                    mapped_value = self.controller.get(mapping, {}).get('value')
                    if event.hat == mapped_hat:
                        callback(event.value == mapped_value, event)
                        break

                elif (mapping == pygame.MOUSEBUTTONDOWN and event.type == pygame.MOUSEBUTTONDOWN
                    or mapping == pygame.MOUSEBUTTONUP and event.type == pygame.MOUSEBUTTONUP
                    or mapping == pygame.MOUSEWHEEL and event.type == pygame.MOUSEWHEEL
                    or mapping == pygame.MOUSEMOTION and event.type == pygame.MOUSEMOTION):
                    callback(event)

                elif '*' == mapping and event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
                    callback(event)
                    break
