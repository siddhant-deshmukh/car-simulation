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

    def on_draw(self):
        # print(self.car.velocity)
        # draw game info
        self.steering_wheel.angle = self.car.steering_angle
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top,
                                          self.bottom, color=arcade.color.DARK_BROWN)
        arcade.draw_lrtb_rectangle_outline(self.left, self.right, self.top,
                                           self.bottom, COLOR_LIGHT)
        self.steering_wheel.draw()
        arcade.draw_text(f'Velocity x: {round(self.car.velocity[0],2)}',
                         self.left + self.width / 2, self.top - 25,
                         COLOR_LIGHT,font_size=20)
        arcade.draw_text(f'Velocity y: {round(self.car.velocity[1],2)}',
                         self.left + self.width / 2, self.top -  65,
                         COLOR_LIGHT,font_size=20)
        arcade.draw_text(f'Speed: {round(math.sqrt(self.car.velocity[0]**2 + self.car.velocity[1]**2),2)}',
                         self.left + self.width / 2 + 250, self.top -  25,
                         COLOR_LIGHT,font_size=20)
        arcade.draw_text(f'Speed: {round(self.view.game_section.acceleration ,2)}',
                         self.left + self.width / 2 + 250, self.top -  65,
                         COLOR_LIGHT,font_size=20)
        # arcade.draw_text(f'Center x: {round(self.car.center_x,2)}',
        #                  self.left + self.width / 2 + 250, self.top -  20,
        #                  COLOR_LIGHT)
        # arcade.draw_text(f'Center y: {round(self.car.center_y,2)}',
        #                  self.left + self.width / 2 + 250, self.top -  40,
        #                  COLOR_LIGHT)

        # ball_change_axis = self.ball.change_x, self.ball.change_y
        # arcade.draw_text(f'Ball change in axis: {ball_change_axis}',
        #                  self.left + 220, self.top - self.height / 1.6,
        #                  COLOR_LIGHT)
        # arcade.draw_text(f'Ball speed: {self.ball.speed} pixels/second',
        #                  self.left + 480, self.top - self.height / 1.6,
        #                  COLOR_LIGHT)

    def on_resize(self, width: int, height: int):
        # stick to the top
        self.width = width
        self.bottom = height - self.view.info_bar.height