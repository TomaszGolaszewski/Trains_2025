# Python Game Engine
# By Tomasz Golaszewski
# under development since 2022

import pygame

from game_engine.scenes_features import *


class SceneBase:
    def __init__(self):
        """Initialization of the scene."""
        self.next = self
    
    def process_input(self, events, keys_pressed):
        """
        Receive all the events that happened since the last frame.
        Handle all received events.
        """
        print("not overwritten process_input")

    def update(self):
        """Game logic for the scene."""
        print("not overwritten update")

    def render(self, win):
        """Draw scene on the screen."""
        print("not overwritten render")

    def switch_scene(self, next_scene):
        """Change scene."""
        self.next = next_scene
    
    def terminate(self):
        """Close the game by changing scene to None."""
        self.switch_scene(None)


# ======================================================================


def run_game(start_scene = SceneBase, win_width: int = 1260, win_height: int = 700, framerate: int = 60, 
                    title_bar: str = "Game by Tomasz", path_to_icon=None):
    """main function - runs the game"""
    
    # initialize the pygame
    pygame.init()

    # set window title bar
    pygame.display.set_caption(title_bar)
    if path_to_icon is not None:
        icon_img = pygame.image.load(path_to_icon)
        pygame.display.set_icon(icon_img)

    # create the window
    win = pygame.display.set_mode((win_width, win_height))
    clock = pygame.time.Clock()
    active_scene = start_scene()
    current_frame = 0
    current_fps = 0
    fps_text = DynamicText((50, 20), "FPS: %.2f" % framerate, 20)

    # main loop
    while active_scene != None:
        # control fps
        clock.tick(framerate)
        current_frame += 1
        if current_frame == framerate:
            current_frame = 0
            
            # print infos about fps and time
            current_fps = clock.get_fps()
            fps_text.set_text("FPS: %.2f" % current_fps)
            seconds_from_start = pygame.time.get_ticks() // 1000
            minuts_from_start = seconds_from_start // 60
            print("FPS: %.2f" % current_fps, end="\t")
            print(f"TIME: {seconds_from_start}s ({minuts_from_start}min)")
        
        # event filtering
        keys_pressed = pygame.key.get_pressed()
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = keys_pressed[pygame.K_LALT] or \
                              keys_pressed[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
            
            if quit_attempt:
                active_scene.terminate()
            else:
                filtered_events.append(event)
        
        # handling events, mouse and keyboard
        active_scene.process_input(filtered_events, keys_pressed)

        # run simulation
        active_scene.update()

        # draw scene on the screen
        active_scene.render(win)
        
        # jump to next scene (or to self)
        active_scene = active_scene.next
        
        # draw FPS  
        fps_text.draw(win)   

        # flip the screen
        pygame.display.flip()