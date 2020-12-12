import arcade
import os
import time

TILE_SPRITE_SCALING = 0.5
PLAYER_SCALING = 0.14

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "A Cute Lil Story"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SPRITE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_TOP = 60
VIEWPORT_MARGIN_BOTTOM = 60
VIEWPORT_RIGHT_MARGIN = 270
VIEWPORT_LEFT_MARGIN = 270

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 22
GRAVITY = 1.0

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class MyGame(arcade.Window):
    """ Main application class. """
    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.walk_pair = load_texture_pair("assets/breeze.png")
        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.state = 0
        self.move_lock = 0
        self.pat_text = "Get the fuck off my boat, scrub."
        self.textx = 1050
        self.texty = 155


        # Sprite lists
        self.wall_list = None
        self.player_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.level = 1
        self.max_level = 2

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        #self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
        self.player_sprite = arcade.Sprite("assets/breeze.png",
                                           PLAYER_SCALING)

        # Starting position of the player
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 64
        self.player_list.append(self.player_sprite)

        self.load_level(self.level)

        self.game_over = False

    def load_level(self, level):
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(f"assets/pat_map{level}.tmx")

        # --- Walls ---

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # Grab the layer of items we can't move through

        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      'Coins',
                                                      TILE_SPRITE_SCALING,
                                                      use_spatial_hash=True)

        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      'Platforms',
                                                      TILE_SPRITE_SCALING,
                                                      use_spatial_hash=True)
        
        

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        """
        Render the screen.
        """

        self.frame_count += 1

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS: {fps:5.0f}"

        if self.fps_message:
            arcade.draw_text(self.fps_message, self.view_left + 10, self.view_bottom + 40, arcade.color.BLACK, 14)

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        # Put the text on the screen.
        # Adjust the text position based on the view port so that we don't
        # scroll the text too.
        distance = self.player_sprite.right
        output = f"Distance: {distance:.0f}"
        arcade.draw_text(output, self.view_left + 10, self.view_bottom + 20, arcade.color.BLACK, 14)

        if self.move_lock == 1:
            arcade.draw_text(self.pat_text, self.textx, self.texty, arcade.color.BLACK, 12)

        if self.game_over:
            arcade.draw_text("Game Over", self.view_left + 200, self.view_bottom + 200, arcade.color.BLACK, 30)

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif self.move_lock == 1 and self.state == 0:
            self.pat_text = "Oh. Um, okay."
            self.textx = 980
            self.texty = 155
            self.state = 1
        elif self.move_lock == 1 and self.state == 1:
            self.pat_text = "See ya."
            self.textx = 1110
            self.texty = 155
            self.state = 2
        elif self.move_lock == 1 and self.state == 2:
            self.level = 2
            self.move_lock = 0
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128
            self.pat_text = ""
            self.load_level(self.level)
            self.state = 3
        elif self.move_lock == 1 and self.state == 3:
            self.pat_text = "YEAH!"
            self.textx = 940
            self.texty = 870
            self.state = 4
        elif self.move_lock == 1 and self.state == 4:
            self.pat_text = "Cool, let's go."
            self.textx = 1010
            self.texty = 870
            self.state = 5
        elif self.move_lock == 1 and self.state == 5:
            self.level = 3
            self.move_lock = 0
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128
            self.pat_text = ""
            self.load_level(self.level)
            self.state = 6
        elif self.move_lock == 1 and self.state == 4:
            self.pat_text = "Cool, let's go."
            self.textx = 1010
            self.texty = 870
            self.state = 5
        elif self.move_lock == 1 and self.state == 6:
            self.pat_text = "Guelph."
            self.textx = 175
            self.texty = 1050
            self.state = 7
        elif self.move_lock == 1 and self.state == 7:
            self.pat_text = "Aight, say less."
            self.textx = 45
            self.texty = 1050
            self.state = 8
        elif self.move_lock == 1 and self.state == 8:
            self.level = 4
            self.move_lock = 0
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128
            self.pat_text = ""
            self.load_level(self.level)
            self.state = 9

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.player_sprite.change_x = 0
        print("X: "+str(self.player_sprite.center_x)+", Y:"+str(self.player_sprite.center_y)+", State:"+str(self.state)+", MoveLOCK:"+str(self.move_lock))
        if self.player_sprite.center_y < 50:
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 128

        if self.up_pressed and self.physics_engine.can_jump():
            self.player_sprite.change_y = JUMP_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
            self.player_sprite.texture = self.walk_pair[1]
            if self.state == 6 and self.player_sprite.center_x <= 200 and self.player_sprite.center_y >= 990:
                self.move_lock = 1
                self.pat_text = "Nice Jumping. Where you going next year?"
                self.textx = 10
                self.texty = 1050
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED
            if self.state < 3 and self.player_sprite.right > 1065:
                self.move_lock = 1
            if self.state == 3 and self.player_sprite.center_x >= 955 and self.player_sprite.center_y == 798.25:
                self.move_lock = 1
                self.pat_text = "Yo, wanna come to my cottage?"
                self.textx = 1010
                self.texty = 870
            self.player_sprite.texture = self.walk_pair[0]

        if self.move_lock == 1:
            self.player_sprite.change_x = 0
        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the view port

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()