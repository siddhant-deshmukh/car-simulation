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
        self.checkPoints = []
        self.curr_check_point = -1
        self.endPoints = []
        
        self.checkPoint_pos = 0
        self.score = 0
        
        self.checkPoint_distX = 0
        self.checkPoint_distY = 0

    # -----------------------------------------------------------------------------------------------------------------
    #                                              functions to  setup
    # -------------------------------------------------------------------------------------------------------------------
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

            # print(self.checkPoints)
            
            self.layer_grid_array = np.array(self.tile_map.tiled_map.layers[0].data)
            self.findSlope()

            self.scene.add_sprite('Player',self.player_sprite)
        
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, gravity_constant=0, walls=self.scene["road_edges"]
            )

    def findSlope(self):
        for point in self.checkPoints:
            minLen = 10000
            ans = [(0,0),(0,0)]
            for ang in range(0,360,10):
                end1 = [point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2 , ( self.tile_map.height -1 - point[1])*self.tile_map.tile_width + self.tile_map.tile_width/2 ]
                end2 = [point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2 , ( self.tile_map.height -1 - point[1])*self.tile_map.tile_width + self.tile_map.tile_width/2 ]
                angle = ang*0.0174533 
                for i in range(0,2000,1):
                    # end1 = ( end1[0] + 5*math.cos(angle) , end2[1] + 5*math.sin(angle) )
                    end1[0] += 5*math.cos(angle)
                    end1[1] += 5*math.sin(angle)
                    if(  self.checkTile(end1[0],end1[1]) != 0):
                        break
                for i in range(0,2000,1):
                    # end2 = ( end2[0] + 5*math.cos(angle + math.pi) , end2[1] + 5*math.sin(angle + math.pi) )
                    end2[0] += 5*math.cos(angle + math.pi)
                    end2[1] += 5*math.sin(angle + math.pi)
                    if(  self.checkTile(end2[0],end2[1]) != 0):
                        break
                dist = ((end1[0] - end2[0])**2  + (end1[1]- end2[1])**2  )**0.5 
                if(dist < minLen):
                    minLen = dist
                    ans = [end1,end2]
            # print(point , ans, (point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2 , point[1]*self.tile_map.tile_width + self.tile_map.tile_width/2 ))
            self.endPoints.append(ans)

            
    # -----------------------------------------------------------------------------------------------------------------
    #                                              functions of the parent class
    # -------------------------------------------------------------------------------------------------------------------  
    def on_draw(self):
        self.scene.draw()
        if(self.camera != None):
            self.camera.use()
        self.draw_lines_direction()
        # for point in self.checkPoints :

        for line in self.endPoints:
            arcade.draw_line(line[0][0],line[0][1],line[1][0],line[1][1],arcade.color.GREEN_YELLOW,3)
        
        for point in self.checkPoints:
            arcade.draw_circle_filled( point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2 , (self.tile_map.width - point[1])*self.tile_map.tile_width + self.tile_map.tile_width/2, 7,arcade.color.RED )
        if len(self.checkPoints) > self.curr_check_point :
            point = self.checkPoints[self.curr_check_point]
            arcade.draw_circle_filled( point[0]*self.tile_map.tile_width + self.tile_map.tile_width/2 , (self.tile_map.width - point[1])*self.tile_map.tile_width + self.tile_map.tile_width/2, 5,arcade.color.RED )
    
    def on_update(self, delta_time: float):
        
        self.check_collision_with_wall()
        self.player_sprite.control_key_turn(self.turning_key)
        self.player_sprite.control_key_acc(self.acceleration_key)
        self.restrict_movement()
        self.check_radar()
        
        # self.draw_lines_direction()
        self.physics_engine.update()
        self.center_camera_to_player()

        self.score -= 0.008
        self.pointRelationWithCheckPoint()
    
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

    # -----------------------------------------------------------------------------------------------------------------
    #                                             helper functions getting call on every loop
    # -------------------------------------------------------------------------------------------------------------------  
    def pointRelationWithCheckPoint(self):
        if len(self.endPoints) <= self.curr_check_point or len(self.checkPoints) <= self.curr_check_point:
            self.restart_game()
            return 
        
        end_points = self.endPoints[self.curr_check_point]
        # print(end_points, self.player_sprite.center_x )
        # print(self.player_sprite.center_x - end_points[0][0])
        # print()

        d = ( self.player_sprite.center_x - end_points[0][0] )*( end_points[1][1] - end_points[0][1] ) - ( self.player_sprite.center_y - end_points[0][1] )*( end_points[1][0] - end_points[0][0] ) 
        if(d!=0):
            d = d//abs(d)
        
        # print( end_points ,self.checkPoint_pos)
        if(d != self.checkPoint_pos ):
            self.curr_check_point += 1 
            self.score += 100
            print("score", self.score)
            if len(self.endPoints) <= self.curr_check_point or len(self.checkPoints) <= self.curr_check_point:
                # end the game
                self.restart_game()
                return 
            
            end_points = self.endPoints[self.curr_check_point]
            d = ( self.player_sprite.center_x - end_points[0][0] )*( end_points[1][1] - end_points[0][1] ) - ( self.player_sprite.center_y - end_points[0][1] )*( end_points[1][0] - end_points[0][0] ) 
            if(d!=0):
                self.checkPoint_pos = d//abs(d)
            else:
                self.checkPoint_pos = 0

            return
        else:
            return

    def center_camera_to_player(self):
        # print(self.width , self.height)
        self.camera.resize( self.width , self.height )

        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        # Don't let camera travel past 0
        if screen_center_x > self.tile_map.width*self.tile_map.tile_width - 2*(self.camera.viewport_width / 2):
            screen_center_x = self.tile_map.width*self.tile_map.tile_width  - (self.camera.viewport_width)
        if screen_center_x < 0:
            screen_center_x = 0
        # if self.player_sprite.center_x < 0 + (self.camera.viewport_width / 2):
        #     screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_y > self.tile_map.height*self.tile_map.tile_height - 2*(self.camera.viewport_height / 2) + 100:
            screen_center_y = self.tile_map.height*self.tile_map.tile_height  - 2*(self.camera.viewport_height / 2) + 100
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def check_collision_with_wall(self):

        if(self.tile_map != None):
            pos_x = self.player_sprite.center_x
            pos_y = self.player_sprite.center_y
            player_width = ((self.player_sprite.width/2)**2 + (self.player_sprite.height/2)**2)**0.5  + 3
            player_height = ((self.player_sprite.width/2)**2 + (self.player_sprite.height/2)**2)**0.5  + 3
            
            ang = ((abs(self.player_sprite.angle - 360))%360)*0.0174533 
            
            phase_angles = [math.pi/4,-math.pi/4,3*math.pi/4,-3*math.pi/4,0,math.pi]
            check = True 
            for phase_angle in phase_angles:
                if( self.checkTile(pos_x + player_width*math.sin(ang + phase_angle) , pos_y + player_height*math.cos(ang + phase_angle))  != 0):
                    check = False
                    print(phase_angle , (phase_angle*180)/math.pi )
                    break
            if(check):
                return
            
            print('Collision' , pos_x , pos_y)
            print()
            self.restart_game()
            
    def check_radar(self):
        if(self.tile_map != None):
            pos_x = self.player_sprite.center_x
            pos_y = self.player_sprite.center_y

            ang = (self.player_sprite.angle + 90)%360
            
            radars = [100,200,200,200,100,200]
            for i in range(0,200,3):
                check_x = pos_x + i*math.cos(ang * 0.0174533)
                check_y = pos_y + i*math.sin(ang * 0.0174533)

                # print(check_x,check_y)
                if(self.checkTile(check_x,check_y) != 0):
                    radars[2] = i
                    # print(i)
                    break
            
            ang = (self.player_sprite.angle + 90 - 30)%360
            for i in range(0,200,3):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.checkTile(check_x,check_y) != 0):
                    radars[3] = i
                    # print(i)
                    break
            
            ang = (self.player_sprite.angle + 90 + 30)%360
            for i in range(0,200,3):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.checkTile(check_x,check_y) != 0):
                    radars[1] = i
                    # print(i)
                    break
            ang = (self.player_sprite.angle + 90 + 90)%360
            for i in range(0,100,3):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.checkTile(check_x,check_y) != 0):
                    radars[0] = i
                    # print(i)
                    break

            ang = (self.player_sprite.angle + 90 - 90)%360
            for i in range(0,100,3):
                check_x = pos_x + i*math.cos(ang* 0.0174533)
                check_y = pos_y + i*math.sin(ang* 0.0174533)

                # print(check_x,check_y)
                if(self.checkTile(check_x,check_y) != 0):
                    radars[4] = i
                    # print(i)
                    break
            # print(radars)
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
        arcade.draw_circle_filled(pos_x + self.radars[4]*math.cos(ang4), pos_y + self.radars[4]*math.sin(ang4),3,arcade.color.PURPLE)
        arcade.draw_circle_filled(pos_x + self.radars[0]*math.cos(ang5), pos_y + self.radars[0]*math.sin(ang5),3,arcade.color.PURPLE)

        ang = (( abs(self.player_sprite.angle - 360) )%360)*0.0174533
        player_width = ((self.player_sprite.width/2)**2 + (self.player_sprite.height/2)**2)**0.5  + 1
        player_height = ((self.player_sprite.width/2)**2 + (self.player_sprite.height/2)**2)**0.5  + 1
        
        # print(( abs(self.player_sprite.angle - 360) )%360)

        arcade.draw_circle_filled(pos_x  + int(player_width*math.sin(ang)), pos_y + int(player_width*math.cos(ang)), 3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x  + int(player_width*math.sin(ang + math.pi)), pos_y + int(player_width*math.cos(ang + math.pi)), 3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x  + int(player_width*math.sin(ang + math.pi/4)), pos_y + int(player_width*math.cos(ang + math.pi/4)), 3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x  + int(player_width*math.sin(ang - math.pi/4)), pos_y + int(player_width*math.cos(ang - math.pi/4)), 3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x  + int(player_width*math.sin(ang + 3*math.pi/4)), pos_y + int(player_width*math.cos(ang + 3*math.pi/4)), 3,arcade.color.PINK)
        arcade.draw_circle_filled(pos_x  + int(player_width*math.sin(ang - 3*math.pi/4)), pos_y + int(player_width*math.cos(ang - 3*math.pi/4)), 3,arcade.color.PINK)
        
    def restrict_movement(self):
        if (self.player_sprite.center_x + self.player_sprite.change_x + self.player_sprite.height > self.tile_map.width*self.tile_map.tile_width ) or (self.player_sprite.center_x + self.player_sprite.change_x - self.player_sprite.height< 0 ):
            self.player_sprite.change_x = 0
        
        if (self.player_sprite.center_y + self.player_sprite.change_y + self.player_sprite.height > self.tile_map.height*self.tile_map.tile_height ) or (self.player_sprite.center_y + self.player_sprite.change_y - self.player_sprite.height < 0 ):
            self.player_sprite.change_y = 0

    
    # -----------------------------------------------------------------------------------------------------------------
    #                                               helper functions 
    # -------------------------------------------------------------------------------------------------------------------  

    def checkTile(self,pos_x,pos_y):
        if(pos_x < 0 or pos_y < 0):
            return -1
        tile_width = self.tile_map.tile_width
        tile_height = self.tile_map.tile_height
        no_of_tiles_y = self.tile_map.tiled_map.layers[0].size.height

        if(int((pos_x)//tile_width) >= self.tile_map.width or (no_of_tiles_y - 1 - int(pos_y//tile_height)) >= self.tile_map.height):
            return -1

        return self.layer_grid_array[ no_of_tiles_y - 1 - int(pos_y//tile_height) , int((pos_x)//tile_width)]


    def restart_game(self):
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 160
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        self.player_sprite.change_angle = 0
        self.player_sprite.angle = 0

        self.score = 0
        self.curr_check_point = -1
        self.checkPoint_pos = 0
        # print(self.score,self.curr_check_point)

        
class CollegeMap(GameMap):
    def __init__(self,left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__("./resources/car.png","./resources/simple_path_1.json",left, bottom, width, height, **kwargs)
        self.checkPoints = [ (10,132),(33,44),(118,15),(179,52),(142,111),(176,152),(154,193),(86,188),(32,188) ]

class SimpleMap(GameMap):
    def __init__(self,left: int, bottom: int, width: int, height: int,**kwargs):
        super().__init__("./resources/car.png","./resources/black.tmj",left, bottom, width, height, **kwargs)
        self.checkPoints = [ (10,132),(33,44),(118,15),(179,52),(142,111),(176,152),(154,193),(86,188),(32,188) ] #


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

