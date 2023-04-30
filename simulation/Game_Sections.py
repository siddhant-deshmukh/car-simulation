import arcade 
import math
from simulation import Car

CHARACTER_SCALING=1
TILE_SCALING=1
CAR_ROTATION_SPEED = 2

GRAVITY = 0
PLAYER_JUMP_SPEED = 20
ACCELERATION_ON_BREAK = -0.09
ACCELERATION_ON_NOTHING = -0.01
ACCELERATION_ON_GEAR_CONSTANT = 0.03
MAX_VELOCITY = 5
MAX_ACCELERATION = 0.5
MIN_VELOCITY = 0.05

class GameMap(arcade.Section):
    def __init__(self, car_img_resource, map_resource, left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.scene = None
        self.tile_map = None

        self.player_sprite=None 

        self.physics_engine = None 
        self.camera = None

        # self.mode = 0
        self.acceleration = 0
        self.velocity = 0

        self.car_img_resource = car_img_resource
        self.map_resource = map_resource
        
        self.acceleration_key = ''
        self.turning_key = ''
        
    def setup(self):
        self.setup_camera()
        self.setup_scene()
        
    def setup_camera(self):
        self.camera = arcade.Camera(self.width, self.height)
    def setup_scene(self):
        self.scene = arcade.Scene()
        image_source = self.car_img_resource

        self.player_sprite = Car.PlayerCar(image_source,CHARACTER_SCALING,center_x=50,center_y=160)

        self.scene.add_sprite('Player',self.player_sprite)

        map_name = self.map_resource
        if(map_name == None):
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, gravity_constant=0
            )
        else:
            layer_options = {
                "road_edges": {
                    "use_spatial_hash": True,
                },
            }
            self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
            # if self.tile_map.background_color:
            #     arcade.set_background_color(self.tile_map.background_color)

            self.scene.add_sprite('Player',self.player_sprite)
        
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, gravity_constant=0, walls=self.scene["road_edges"]
            )
        
    def on_draw(self):
        self.scene.draw()
        if(self.camera != None):
            self.camera.use()

    def center_camera_to_player(self):
        
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        # if self.player_sprite.center_x < 0 + (self.camera.viewport_width / 2):
        #     screen_center_x = 0
        if screen_center_x > self.tile_map.width*self.tile_map.tile_width - 2*(self.camera.viewport_width / 2):
            screen_center_x = self.tile_map.width*self.tile_map.tile_width  - (self.camera.viewport_width)
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_y > self.tile_map.height*self.tile_map.tile_height - 2*(self.camera.viewport_height / 2):
            screen_center_y = self.tile_map.height*self.tile_map.tile_height  - (self.camera.viewport_height)
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE :
            self.acceleration_key = 'BRAKE'
        elif key == arcade.key.UP or key == arcade.key.W:
            self.acceleration_key = 'UP'
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.acceleration_key = 'DOWN'

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.turning_key = 'LEFT'
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.turning_key = 'RIGHT'

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key==arcade.key.W or key == arcade.key.DOWN or key == arcade.key.SPACE or key==arcade.key.S:
            self.acceleration_key = ''
        if key == arcade.key.LEFT or key == arcade.key.A or key == arcade.key.D or key == arcade.key.RIGHT:
            self.turning_key = ''

    # def move_car_mode(self):

    #     if self.mode == 0:  #break
    #         if self.velocity > MIN_VELOCITY:
    #             self.acceleration = ACCELERATION_ON_BREAK
    #             self.velocity += self.acceleration 
    #         else:
    #             self.acceleration = 0
    #             self.velocity = 0
    #     elif self.mode == 1: #acceleration
    #         # print(self.player_sprite.angle)

    #         if self.acceleration < 0 :
    #             self.acceleration = 0
    #         self.acceleration += ACCELERATION_ON_GEAR_CONSTANT
    #         self.velocity += self.acceleration 
    #         if self.acceleration > MAX_ACCELERATION:
    #             self.acceleration = MAX_ACCELERATION
    #         if self.velocity > MAX_VELOCITY:
    #             self.velocity = MAX_VELOCITY 
    #     else: #stoped acceleration
    #         self.acceleration = ACCELERATION_ON_NOTHING
    #         self.velocity += self.acceleration 
    #         if self.velocity < MIN_VELOCITY:
    #             self.velocity = 0
                
    #     self.player_sprite.change_x = self.velocity * -1*math.sin(self.player_sprite.radians)
    #     self.player_sprite.change_y = self.velocity * 1*math.cos(self.player_sprite.radians) 
        
    #     self.restrict_movement()

        
    def restrict_movement(self):
        if (self.player_sprite.center_x + self.player_sprite.change_x + self.player_sprite.height > self.tile_map.width*self.tile_map.tile_width ) or (self.player_sprite.center_x + self.player_sprite.change_x - self.player_sprite.height< 0 ):
            self.player_sprite.change_x = 0
        
        if (self.player_sprite.center_y + self.player_sprite.change_y + self.player_sprite.height > self.tile_map.height*self.tile_map.tile_height ) or (self.player_sprite.center_y + self.player_sprite.change_y - self.player_sprite.height < 0 ):
            self.player_sprite.change_y = 0

    def on_update(self, delta_time: float):
        # self.move_car_mode()
        self.player_sprite.control_key_turn(self.turning_key)
        self.player_sprite.control_key_acc(self.acceleration_key)
        self.restrict_movement()
        
        self.physics_engine.update()
        self.center_camera_to_player()
        
class CollegeMap(GameMap):
    def __init__(self,left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__("./resources/car.png","./resources/map-car-simulation.json",left, bottom, width, height, **kwargs)


class EmptyMap(GameMap):
    def __init__(self, left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__("./resources/car.png",None,left, bottom, width, height, **kwargs)
    def center_camera_to_player(self):
        pass
    def restrict_movement(self):
        if (self.player_sprite.center_x > self.width ):
            self.player_sprite.center_x = 0
        elif (self.player_sprite.center_x < 0 ):
            self.player_sprite.center_x = self.width

        if (self.player_sprite.center_y > self.height ):
            self.player_sprite.center_y = 0
        elif (self.player_sprite.center_y < 0):
            self.player_sprite.center_y = self.height

