import arcade 
import math
from simulation import Car
import numpy as np

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
        
        self.layer_grid_array = np.array([])   

        self.radars = [-1,-1,-1,-1,-1,-1]

    def setup(self):
        self.setup_camera()
        self.setup_scene()
        
    def setup_camera(self):
        self.camera = arcade.Camera(self.width, self.height)
    
    def setup_scene(self):
        self.scene = arcade.Scene()
        image_source = self.car_img_resource

        self.player_sprite = Car.PlayerCar(image_source,CHARACTER_SCALING,center_x=100,center_y=160)

        self.scene.add_sprite('Player',self.player_sprite)

        # print(self.player_sprite.width, self.player_sprite.height)

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
            self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options,True,hit_box_algorithm='Detailed')
            self.scene = arcade.Scene.from_tilemap(self.tile_map)


            # print(self.tile_map.height, self.tile_map.width, self.tile_map.tile_height, self.tile_map.tile_width)
            # print(self.tile_map.sprite_lists['road_edges'], self.tile_map.tiled_map.layers[0].size.height)
            # print(self.tile_map.tiled_map.layers[0].data)

            self.layer_grid_array = np.array(self.tile_map.tiled_map.layers[0].data)
            # print()
            # print(self.layer_grid_array[40:,:10])
            # print()
            # print(self.layer_grid_array)
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
        self.draw_lines_direction()

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

    def check_collision_with_wall(self):

        if(self.tile_map != None):
            pos_x = self.player_sprite.center_x
            pos_y = self.player_sprite.center_y
            player_width = self.player_sprite.width//2   + 7
            player_height = self.player_sprite.height//2 + 7

            tile_width = self.tile_map.tile_width
            tile_height = self.tile_map.tile_height
            no_of_tiles_x = self.tile_map.tiled_map.layers[0].size.width # self.tile_map.width
            no_of_tiles_y = self.tile_map.tiled_map.layers[0].size.height # self.tile_map.height

            ang = ((self.player_sprite.angle + 90)%360)*0.0174533
            
            # print( 'x :', int((pos_x + player_width*math.cos(ang + math.pi/4)))//tile_width , '\t y:', no_of_tiles_y - 1 - int((pos_y + player_height*math.sin(ang + math.pi/4)))//tile_height)
            

            if(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y + player_height*math.sin(ang + math.pi/4))//tile_height) , int((pos_x + player_width*math.cos(ang + math.pi/4))//tile_width)] != 0):
                print('45')
                pass
            elif(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y + player_height*math.sin(ang - math.pi/4))//tile_height) , int((pos_x + player_width*math.cos(ang - math.pi/4))//tile_width)] != 0):
                print('-45')
                pass
            elif(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y + player_height*math.sin(ang + 3*math.pi/4))//tile_height) , int((pos_x + player_width*math.cos(ang + 3*math.pi/4))//tile_width)] != 0):
                print('-135')
                pass
            elif(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y + player_height*math.sin(ang - 3*math.pi/4))//tile_height) , int((pos_x + player_width*math.cos(ang - 3*math.pi/4))//tile_width)] != 0):
                print('135')
                pass
            else:
                return 
            print('Collision' , tile_height, tile_width, player_height, player_width, pos_x , pos_y)
            # print(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y + player_height)//tile_height) , int((pos_x + player_width)//tile_width)] , no_of_tiles_y - 1 - int((pos_y + player_height)//tile_height) , int((pos_x + player_width)//tile_width) )
            # print(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y + player_height)//tile_height) , int((pos_x - player_width)//tile_width)] , no_of_tiles_y - 1 - int((pos_y + player_height)//tile_height) , int((pos_x - player_width)//tile_width) )
            # print(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y - player_height)//tile_height) , int((pos_x - player_width)//tile_width)] , no_of_tiles_y - 1 - int((pos_y - player_height)//tile_height) , int((pos_x - player_width)//tile_width) )
            # print(self.layer_grid_array[ no_of_tiles_y - 1 - int((pos_y - player_height)//tile_height) , int((pos_x + player_width)//tile_width)] , no_of_tiles_y - 1 - int((pos_y - player_height)//tile_height) , int((pos_x + player_width)//tile_width) )
            
            print()

            self.player_sprite.center_x = 100
            self.player_sprite.center_y = 160
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.change_angle = 0
            self.player_sprite.angle = 0

    def check_radar(self):
        if(self.tile_map != None):
            pos_x = self.player_sprite.center_x
            pos_y = self.player_sprite.center_y

            ang = (self.player_sprite.angle + 90)%360
            
            tile_width = self.tile_map.tile_width
            tile_height = self.tile_map.tile_height
            no_of_tiles_x = self.tile_map.tiled_map.layers[0].size.width # self.tile_map.width
            no_of_tiles_y = self.tile_map.tiled_map.layers[0].size.height
            
            radars = [-1,-1,-1,-1,-1,-1]
            for i in range(0,200,10):
                check_x = pos_x + i*math.cos(ang * 0.0174533)
                check_y = pos_y + i*math.sin(ang * 0.0174533)

                # print(check_x,check_y)
                if(self.layer_grid_array[no_of_tiles_y - 1 - int(check_y//tile_height) , int(check_x//tile_width)] != 0):
                    radars[2] = i
                    # print(i)
                    break
            
            ang = (self.player_sprite.angle + 90 - 30)%360
            for i in range(0,200,10):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.layer_grid_array[no_of_tiles_y - 1 - int(check_y//tile_height) , int(check_x//tile_width)] != 0):
                    radars[3] = i
                    # print(i)
                    break
            
            ang = (self.player_sprite.angle + 90 + 30)%360
            for i in range(0,200,10):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.layer_grid_array[no_of_tiles_y - 1 - int(check_y//tile_height) , int(check_x//tile_width)] != 0):
                    radars[1] = i
                    # print(i)
                    break
            ang = (self.player_sprite.angle + 90 + 90)%360
            for i in range(0,100,10):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.layer_grid_array[no_of_tiles_y - 1 - int(check_y//tile_height) , int(check_x//tile_width)] != 0):
                    radars[0] = i
                    # print(i)
                    break

            ang = (self.player_sprite.angle + 90 - 90)%360
            for i in range(0,100,10):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.layer_grid_array[no_of_tiles_y - 1 - int(check_y//tile_height) , int(check_x//tile_width)] != 0):
                    radars[4] = i
                    # print(i)
                    break
                
            self.radars = radars[:]

    def draw_lines_direction(self):
        pos_x = self.player_sprite.center_x
        pos_y = self.player_sprite.center_y
        ang   = self.player_sprite.angle%360 * 0.0174533

        arcade.draw_line(pos_x,pos_y,pos_x+100*math.cos(ang),pos_y+100*math.sin(ang), arcade.color.DARK_BLUE)
        arcade.draw_line(pos_x,pos_y,pos_x-100*math.cos(ang),pos_y-100*math.sin(ang), arcade.color.DARK_BLUE)
        arcade.draw_line(pos_x,pos_y,pos_x+200*math.cos(ang + math.pi/2),pos_y+200*math.sin(ang + math.pi/2 ), arcade.color.DARK_BLUE)
        arcade.draw_line(pos_x,pos_y,pos_x+200*math.cos(ang + math.pi/3),pos_y+200*math.sin(ang + math.pi/3 ), arcade.color.DARK_BLUE)
        arcade.draw_line(pos_x,pos_y,pos_x+200*math.cos(ang + (4*math.pi)/6),pos_y+200*math.sin(ang + (4*math.pi)/6), arcade.color.DARK_BLUE)
        
        ang1 = (self.player_sprite.angle + 90)%360 * 0.0174533
        ang2 = (self.player_sprite.angle + 90 -30)%360 * 0.0174533
        ang3 = (self.player_sprite.angle + 90 +30)%360 * 0.0174533
        ang4 = (self.player_sprite.angle + 90 -90)%360 * 0.0174533
        ang5 = (self.player_sprite.angle + 90 +90)%360 * 0.0174533

        arcade.draw_circle_filled(pos_x + self.radars[2]*math.cos(ang1), pos_y + self.radars[2]*math.sin(ang1),3,arcade.color.GREEN)
        arcade.draw_circle_filled(pos_x + self.radars[3]*math.cos(ang2), pos_y + self.radars[3]*math.sin(ang2),3,arcade.color.RED)
        arcade.draw_circle_filled(pos_x + self.radars[1]*math.cos(ang3), pos_y + self.radars[1]*math.sin(ang3),3,arcade.color.RED)
        arcade.draw_circle_filled(pos_x + self.radars[4]*math.cos(ang4), pos_y + self.radars[4]*math.sin(ang4),3,arcade.color.BLACK)
        arcade.draw_circle_filled(pos_x + self.radars[0]*math.cos(ang5), pos_y + self.radars[0]*math.sin(ang5),3,arcade.color.BLACK)

        ang = ((self.player_sprite.angle + 90)%360)*0.0174533
        player_width = self.player_sprite.width//2   + 7
        player_height = self.player_sprite.height//2 + 7

        arcade.draw_circle_filled(pos_x + player_width*math.cos(ang + math.pi/4), pos_y + player_height*math.sin(ang + math.pi/4),3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x + player_width*math.cos(ang - math.pi/4), pos_y + player_height*math.sin(ang - math.pi/4),3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x + player_width*math.cos(ang + 3*math.pi/4), pos_y + player_height*math.sin(ang + 3*math.pi/4),3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x + player_width*math.cos(ang - 3*math.pi/4), pos_y + player_height*math.sin(ang - 3*math.pi/4),3,arcade.color.PINK)


        # arcade.draw_line(pos_x,pos_y,pos_x-200*math.cos(ang),pos_y+200*math.sin(ang), arcade.color.RED)
        # arcade.draw_line(pos_x,pos_y,pos_x-200*math.cos(ang),pos_y+200*math.sin(ang), arcade.color.BROWN)
        
        # self.scene.add_sprite()
        pass
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
        

        # if arcade.check_for_collision_with_list(self.player_sprite, self.tile_map.sprite_lists['road_edges'], 1) :

        #     self.player_sprite.change_x = 0
        #     self.player_sprite.change_y = 0

        #     self.player_sprite.center_x = 100
        #     self.player_sprite.center_y = 160
        #     print('Collision!!!')

        # self.move_car_mode()

        self.check_collision_with_wall()
        self.player_sprite.control_key_turn(self.turning_key)
        self.player_sprite.control_key_acc(self.acceleration_key)
        self.restrict_movement()
        self.check_radar()
        
        # self.draw_lines_direction()
        self.physics_engine.update()
        self.center_camera_to_player()
        
class CollegeMap(GameMap):
    def __init__(self,left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__("./resources/car.png","./resources/simple_path_1.json",left, bottom, width, height, **kwargs)


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

