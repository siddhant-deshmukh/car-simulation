import arcade 
import math

COLOR_LIGHT = arcade.color_from_hex_string('#D9BBA0')
COLOR_DARK = arcade.color_from_hex_string('#0D0D0D')

class ModalSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int):
        super().__init__(left, bottom, width, height, modal=True, enabled=False)

class InfoBar(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int, **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.steering_wheel = arcade.Sprite('./resources/steering_wheel.png',0.1,center_x= 50,center_y=self.window.height - 50)

    @property
    def car(self):
        return self.view.game_section.player_sprite 
    @property
    def radars(self):
        return self.view.game_section.radars
    @property
    def score(self):
        return self.view.game_section.score
    @property
    def distX(self):
        points_array = self.view.game_section.checkPoints 
        index = self.view.game_section.curr_check_point

        if(len(points_array) <= index or index < 0):
            return -1
        tile_width = self.view.game_section.tile_map.tile_width 
        # point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2
        return self.view.game_section.player_sprite.center_x - points_array[index][0]*tile_width + tile_width/2
    @property
    def distY(self):
        points_array = self.view.game_section.checkPoints 
        index = self.view.game_section.curr_check_point

        if(len(points_array) <= index or index < 0):
            return -1
        
        tile_width = self.view.game_section.tile_map.tile_width  
        # point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2
        return self.view.game_section.player_sprite.center_y - (self.view.game_section.tile_map.height -1 -points_array[index][1])*tile_width + tile_width
    
    
    def on_draw(self):
        # print(self.car.velocity)
        # draw game info
        self.steering_wheel.angle = self.car.steering_angle
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top, 
                                          self.bottom, color=arcade.color.DARK_BROWN)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, COLOR_LIGHT)
        self.steering_wheel.center_x = self.left + 50
        self.steering_wheel.center_y = self.top - 50
        self.steering_wheel.draw()
        # Velocity
        arcade.draw_text(f'Velocity x: {round(self.car.velocity[0],2)}',
                         self.left + self.width / 2, self.top - 15,
                         COLOR_LIGHT,font_size=15)
        arcade.draw_text(f'Velocity y: {round(self.car.velocity[1],2)}',
                         self.left + self.width / 2, self.top -  45,
                         COLOR_LIGHT,font_size=15)
        arcade.draw_text(f'Speed: {round(math.sqrt(self.car.velocity[0]**2 + self.car.velocity[1]**2),2)}',
                         self.left + self.width / 2, self.top -  75,
                         COLOR_LIGHT,font_size=15)
        # Positions
        arcade.draw_text(f'Wheel Angle: {round(self.car.steering_angle ,2)}',
                         self.left + self.width / 2 - 250, self.top -  15,
                         COLOR_LIGHT,font_size=15)
        arcade.draw_text(f'Angle: {round(self.car.angle ,2)}',
                         self.left + self.width / 2 - 250, self.top -  45,
                         COLOR_LIGHT,font_size=15)
        arcade.draw_text(f'Accelerator: {round(self.car.accelerator_angle ,2)}',
                         self.left + self.width / 2 - 250, self.top -  85,
                         COLOR_LIGHT,font_size=15)
        
        # Radars
        arcade.draw_text(f'Raders:',
                         self.left + self.width / 2 + 250, self.top -  15,
                         COLOR_LIGHT,font_size=12)
        arcade.draw_text(f'  Side Left: {round(self.radars[0] ,2)}',
                         self.left + self.width / 2 + 250, self.top -  30,
                         COLOR_LIGHT,font_size=10)
        arcade.draw_text(f'  Side Right: {round(self.radars[4] ,2)}',
                         self.left + self.width / 2 + 250, self.top -  45,
                         COLOR_LIGHT,font_size=10)
        arcade.draw_text(f'  30 Left: {round(self.radars[1] ,2)}',
                         self.left + self.width / 2 + 250, self.top -  60,
                         COLOR_LIGHT,font_size=10)
        arcade.draw_text(f'  30 Right: {round(self.radars[3] ,2)}',
                         self.left + self.width / 2 + 250, self.top -  75,
                         COLOR_LIGHT,font_size=10)
        
        arcade.draw_text(f'  front: {round(self.radars[2] ,2)}',
                         self.left + self.width / 2 + 250, self.top -  90,
                         COLOR_LIGHT,font_size=10)
        
        # Radars
        arcade.draw_text(f' Score: {round(self.score ,2)}',
                         self.left + self.width / 2 + 350, self.top -  30,
                         COLOR_LIGHT,font_size=20)
        arcade.draw_text(f' CheckPoint Dist X: {round(self.distX ,2)}',
                         self.left + self.width / 2 + 350, self.top -  60,
                         COLOR_LIGHT,font_size=12)
        arcade.draw_text(f' CheckPoint Dist Y: {round(self.distY ,2)}',
                         self.left + self.width / 2 + 350, self.top -  75,
                         COLOR_LIGHT,font_size=12)
        
    def on_resize(self, width: int, height: int):
        # stick to the top
        self.width = width
        self.bottom = height - self.view.info_bar.height