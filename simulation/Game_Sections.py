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
ACCELERATION_ON_GEAR_CONSTANT = 0.005
MAX_VELOCITY = 5
MAX_ACCELERATION = 0.5
MIN_VELOCITY = 0.05

class CollegeMap(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.scene = None
        self.tile_map = None

        self.player_sprite=None 

        self.physics_engine = None 
        self.camera = None

        self.mode = 0
        self.acceleration = 0
        self.velocity = 0
    def setup(self):
        # self.player_list = arcade.SpriteList()
        # #use_spatial_hash detect collisons faster but slows down speed (ideal for static object like walls)
        # self.wall_list = arcade.SpriteList(use_spatial_hash=True) 
        self.scene = arcade.Scene()
        # self.scene.add_sprite_list('Player')
        # self.scene.add_sprite_list('Walls', use_spatial_hash=True)

        self.camera = arcade.Camera(self.width, self.height)
        # print(self.width, self.height)
        map_name = "./resources/map-car-simulation.json"
        layer_options = {
            "road_edges": {
                "use_spatial_hash": True,
            },
        }
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        image_source = "./resources/car.png"

        self.player_sprite = Car.PlayerCar(image_source,CHARACTER_SCALING,center_x=20,center_y=160)

        self.scene.add_sprite('Player',self.player_sprite)

        
        

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=0, walls=self.scene["road_edges"]
        )
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        #     self.player_sprite, gravity_constant=0
        # )

    def on_draw(self):
        # self.clear()
        # self.wall_list.draw()
        # self.player_list.draw()
        self.scene.draw()
        self.camera.use()

        # return super().on_draw()
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
        if key == arcade.key.UP or key == arcade.key.W:
            self.mode = 1
        elif key == arcade.key.DOWN or key == arcade.key.SPACE:
            self.mode = 0
        # if key == arcade.key.DOWN or key == arcade.key.S:
        #     self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_angle = CAR_ROTATION_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_angle = -CAR_ROTATION_SPEED

        # return super().on_key_press(symbol, modifiers)
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.DOWN or key == arcade.key.SPACE:
            self.mode = 2
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_angle = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_angle = 0

    def move_car_mode(self):

        if self.mode == 0:  #break
            if self.velocity > MIN_VELOCITY:
                self.acceleration = ACCELERATION_ON_BREAK
                self.velocity += self.acceleration 
            else:
                self.acceleration = 0
                self.velocity = 0
        elif self.mode == 1: #acceleration
            # print(self.player_sprite.angle)

            if self.acceleration < 0 :
                self.acceleration = 0
            self.acceleration += ACCELERATION_ON_GEAR_CONSTANT
            self.velocity += self.acceleration 
            if self.acceleration > MAX_ACCELERATION:
                self.acceleration = MAX_ACCELERATION
            if self.velocity > MAX_VELOCITY:
                self.velocity = MAX_VELOCITY 
        else: #stoped acceleration
            self.acceleration = ACCELERATION_ON_NOTHING
            self.velocity += self.acceleration 
            if self.velocity < MIN_VELOCITY:
                self.velocity = 0
                
        self.player_sprite.change_x = self.velocity * -1*math.sin(self.player_sprite.radians)
        self.player_sprite.change_y = self.velocity * 1*math.cos(self.player_sprite.radians) 

        if (self.player_sprite.center_x + self.player_sprite.change_x + self.player_sprite.height > self.tile_map.width*self.tile_map.tile_width ) or (self.player_sprite.center_x + self.player_sprite.change_x - self.player_sprite.height< 0 ):
            self.player_sprite.change_x = 0
        
        if (self.player_sprite.center_y + self.player_sprite.change_y + self.player_sprite.height > self.tile_map.height*self.tile_map.tile_height ) or (self.player_sprite.center_y + self.player_sprite.change_y - self.player_sprite.height < 0 ):
            self.player_sprite.change_y = 0
        

    def on_update(self, delta_time: float):
        # if (self.player_sprite.center_x > 1250 and self.player_sprite.change_x > 0) or (self.player_sprite.center_x < 0 and self.player_sprite.change_x < 0):
        #     self.player_sprite.change_x = 0
        
        self.move_car_mode()
        # if (self.player_sprite.center_x > 1250 and self.player_sprite.change_x > 0):
        #     self.player_sprite.center_x = 0
        # elif (self.player_sprite.center_x < 0 and self.player_sprite.change_x < 0):
        #     self.player_sprite.center_x = 1250
        self.physics_engine.update()
        self.center_camera_to_player()
        # return super().on_update(delta_time)

class EmptyMap(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__(left, bottom, width, height, **kwargs)
        self.scene = None
        

        self.player_sprite=None 

        self.physics_engine = None 
        

        self.mode = 0
        self.acceleration = 0
        self.velocity = 0

    def setup(self):
        self.scene = arcade.Scene()
        image_source = "./resources/car.png"

        self.player_sprite = Car.PlayerCar(image_source,CHARACTER_SCALING,center_x=200,center_y=200)

        self.scene.add_sprite('Player',self.player_sprite)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=0
        )
    

    def on_draw(self):
        # self.clear()
        # self.wall_list.draw()
        # self.player_list.draw()
        self.scene.draw()
        

        # return super().on_draw()
    


    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.mode = 1
        elif key == arcade.key.DOWN or key == arcade.key.SPACE:
            self.mode = 0
        # if key == arcade.key.DOWN or key == arcade.key.S:
        #     self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_angle = CAR_ROTATION_SPEED
            self.player_sprite.steering_angle += 5

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_angle = -CAR_ROTATION_SPEED
            self.player_sprite.steering_angle -= 5

        # return super().on_key_press(symbol, modifiers)
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.DOWN or key == arcade.key.SPACE:
            self.mode = 2
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_angle = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_angle = 0

    def move_car_mode(self):

        if self.mode == 0:  #break
            if self.velocity > MIN_VELOCITY:
                self.acceleration = ACCELERATION_ON_BREAK
                self.velocity += self.acceleration 
            else:
                self.acceleration = 0
                self.velocity = 0
        elif self.mode == 1: #acceleration
            # print(self.player_sprite.angle)

            if self.acceleration < 0 :
                self.acceleration = 0
            self.acceleration += ACCELERATION_ON_GEAR_CONSTANT
            self.velocity += self.acceleration 
            if self.acceleration > MAX_ACCELERATION:
                self.acceleration = MAX_ACCELERATION
            if self.velocity > MAX_VELOCITY:
                self.velocity = MAX_VELOCITY 
        else: #stoped acceleration
            self.acceleration = ACCELERATION_ON_NOTHING
            self.velocity += self.acceleration 
            if self.velocity < MIN_VELOCITY:
                self.velocity = 0
                
        self.player_sprite.change_x = self.velocity * -1*math.sin(self.player_sprite.radians)
        self.player_sprite.change_y = self.velocity * 1*math.cos(self.player_sprite.radians) 

        if (self.player_sprite.center_x > self.width ):
            self.player_sprite.center_x = 0
        elif (self.player_sprite.center_x < 0 ):
            self.player_sprite.center_x = self.width

        if (self.player_sprite.center_y > self.height ):
            self.player_sprite.center_y = 0
        elif (self.player_sprite.center_y < 0):
            self.player_sprite.center_y = self.height

    def on_update(self, delta_time: float):
        self.move_car_mode()
        self.physics_engine.update()