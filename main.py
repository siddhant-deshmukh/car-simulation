import arcade 
import math
from simulation import Car, Views

SCREEN_WIDTH = 1000
SCREEN_HEIGHT= 800
SCREEN_TITLE= 'Car simulation'




        
def main():
    # window = MyGame()
    # window.setup()
    # arcade.run()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Instruction and Game Over Views Example")
    view = Views.MyView()
    window.show_view(view)
    arcade.run()


if __name__=='__main__':
    main()