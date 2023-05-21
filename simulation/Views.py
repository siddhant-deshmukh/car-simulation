"""
Example code showing how to create a button,
and the three ways to process button events.
"""
import arcade
import arcade.gui
from simulation import Car, Game_Sections, Other_Sections
import math

INFO_BAR_HEIGHT = 100

# --- Method 1 for handling click events,
# Create a child class.
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class MyView(arcade.View):
    def __init__(self):
        super().__init__()

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create a text label
        ui_text_label = arcade.gui.UITextArea(text="Car Simulation",
                                              width=450,
                                              height=40,
                                              font_size=24,
                                              font_name="Kenney Future")
        self.v_box.add(ui_text_label.with_space_around(bottom=0))

        text = "Select a map!"
        ui_text_label = arcade.gui.UITextArea(text=text,
                                              width=450,
                                              height=60,
                                              font_size=20,
                                              font_name="Arial")
        self.v_box.add(ui_text_label.with_space_around(bottom=0))

        # Create the buttons
        clg_map_btn = arcade.gui.UIFlatButton(text="College Map", width=200)
        self.v_box.add(clg_map_btn.with_space_around(bottom=20))

        simple_map_btn = arcade.gui.UIFlatButton(text="Simple Map", width=200)
        self.v_box.add(simple_map_btn.with_space_around(bottom=20))

        empty_map_btn = arcade.gui.UIFlatButton(text="Empty Map", width=200)
        self.v_box.add(empty_map_btn.with_space_around(bottom=50))

        simple_map_btn_AI = arcade.gui.UIFlatButton(text="Simple AI", width=200)
        self.v_box.add(simple_map_btn_AI.with_space_around(bottom=20))

        # Again, method 1. Use a child class to handle events.
        quit_button = QuitButton(text="Quit", width=100)
        self.v_box.add(quit_button)

        # --- Method 2 for handling click events,
        # assign self.on_select_clg as callback
        clg_map_btn.on_click   = self.on_select_clg
        empty_map_btn.on_click = self.on_select_empty
        simple_map_btn.on_click = self.on_select_simple
        simple_map_btn_AI.on_click = self.on_select_simple_ai
        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_select_clg(self, event):
        game = MyGame('college')
        game.setup()
        self.window.show_view(game)
    def on_select_simple(self, event):
        game = MyGame('simple')
        game.setup()
        self.window.show_view(game)

    def on_select_simple_ai(self, event):
        game = MyGame('simple_ai')
        game.setup()
        self.window.show_view(game)

    def on_select_empty(self,event):
        game = MyGame('empty')
        game.setup()
        self.window.show_view(game)

    def on_draw(self):
        self.clear()
        self.manager.draw()

class MyGame(arcade.View):
    def __init__(self, map_type):
        # super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True) 
        super().__init__() 
        
        self.info_bar = Other_Sections.InfoBar(0, self.window.height - INFO_BAR_HEIGHT,
                                self.window.width, INFO_BAR_HEIGHT,
                                accept_keyboard_events=False)
        
        self.game_section : arcade.Section = Game_Sections.CollegeMap(0, 0, self.window.width, self.window.height - INFO_BAR_HEIGHT)
        if(map_type == 'college'):
            self.game_section = Game_Sections.CollegeMap(0, 0, self.window.width, self.window.height - INFO_BAR_HEIGHT)
        elif(map_type == 'simple'):
            self.game_section = Game_Sections.SimpleMap(0, 0, self.window.width, self.window.height - INFO_BAR_HEIGHT)
        elif(map_type == 'simple_ai'):
            self.game_section = Game_Sections.SimpleMapAI(0, 0, self.window.width, self.window.height - INFO_BAR_HEIGHT)
        else:
            self.game_section = Game_Sections.EmptyMap(0, 0, self.window.width, self.window.height - INFO_BAR_HEIGHT)
            

        # self.player_list = None 
        # self.wall_list = None 

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.game_section.setup()
        self.section_manager.add_section(self.game_section)
        self.section_manager.add_section(self.info_bar)

    def on_resize(self, width: int, height: int):
        self.game_section.width = width
        self.game_section.height = height

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()

    def on_update(self, delta_time: float):
        pass

# window = MyWindow()
# arcade.run()