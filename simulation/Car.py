import arcade
from math import sqrt, cos, sin, tan
# from typing import *

MAX_ACCELERATOR_ANGLE = 35
MAX_STEERING_ANGLE = 45
MIN_STEERING_ANGLE = -45
CONSTANT_INCREASE_ACCELERATOR = 2
CONSTANT_INCREASE_STEERING = 5

LENGTH_OF_CAR = 4
MASS_OF_CAR = 1500
TRACTION_FORCE_CONSTANT = 2.5
DRAG_FORCE_CONSTANT =0.73
ROLLING_FORCE_CONSTANT = 19.2
BRAKE_FORCE_CONSTANT = 150
ACCELERATOR_INC_CONSTANT = 0.1
ACCELERATOR_DESC_CONSTANT= 0.02

class PlayerCar(arcade.Sprite):
    def __init__(self, filename: str = None, scale: float = 1,center_x=5, center_y=5):
        super().__init__(filename, scale,center_x=center_x,center_y=center_y)
        self.accelerator_angle = 0    #angle of accelerator
        self.steering_angle = 0       #angle of steering wheel  

        # self.radians = 3.14/2
        self.car_acceleration = (0,0)
        self.car_velocity = (0,0)
        
    @property
    def speed(self):
        # return euclidian distance * current fps (60 default)
        return int(sqrt(pow(self.change_x, 2) + pow(self.change_y, 2)) * 60)

    # def control_acceleration(self,mode:str ):
    #     if(mode == 'UP'):
    #         pass
    #     elif(mode == 'DOWN'):
    #         pass 
    #     elif(mode =='BRAK'):
    #         pass
    #     else:
    #         pass
    # def control_turning(self,mode:str):
    #     if(mode =='LEFT'):
    #         pass
    #     else:
    #         pass

    def control_key_acc(self,mode:str):
        speed = sqrt(self.change_x**2 + self.change_y**2)
        if(mode =='BRAKE'):
            if self.change_x > 0:
                force_longitude_x = -BRAKE_FORCE_CONSTANT - DRAG_FORCE_CONSTANT*self.velocity[0]*speed - ROLLING_FORCE_CONSTANT*self.velocity[0]
            else :
                force_longitude_x = -1*(-BRAKE_FORCE_CONSTANT - DRAG_FORCE_CONSTANT*self.velocity[0]*speed - ROLLING_FORCE_CONSTANT*self.velocity[0] )
            
            if self.change_y > 0:
                force_longitude_y = -BRAKE_FORCE_CONSTANT - DRAG_FORCE_CONSTANT*self.velocity[1]*speed - ROLLING_FORCE_CONSTANT*self.velocity[1]
            else :
                force_longitude_y = -1*(-BRAKE_FORCE_CONSTANT - DRAG_FORCE_CONSTANT*self.velocity[1]*speed - ROLLING_FORCE_CONSTANT*self.velocity[1])

            if(self.change_x != 0):
                change_x = self.change_x + force_longitude_x / MASS_OF_CAR
                if(self.change_x * change_x <0):
                    self.change_x = 0
                    self.accelerator_angle = 0
                else:
                    self.change_x = change_x
            if(self.change_y != 0):
                change_y = self.change_y + force_longitude_y / MASS_OF_CAR
                if(self.change_y * change_y <0):
                    self.change_y = 0
                    self.accelerator_angle = 0
                else:
                    self.change_y = change_y

            self.accelerator_angle = 0

        else:
            if(mode == 'UP'):
                self.accelerator_angle += ACCELERATOR_INC_CONSTANT 
            else:  
                self.accelerator_angle -= ACCELERATOR_DESC_CONSTANT
            
            if self.accelerator_angle > MAX_ACCELERATOR_ANGLE:
                self.accelerator_angle = MAX_ACCELERATOR_ANGLE
            if self.accelerator_angle < 0:
                self.accelerator_angle = 0

            # force_longitude_x = -TRACTION_FORCE_CONSTANT*self.accelerator_angle*sin(self.radians) - DRAG_FORCE_CONSTANT*self.change_x*speed - ROLLING_FORCE_CONSTANT*self.change_x
            # force_longitude_y = TRACTION_FORCE_CONSTANT*self.accelerator_angle*cos(self.radians) - DRAG_FORCE_CONSTANT*self.change_y*speed - ROLLING_FORCE_CONSTANT*self.change_y
            # self.change_x += force_longitude_x / MASS_OF_CAR
            # self.change_y += force_longitude_y / MASS_OF_CAR

            speed = sqrt(self.change_x**2 + self.change_y**2)
            self.change_angle =  (speed / LENGTH_OF_CAR )* tan(self.steering_angle * 0.0174533)  # (speed*sin(self.steering_angle * 0.0174533))/LENGTH_OF_CAR
            

            force_longitude =  TRACTION_FORCE_CONSTANT*self.accelerator_angle - DRAG_FORCE_CONSTANT*speed*speed - ROLLING_FORCE_CONSTANT*speed

            new_speed =speed + force_longitude / MASS_OF_CAR
            # print(force_longitude)
            self.change_x = -1*new_speed*sin(self.angle *0.0174533)
            self.change_y = new_speed*cos(self.angle *0.0174533)
            
            if(self.change_x<0.005 and self.change_x>-0.005):
                self.change_x = 0
            if(self.change_y<0.005 and self.change_y>-0.005):
                self.change_y = 0


    def control_key_turn(self,mode:str):
        if(mode =='LEFT'):
            # print(self.radians)
            self.steering_angle += 0.6
        elif (mode == 'RIGHT'):
            self.steering_angle -= 0.6
        else:
            if self.steering_angle > 4:
                self.steering_angle -= 2
            elif self.steering_angle < -4:
                self.steering_angle += 2
            else:
                self.steering_angle = 0
            pass
        if self.steering_angle > MAX_STEERING_ANGLE:
            self.steering_angle = MAX_STEERING_ANGLE
        if self.steering_angle < MIN_STEERING_ANGLE:
            self.steering_angle = MIN_STEERING_ANGLE