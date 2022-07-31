import pygame
from pygame import mixer

from debug import *
from strings import *
from assets import *
from player import Player
from utils import *
from user_interface import *
from level import *
from database_helper import DatabaseHelper


# TODO: mixer.find_channel()

class Game:

    def __init__(self):
        pygame.init()
        mixer.init()

        # When True, game will end:
        self.done = False

        # A helper for the relational database:
        self.database_helper = DatabaseHelper(self)

        # Getting the current resolution of the physical screen:
        screen_info = pygame.display.Info()
        self.resolution = [screen_info.current_w, screen_info.current_h]
        self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        self.rect = self.screen.get_rect()
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()

        # Calculating window dimensions - this is an arbitrary unit to make everything fully resolution independent:
        if self.resolution[0] > self.resolution[1]:
            self.window_dimensions = [1 + self.resolution[1] / self.resolution[0], 1]
        else:
            self.window_dimensions = [1, 1 + self.resolution[1] / self.resolution[0]]

        self.frame_rate = None
        self.show_frame_rate = None
        self.audio_volume = None
        self.current_level = None
        self.refresh_settings()

        # Setting up display:
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()

        # The font of the game:
        self.font = FONT

        self.all_events = []
        self.key_down_events = []
        self.start_game()

    def refresh_settings(self):
        # Getting the frame rate cap setting from the database:
        self.frame_rate = int(self.database_helper.get_setting(DatabaseHelper.FRAME_RATE_LIMIT))

        # Getting whether the frame rate should be displayed at the corner of the screen:
        self.show_frame_rate = self.database_helper.get_setting(DatabaseHelper.SHOW_FRAME_RATE)

        # Getting the audio volume level:
        self.audio_volume = self.database_helper.get_setting(DatabaseHelper.AUDIO_VOLUME)

        # Setting up level:
        level_id = self.database_helper.get_player_stats()[Player.CURRENT_LEVEL_ID]
        self.current_level = Level(self, level_id)

    def start_game(self):
        self.show_main_menu()

    def update(self):
        self.get_input()

        if self.show_frame_rate:
            fps_text = TextLine(self,
                                str(int(self.clock.get_fps())),
                                font_size=0.04)
            fps_text.get_rect().topleft = self.rect.topleft
            fps_text.draw()

    def quit(self):
        self.done = True

    def get_current_level(self):
        return self.current_level

    def get_database_helper(self):
        return self.database_helper

    def get_current_frame_rate(self):
        return self.clock.get_fps()

    def get_current_frame_time(self):
        return 1 / self.clock.get_fps()

    def get_frame_rate_cap(self):
        return self.frame_rate

    def set_frame_rate_cap(self, frame_rate):
        self.frame_rate = frame_rate
        self.database_helper.update_setting(DatabaseHelper.FRAME_RATE_LIMIT, frame_rate)

    def get_show_frame_rate(self):
        return self.show_frame_rate

    def set_show_frame_rate(self, value):
        self.show_frame_rate = value
        self.database_helper.update_setting(DatabaseHelper.SHOW_FRAME_RATE, value)

    def get_audio_volume(self):
        return self.audio_volume

    def set_audio_volume(self, audio_volume):
        self.audio_volume = audio_volume
        self.database_helper.update_setting(DatabaseHelper.AUDIO_VOLUME, audio_volume)
        mixer.music.set_volume(audio_volume)

    def get_key_down_events(self):
        return self.key_down_events

    def get_input(self):
        self.all_events = pygame.event.get()
        self.key_down_events = []

        for event in self.all_events:
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                self.key_down_events.append(event.key)

    def key_pressed(self, key_id):
        for key_input in self.key_down_events:
            if key_input == key_id: return True
        return False

    def mouse_pressed(self):
        for event in self.all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
        return False

    def mouse_released(self):
        for event in self.all_events:
            if event.type == pygame.MOUSEBUTTONUP:
                return True
        return False

    def get_rect(self):
        return self.rect

    def unit_to_pixel(self, value):
        # Conversion between pixels and arbitrary units:
        return int(value * (self.resolution[0] / self.window_dimensions[0]))

    def unit_to_pixel_point(self, values):
        return int(values[0] * (self.resolution[0] / self.window_dimensions[0])), \
               int(values[1] * (self.resolution[0] / self.window_dimensions[0]))

    def pixel_to_unit(self, value):
        return value / (self.resolution[0] / self.window_dimensions[0])

    def pixel_to_unit_point(self, values):
        return values[0] / (self.resolution[0] / self.window_dimensions[0]), \
               values[1] / (self.resolution[0] / self.window_dimensions[0])

    def get_font(self, size):
        # The size of the font in arbitrary units:
        return pygame.font.SysFont(self.font, size)

    def show_main_menu(self):
        views = []

        # Play Button:
        btn_play = Button(self,
                          text_string=PLAY_GAME,
                          position=self.rect.center)
        views.append(btn_play)

        # Settings Button:
        btn_settings = Button(self,
                              text_string=SETTINGS,
                              below=btn_play)
        views.append(btn_settings)

        # Quit Button:
        btn_quit = Button(self,
                          text_string=QUIT,
                          below=btn_settings)
        views.append(btn_quit)

        # Title Text
        txt_title = TextLine(self,
                             text_string=GAME_NAME,
                             centre_between=(self.rect.midtop,
                                             btn_play.get_rect().midtop),
                             frame_condition=View.ALWAYS,
                             font_size=0.25)
        txt_title.set_italic(True)
        views.append(txt_title)

        while not self.done:
            self.screen.fill(WHITE)

            if self.key_pressed(pygame.K_1):
                self.testing()

            # On Click:
            if btn_play.clicked():
                if self.database_helper.get_player_stats()[Player.FULL_HEALTH] == 0:
                    self.show_character_menu()
                self.show_game()
            elif btn_settings.clicked(): self.show_settings_menu()
            elif btn_quit.clicked(): self.quit()

            for view in views: view.draw()
            self.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_settings_menu(self):
        views = []

        # Show Frame Rate Selector:
        if self.show_frame_rate: start_index = 1
        else: start_index = 0

        sel_show_frame_rate = Selector(self,
                                       font_size=0.04,
                                       start_index=start_index,
                                       position=self.rect.center,
                                       margin=0.015)
        views.append(sel_show_frame_rate)

        # Show Frame Rate Text:
        txt_show_frame_rate = TextLine(self, SHOW_FRAME_RATE,
                                       font_size=0.04,
                                       to_left_of=sel_show_frame_rate,
                                       margin=0.015)
        views.append(txt_show_frame_rate)

        # Max Frame Rate Input:
        edt_txt_frame_rate = TextInput(self,
                                       font_size=0.04,
                                       hint=str(self.frame_rate),
                                       clear_on_focus=True,
                                       input_type=TextInput.INTEGER,
                                       max_length=3,
                                       above=sel_show_frame_rate,
                                       margin=0.015)
        views.append(edt_txt_frame_rate)

        # Frame Rate Text:
        txt_frame_rate = TextLine(self, FRAME_RATE_LIMIT,
                                  font_size=0.04,
                                  to_left_of=edt_txt_frame_rate,
                                  margin=0.015)
        views.append(txt_frame_rate)

        # Resolution Value Text:
        txt_resolution_value = TextLine(self, RESOLUTION_FORMAT.format(*self.resolution),
                                        font_size=0.04,
                                        above=edt_txt_frame_rate,
                                        frame_condition=View.ALWAYS,
                                        margin=0.015)
        views.append(txt_resolution_value)

        # Resolution Text:
        txt_resolution = TextLine(self, RESOLUTION,
                                  font_size=0.04,
                                  to_left_of=txt_resolution_value,
                                  margin=0.015)
        views.append(txt_resolution)

        # Audio Volume Slider:
        sl_audio_volume = Slider(self,
                                 below=sel_show_frame_rate,
                                 start_value=[self.audio_volume, 0],
                                 margin=0.015)
        views.append(sl_audio_volume)

        # Audio Volume Text:
        txt_audio_volume = TextLine(self, AUDIO_VOLUME,
                                    font_size=0.04,
                                    to_left_of=sl_audio_volume,
                                    margin=0.015)
        views.append(txt_audio_volume)

        # Settings Text:
        txt_settings = TextLine(self, SETTINGS,
                                centre_between=(self.rect.midtop,
                                                txt_resolution_value.get_rect().midtop),
                                margin=0.015)

        views.append(txt_settings)

        # Delete Save Data Button:
        btn_delete_saves = Button(self, text_string=DELETE_SAVES,
                                  font_size=0.025,
                                  text_hover_colour=RED,
                                  frame_hover_colour=RED,
                                  margin=0.015)
        btn_delete_saves.get_rect().midbottom = self.rect.midbottom + pygame.Vector2(0, -btn_delete_saves.get_margin())
        views.append(btn_delete_saves)

        # Save & Exit Button:
        btn_exit = Button(self,
                          text_string=BACK,
                          font_size=0.04,
                          centre_between=(sl_audio_volume.get_rect().midbottom,
                                          btn_delete_saves.get_rect().midtop),
                          margin=0.015)
        views.append(btn_exit)

        while not self.done:
            self.screen.fill(WHITE)

            # If the refresh rate has been changed and the input is not empty, set it to the attribute:
            if edt_txt_frame_rate.unfocused() and not edt_txt_frame_rate.input_empty():
                frame_rate = int(edt_txt_frame_rate.get_text())
                self.set_frame_rate_cap(frame_rate)

            # Changing the frame rate display if the frame rate selector is clicked:
            if sel_show_frame_rate.clicked():
                self.set_show_frame_rate(sel_show_frame_rate.get_state() == ON)

            # If the audio volume slider has been changed:
            if sl_audio_volume.handle_released():
                self.set_audio_volume(sl_audio_volume.get_value()[0])

            # Exit if exit button or escape clicked:
            if btn_exit.clicked() or self.key_pressed(pygame.K_ESCAPE):
                return

            # If the delete saves button is clicked, deleting saves:
            if btn_delete_saves.clicked():
                self.database_helper.delete_saves()
                self.refresh_settings()
                return

            for view in views: view.draw()
            self.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def testing(self):
        views = []
        txt_1 = TextLine(self, "TESTING",
                         position=self.rect.center,
                         frame_condition=View.ALWAYS,
                         margin=0)
        views.append(txt_1)

        btn_2 = Button(self, text_string="2",
                       to_left_of=txt_1)
        views.append(btn_2)

        btn_1 = Button(self, text_string="1",
                       to_left_of=btn_2)
        views.append(btn_1)

        sl_1 = Slider(self,
                      bar_size=(0.1, 0.1),
                      below=btn_1,
                      slide_vertical=True,
                      slide_horizontal=True)
        views.append(sl_1)

        btn_3 = Button(self,
                       icon=pygame.image.load("../assets/images/icons/speed.png"),
                       padding=0.1)
        btn_3.get_rect().midright = self.rect.midright
        views.append(btn_3)

        sl_2 = Slider(self,
                      to_right_of=sl_1)
        views.append(sl_2)

        txt_2 = TextLine(self, "...",
                         to_right_of=sl_2,
                         font_size=0.04,
                         frame_condition=View.ALWAYS)
        views.append(txt_2)

        txt_3 = TextLine(self, "...",
                         to_right_of=txt_2,
                         font_size=0.02,
                         frame_condition=View.ALWAYS)
        views.append(txt_3)

        edt_txt_1 = TextInput(self,
                              hint="Input Here",
                              above=txt_1,
                              clear_on_focus=True,
                              max_length=15)
        views.append(edt_txt_1)

        edt_txt_2 = TextInput(self,
                              hint="Input Here",
                              to_right_of=edt_txt_1,
                              clear_on_focus=True,
                              max_length=15)
        views.append(edt_txt_2)

        while not self.done:
            self.screen.fill(WHITE)
            if self.key_pressed(pygame.K_ESCAPE): return

            if btn_1.clicked():
                txt_2.set_text("Will Item To Right Move?")
            if btn_2.clicked():
                txt_3.set_text("Testing UI Element Movement...")

            if sl_1.handle_is_held():
                txt_2.set_text(sl_1.get_value())
            if sl_2.handle_is_held():
                txt_3.set_text(sl_2.get_value())

            for view in views: view.draw()
            self.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_character_menu(self):
        views = []

        sl_stats = Slider(self, bar_size=[0.3, 0.3],
                          start_value=[0.5, 0.5],
                          centre_between=(self.rect.center, self.rect.midleft),
                          slide_horizontal=True,
                          slide_vertical=True,
                          padding=0,
                          margin=0)
        views.append(sl_stats)

        img_health = Image(self, icon=pygame.image.load(HEALTH_ICON).convert_alpha(),
                           above=sl_stats,
                           frame_condition=1)
        views.append(img_health)

        img_speed = Image(self, icon=pygame.image.load(SPEED_ICON).convert_alpha(),
                          below=sl_stats,
                          frame_condition=1)
        views.append(img_speed)

        img_attack_damage = Image(self, icon=pygame.image.load(ATTACK_DAMAGE_ICON).convert_alpha(),
                                  to_left_of=sl_stats,
                                  frame_condition=1)
        views.append(img_attack_damage)

        img_magic_damage = Image(self, icon=pygame.image.load(MAGIC_DAMAGE_ICON).convert_alpha(),
                                 to_right_of=sl_stats,
                                 frame_condition=1)
        views.append(img_magic_damage)

        slider_values = sl_stats.get_value()
        health = round(Player.MIN_HEALTH + (Player.MAX_HEALTH - Player.MIN_HEALTH) * slider_values[1], 2)
        movement = round(Player.MIN_SPEED + (Player.MAX_SPEED - Player.MIN_SPEED) * (1 - slider_values[1]), 2)
        magic = round(Player.MIN_MAGIC + (Player.MAX_MAGIC - Player.MIN_MAGIC) * slider_values[0], 2)
        attack = round(Player.MIN_ATTACK + (Player.MAX_ATTACK - Player.MIN_ATTACK) * (1 - slider_values[0]), 2)

        txt_stats = Text(self, CHARACTER_STATS.format(int(health * 100),
                                                      int(movement * 100),
                                                      int(attack * 100),
                                                      int(magic * 100)),
                         centre_between=(self.rect.center, self.rect.midright),
                         font_size=0.065)
        views.append(txt_stats)

        txt_warning = TextLine(self, ENTER_CHARACTER_NAME,
                               visible=False,
                               position=(0, 0),
                               font_size=0.04,
                               below=txt_stats,
                               margin=0,
                               frame_condition=View.ALWAYS,
                               text_colour=RED,
                               frame_colour=RED)
        views.append(txt_warning)

        btn_continue = Button(self, text_string=CONTINUE,
                              below=txt_warning)
        views.append(btn_continue)

        edt_txt_player_name = TextInput(self,
                                        max_length=20,
                                        hint=CHARACTER_NAME,
                                        above=txt_stats)
        views.append(edt_txt_player_name)

        while not self.done:
            self.screen.fill(WHITE)

            if self.key_pressed(pygame.K_ESCAPE):
                return

            if sl_stats.handle_held:
                slider_values = sl_stats.get_value()
                health = round(Player.MIN_HEALTH + (Player.MAX_HEALTH - Player.MIN_HEALTH) * slider_values[1], 2)
                movement = round(Player.MIN_SPEED + (Player.MAX_SPEED - Player.MIN_SPEED) * (1 - slider_values[1]), 2)
                magic = round(Player.MIN_MAGIC + (Player.MAX_MAGIC - Player.MIN_MAGIC) * slider_values[0], 2)
                attack = round(Player.MIN_ATTACK + (Player.MAX_ATTACK - Player.MIN_ATTACK) * (1 - slider_values[0]), 2)
                txt_stats.set_text(CHARACTER_STATS.format(int(health * 100),
                                                          int(movement * 100),
                                                          int(attack * 100),
                                                          int(magic * 100)))

            if btn_continue.clicked():
                if edt_txt_player_name.input_empty():
                    txt_warning.set_visibility(True)
                else:
                    self.database_helper.update_player_stats({Player.FULL_HEALTH: health,
                                                              Player.CURRENT_HEALTH: health,
                                                              Player.SPEED_MULTIPLIER: movement,
                                                              Player.MELEE_DAMAGE_MULTIPLIER: attack,
                                                              Player.MAGIC_DAMAGE_MULTIPLIER: magic})
                    self.current_level.refresh_player()
                    return

            if txt_warning.clicked():
                txt_warning.set_visibility(False)

            for view in views: view.draw()
            self.update()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_inventory(self):
        player = self.current_level.get_player()

        views = []

        img_current_weapon = Image(self, icon=player.get_item_selected().get_icon(),
                                   centre_between=(self.rect.center, self.rect.midright),
                                   size=(0.2, 0.2),
                                   padding=0.01,
                                   frame_condition=View.ALWAYS)
        views.append(img_current_weapon)

        while not self.done:
            self.screen.fill(WHITE)

            if self.key_pressed(pygame.K_ESCAPE): return

            self.update()
            for view in views: view.draw()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def show_game(self):
        background_colour = self.current_level.get_background_colour()
        self.current_level.set_up_map()

        player = self.current_level.get_player()

        views = []

        btn_pause = Button(self, icon=pygame.image.load(PAUSE_ICON).convert_alpha(),
                           size=(0.05, 0.05),
                           padding=0.01,
                           frame_condition=View.ALWAYS)
        btn_pause.get_rect().topright = self.rect.topright + pygame.Vector2(-btn_pause.get_margin(),
                                                                            btn_pause.get_margin())
        views.append(btn_pause)

        btn_switch = Button(self, icon=pygame.image.load(SWITCH_ICON).convert_alpha(),
                            size=(0.05, 0.05),
                            padding=0.01,
                            frame_condition=View.ALWAYS)
        btn_switch.get_rect().midright = self.rect.midright + pygame.Vector2(-btn_switch.get_margin(), 0)
        views.append(btn_switch)

        btn_use = Button(self, icon=player.get_item_selected().get_icon(),
                         below=btn_switch,
                         size=(0.05, 0.05),
                         padding=0.01,
                         frame_condition=View.ALWAYS)
        views.append(btn_use)

        # TODO: SHOW QUANTITY

        while not self.done:
            self.screen.fill(background_colour)

            if self.key_pressed(pygame.K_ESCAPE) or btn_pause.clicked(): return

            if self.key_pressed(pygame.K_TAB) or btn_switch.clicked():
                player.increment_item_selected()
                # After switching item, the icon needs to be updated:
                btn_use.set_icon(player.get_item_selected().get_icon())

            if btn_use.clicked():
                player.use_item()

            self.current_level.update()
            self.update()

            # Only drawing view elements if enabled:

            for view in views: view.draw()
            pygame.display.flip()
            self.clock.tick(self.frame_rate)


Game()
