import arcade 
import math
from simulation import Car, Views

SCREEN_WIDTH = 1250
SCREEN_HEIGHT= 800
SCREEN_TITLE= 'Car simulation'
        
def main():
    # window = MyGame()
    # window.setup()
    # arcade.run()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Car simulation", resizable=True)
    view = Views.MyView()
    window.show_view(view)
    arcade.run()


if __name__=='__main__':
    main()