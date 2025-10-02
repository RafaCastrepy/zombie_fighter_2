import tkinter as tk
from PIL import Image, ImageTk
import random

# creating the initial window
root = tk.Tk()
root.geometry("1400x1000")
root.title("Zombie Fighter 2")
root.config(bg="grey")

# initial constants and variables
score = 0

game_started = False

pause = False
boss = False

UDR_keys = ['<Up>', '<Down>', '<Right>']
UDS_keys = ['<Up>', '<Down>', '<space>']
WSS_keys = ['<w>', '<s>', '<space>']

num_games_played = 0

DIFF1 = [2500, 2000, 1500]
DIFF2 = [2000, 1500, 1200]
DIFF3 = [1200, 1000, 800]

# default keybinds
chosen_keys = UDR_keys
# default difficult
chosen_diff = DIFF1

# desired size of the background images
FRAME_WIDTH = 1400
FRAME_HEIGHT = 1000


def out_boss(event=None):
    '''displays and undisplays boss_screen when not in game loop'''
    global boss, prev_screen
    boss = not boss
    if boss:
        show_frame(boss_screen)
    else:
        show_frame(prev_screen)


def show_vic():
    '''displays victory screen'''
    global prev_screen
    prev_screen = victory_screen
    show_frame(victory_screen)


class Zombie:
    '''
    zombie class which are the main enemies in the game

    attributes
        frame dimensions, coordinates, animation frames, if it's alive,
        canvas, speed of animation
    methods
        animate and die
    '''

    def __init__(self, canvas, x, y):
        self.alive = True

        self.sprite_sheet = Image.open("Zombie running-2.png")

        self.frame_width = 275
        self.frame_height = 275

        self.frames = []
        for i in range(8):
            # crops the sprite sheet to desired frame
            frame = self.sprite_sheet.crop(
                (i * self.frame_width, 0, (i + 1) * self.frame_width,
                 self.frame_height))
            self.frames.append(ImageTk.PhotoImage(frame))

        self.canvas = canvas
        self.character_id = canvas.create_image(x,
                                                200,
                                                image=self.frames[0],
                                                anchor="n")

        self.character_x = x
        self.character_y = y
        self.frame_index = 0
        self.animation_speed = 100
        if self.alive:
            self.animate()

    def animate(self):
        '''
        animates the zombies running across the screen

        moves the zombies coordinates left to right
        checks if the zombie has left the screen
        checks for collision with an attack
        '''
        if not self.alive:
            self.canvas.delete(self.character_id)
            return
        if not pause:
            self.frame_index = (self.frame_index + 1) % len(self.frames)

            self.canvas.itemconfig(self.character_id,
                                   image=self.frames[self.frame_index])
            # changes zombie speed depending on cheat code
            if player_name == "slodown":
                self.character_x -= 20
            else:
                self.character_x -= 50

            self.canvas.coords(self.character_id, self.character_x,
                               self.character_y)

            if self.character_x < -self.frame_width:
                self.die(killed_by_player=False)
                if fighter.hp == 1:
                    fighter.die()
                if fighter.hp > 0:
                    # fighter takes damage depending on cheat code
                    if player_name == "imortal":
                        pass
                    else:
                        fighter.hp -= 1
                        fighter.update_health_bar()

            if (200 <= self.character_x <= 400 and fighter.attack
                    and fighter.y == self.character_y - 50):
                self.die(killed_by_player=True)

            self.canvas.after(self.animation_speed, self.animate)

    def die(self, killed_by_player=True):
        '''
        used for when the zombie dies

        two ways a zombie can die, by fighter or going off the screen
        if killed by player score and mana is increased
        updates score label
        displays win/lose screen
        parameter:
            killed by player determines how the zombie died
        '''
        global score
        self.alive = False
        self.canvas.delete(self.character_id)
        if killed_by_player:
            # double points for cheatcode
            if player_name == "2xpoint":
                score += 20
            else:
                score += 10
            if fighter.mana < fighter.max_mana - 2:
                fighter.mana += 2
                fighter.update_mana_bar()
            score_label.config(text=f"Score: {score}")
            final_score_label1.config(text=f"Score: {score}")
            final_score_label2.config(text=f"Score: {score}")

        if len(zombies) == 20:
            if all(not zom.alive for zom in zombies):
                # checks if all zombies are dead
                if fighter.hp <= 0:
                    fighter.die()
                else:
                    root.unbind('<b>')
                    root.unbind('<p>')
                    root.bind('<b>', out_boss)
                    show_vic()


class Fighter:
    '''
    fighter class for the player controlled character

    attributes
        canvas, character name, coordinates, hp and mana, frame details
        and whether it's alive

    methods
        update hp and mana bar, changes the length and
        colour of the hp and mana bar
        update frame, animates the fighter
        move up and down
        die
    '''

    def __init__(self, canvas, x, y, name, max_hp, max_mana):
        self.x = x
        self.y = y
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        if player_name == "mo_mana":
            self.max_mana = 100
            self.mana = 100
        else:
            self.max_mana = max_mana
            self.mana = max_mana
        self.attack = False
        self.alive = True
        self.canvas = canvas

        self.sprite_sheet = Image.open(self.name + " sprite sheet.png")

        self.frame_width = 500
        self.frame_height = 400
        self.num_frames = 21

        self.current_frame = 0

        self.frames = []
        for i in range(self.num_frames):
            # crops the sprite sheet to desired frame
            frame = self.sprite_sheet.crop(
                (i * self.frame_width, 0, (i + 1) * self.frame_width,
                 self.frame_height))
            self.frames.append(ImageTk.PhotoImage(frame))

        self.character_id = canvas.create_image(self.x,
                                                self.y,
                                                image=self.frames[0],
                                                anchor="nw")

        self.health_bar_bg = canvas.create_rectangle(50,
                                                     50,
                                                     1350 *
                                                     (self.hp / self.max_hp),
                                                     70,
                                                     fill="black")
        self.health_bar = canvas.create_rectangle(50,
                                                  50,
                                                  1350 *
                                                  (self.hp / self.max_hp),
                                                  70,
                                                  fill="green")

        self.mana_bar_bg = canvas.create_rectangle(50,
                                                   80,
                                                   1350 *
                                                   (self.mana / self.max_mana),
                                                   100,
                                                   fill="black")
        self.mana_bar = canvas.create_rectangle(50,
                                                80,
                                                1350 *
                                                (self.mana / self.max_mana),
                                                100,
                                                fill="blue")

    def update_health_bar(self):
        '''changes the length and colour of health bar'''
        width = 1350 * (self.hp / self.max_hp)
        self.canvas.coords(self.health_bar, 50, 50, width, 70)
        if self.hp > self.max_hp / 2:
            self.canvas.itemconfig(self.health_bar, fill="green")
        elif self.hp > self.max_hp / 4:
            self.canvas.itemconfig(self.health_bar, fill="yellow")
        else:
            self.canvas.itemconfig(self.health_bar, fill="red")

    def update_mana_bar(self):
        '''changes the length and colour of mana bar'''
        width = 1350 * (self.mana / self.max_mana)
        self.canvas.coords(self.mana_bar, 50, 80, width + 50, 100)
        if self.mana > self.max_mana / 2:
            self.canvas.itemconfig(self.mana_bar, fill="blue")
        elif self.mana > self.max_mana / 4:
            self.canvas.itemconfig(self.mana_bar, fill="yellow")
        else:
            self.canvas.itemconfig(self.mana_bar, fill="red")

    def update_frame(self):
        '''
        animates the fighter's attack

        depending on the character the attack is short or long
        '''
        if self.current_frame < self.num_frames:
            self.canvas.itemconfig(self.character_id,
                                   image=self.frames[self.current_frame])
            self.current_frame += 1
            if self.name == "cloudy":
                # attack length is based on the character
                root.after(20, self.update_frame)
            else:
                root.after(30, self.update_frame)
        else:
            self.attack = False
            self.current_frame = 0
            self.canvas.itemconfig(self.character_id,
                                   image=self.frames[self.current_frame])

    def start_animation(self, event=None):
        '''
        starts the attack

        reduces mana, sets attack to true and calls the update frame method
        '''
        if not self.attack and self.alive and not (pause
                                                   or boss) and self.mana != 0:
            self.attack = True
            self.mana -= 1
            self.update_mana_bar()
            self.current_frame = 0
            self.update_frame()

    def move_up(self, event):
        '''moves character up one row'''
        if self.y != 50 and not self.attack and self.alive and not (pause
                                                                    or boss):
            self.y -= 250
            self.canvas.coords(self.character_id, self.x, self.y)

    def move_down(self, event):
        '''moves character down one row'''
        if self.y != 550 and not self.attack and self.alive and not (pause
                                                                     or boss):
            self.y += 250
            self.canvas.coords(self.character_id, self.x, self.y)

    def die(self):
        '''sets fighter. alive to false and displays death screen'''
        global prev_screen
        self.alive = False
        show_frame(death_screen)
        prev_screen = death_screen
        root.unbind('<b>')
        root.bind('<b>', out_boss)
        root.unbind('<p>')


def image_resize(file):
    '''
    resizes an image to fit the frame

    parameter is the file to be resized
    '''
    og_image = Image.open(file)
    new_image = og_image.resize((FRAME_WIDTH, FRAME_HEIGHT))
    return ImageTk.PhotoImage(new_image)


def show_frame(frame):
    '''
    raises the desired frame to the front

    the parameter is the desired frame
    '''
    frame.tkraise()


def show_main():
    '''shows the main menu'''
    global prev_screen
    show_frame(main_menu)
    prev_screen = main_menu


main_menu = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
char_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
diff_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
opt_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
key_bind_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
game_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
death_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
victory_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
pause_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
boss_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
name_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
leaderboard_screen = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
for frame in (main_menu, char_screen, diff_screen, opt_screen, key_bind_screen,
              game_screen, death_screen, victory_screen, pause_screen,
              boss_screen, name_screen, leaderboard_screen):
    frame.place(x=0, y=0, relwidth=1, relheight=1)

game_canvas = tk.Canvas(game_screen, width=FRAME_WIDTH, height=FRAME_HEIGHT)
zombies_num = 0
zombies = []


def spawn_zombie():
    '''spawns zombies randomly on 3 different y levels'''
    global zombie, zombies_num, time_since_prev_zom
    time_since_prev_zom = 0
    new_x = 1550
    new_y = random.choice([100, 350, 600])
    zombies_num += 1
    zombie = Zombie(game_canvas, new_x, new_y)
    zombies.append(zombie)


def spawn_zombie_periodically():
    '''
    calls spawn zombies after certain intervals

    time between spawn depends on the difficulty
    delay is for pause or boss key so the game
    waits before spawning a zombie after unpausing
    '''
    global zombies_num, chosen_diff, zombie_spawn_delay
    global remaining_spawn_time, delay
    if zombies_num < 20 and not (pause or boss):
        if fighter.alive:
            spawn_zombie()
            if zombies_num == 1:
                delay = chosen_diff[0]
            elif zombies_num <= 10:
                delay = chosen_diff[1]
            else:
                delay = chosen_diff[2]

        # Schedule the next spawn and keep track of the delay
        remaining_spawn_time = delay
        zombie_spawn_delay = root.after(delay, spawn_zombie_periodically)
    else:
        zombie_spawn_delay = None


def start_game():
    '''counts the number of games'''
    global game_started, num_games_played
    num_games_played += 1
    if not game_started:
        game_started = True
        start_game_logic()


def pause_fn(event=None):
    '''
    pauses the game

    shows the pause screen
    calculates a delay for zombie spawning after unpausing
    '''
    global pause, boss, zombie_spawn_delay

    pause = not pause
    if boss:
        show_frame(boss_screen)
    elif pause:
        show_frame(pause_screen)
        if zombie_spawn_delay is not None:
            root.after_cancel(zombie_spawn_delay)
            zombie_spawn_delay = None
            root.unbind('<b>')
    else:
        show_frame(game_screen)
        for zombie in zombies:
            zombie.animate()
        if remaining_spawn_time is not None:
            zombie_spawn_delay = root.after(remaining_spawn_time,
                                            spawn_zombie_periodically)
        root.bind('<b>', boss_fn)


def start_game_logic():
    '''
    starts the game

    displays game background, binds controls creates instance of
    fighter class
    '''
    global fighter, background_image, chosen_keys, pause
    if not pause or not boss:
        game_canvas.pack()
        background_image = image_resize("Game BG.png")
        game_canvas.create_image(0, 0, image=background_image, anchor="nw")
        fighter = Fighter(game_canvas, 0, 50, name, 10, 5)
        root.bind(chosen_keys[2], fighter.start_animation)
        root.bind(chosen_keys[0], fighter.move_up)
        root.bind(chosen_keys[1], fighter.move_down)
        spawn_zombie_periodically()
        root.bind('<p>', pause_fn)
        root.bind('<b>', boss_fn)
    else:
        show_frame(pause_screen)


def go_to_name():
    '''displays name screen'''
    global prev_screen
    show_frame(name_screen)
    prev_screen = name_screen
    root.bind('<b>', out_boss)


def go_to_opt():
    '''displays options screen'''
    global prev_screen
    show_frame(opt_screen)
    prev_screen = opt_screen
    root.bind('<b>', out_boss)


def go_to_keybinds():
    '''displays key binds screen'''
    global prev_screen
    show_frame(key_bind_screen)
    prev_screen = key_bind_screen
    root.bind('<b>', out_boss)


# --- Main Menu Screen ---
menu_canvas = tk.Canvas(main_menu,
                        width=FRAME_WIDTH,
                        height=FRAME_HEIGHT,
                        bg="black")
menu_canvas.pack()
bg_image = image_resize("screen/BG image.png")
menu_canvas.create_image(0, 0, anchor="nw", image=bg_image)

start_btn = tk.Button(main_menu,
                      text="Start Game",
                      font=("Arial", 14, "bold"),
                      command=go_to_name)
start_btn.place(x=600, y=250, height=75, width=200)

options_btn = tk.Button(main_menu,
                        text="Options",
                        font=("Arial", 14, "bold"),
                        command=go_to_opt)
options_btn.place(x=600, y=350, height=75, width=200)

exit_btn = tk.Button(main_menu,
                     text="Exit",
                     font=("Arial", 14, "bold"),
                     command=root.quit)
exit_btn.place(x=600, y=450, height=75, width=200)

# --- options Screen ---
opt_canvas = tk.Canvas(opt_screen,
                       width=FRAME_WIDTH,
                       height=FRAME_HEIGHT,
                       bg="black")
opt_canvas.pack()
opt_bg_image = image_resize("screen/Options.png")
opt_canvas.create_image(0, 0, anchor="nw", image=opt_bg_image)

back_to_menu_btn = tk.Button(opt_screen,
                             text="Back to Main Menu",
                             font=("Arial", 14),
                             command=show_main)
back_to_menu_btn.place(x=600, y=200, height=50, width=200)
key_bind_btn = tk.Button(opt_screen,
                         text="choose keybinds",
                         font=("Arial", 14, "bold"),
                         command=go_to_keybinds)
key_bind_btn.place(x=600, y=300, height=50, width=200)


def set_keys(list):
    '''set keybinds to the ones you chose'''
    global chosen_keys
    chosen_keys = list


# --- key binds Screen ---
key_bind_canvas = tk.Canvas(key_bind_screen,
                            width=FRAME_WIDTH,
                            height=FRAME_HEIGHT,
                            bg="black")
key_bind_canvas.pack()
key_bind_bg_image = image_resize("screen/Keybinds.png")
key_bind_canvas.create_image(0, 0, anchor="nw", image=key_bind_bg_image)
UDR_icon = tk.PhotoImage(file="buttons/UDR.png")
UDS_icon = tk.PhotoImage(file="buttons/UDS.png")
WSS_icon = tk.PhotoImage(file="buttons/WSS.png")
UDR_keys_btn = tk.Button(key_bind_screen,
                         image=UDR_icon,
                         command=lambda: set_keys(UDR_keys))
UDR_keys_btn.place(x=300, y=400)
UDS_keys_btn = tk.Button(key_bind_screen,
                         image=UDS_icon,
                         command=lambda: set_keys(UDS_keys))
UDS_keys_btn.place(x=620, y=400)
WSS_keys_btn = tk.Button(key_bind_screen,
                         image=WSS_icon,
                         command=lambda: set_keys(WSS_keys))
WSS_keys_btn.place(x=945, y=400)
UDR_label = tk.Label(key_bind_screen,
                     text="Play with one hand",
                     font=("Arial", 20),
                     bg="grey",
                     fg="white")
UDR_label.place(x=380, y=600, anchor="n")
UDS_label = tk.Label(key_bind_screen,
                     text="Right-handed play",
                     font=("Arial", 20),
                     bg="grey",
                     fg="white")
UDS_label.place(x=700, y=600, anchor="n")
WSS_label = tk.Label(key_bind_screen,
                     text="Left-handed play",
                     font=("Arial", 20),
                     bg="grey",
                     fg="white")
WSS_label.place(x=1025, y=600, anchor="n")
back_to_menu_btn = tk.Button(key_bind_screen,
                             text="Back to Main Menu",
                             font=("Arial", 14),
                             command=show_main)
back_to_menu_btn.place(x=600, y=200, height=50, width=200)

# --- name Screen ---


def submit_form():
    '''
    function for submit button

    only lets the user submit a name if it is 7 characters long
    returns the submitted game
    '''
    global player_name, prev_screen
    temp_name = entry.get()
    if len(temp_name) == 7:
        player_name = temp_name
        show_frame(char_screen)
        prev_screen = char_screen
        root.bind('<b>', out_boss)
        return player_name


def validate_input(input_text):
    ''' stops the user from typing more than 7 characters'''
    if len(input_text) <= 7:
        return True
    else:
        return False


name_canvas = tk.Canvas(name_screen,
                        width=FRAME_WIDTH,
                        height=FRAME_HEIGHT,
                        bg="black")
name_canvas.pack()
name_bg_image = image_resize("screen/Type your NAME.png")
name_canvas.create_image(0, 0, anchor="nw", image=name_bg_image)

validate_cmd = name_screen.register(validate_input)

entry = tk.Entry(name_screen,
                 width=30,
                 validate="key",
                 validatecommand=(validate_cmd, "%P"))
# checks each key entered using %P
entry.place(x=700, y=300, anchor="n")

submit_button = tk.Button(name_screen, text="Submit", command=submit_form)
submit_button.place(x=700, y=350, anchor="n")
back_to_menu_btn = tk.Button(name_screen,
                             text="Back to Main Menu",
                             font=("Arial", 14),
                             command=show_main)
back_to_menu_btn.place(x=600, y=200, height=50, width=200)

# --- choose character Screen ---
name = ""
char_canvas = tk.Canvas(char_screen,
                        width=FRAME_WIDTH,
                        height=FRAME_HEIGHT,
                        bg="black")
char_canvas.pack()
char_bg_image = image_resize("screen/Choose CHAR.png")
char_canvas.create_image(0, 0, anchor="nw", image=char_bg_image)
cloudy_icon = tk.PhotoImage(file="Cloudy.png")
hammer_icon = tk.PhotoImage(file="Hammer.png")


def combined_command_cloudy():
    '''sets the character and displays the difficulty screen'''
    global name, prev_screen
    name = "cloudy"
    show_frame(diff_screen)
    prev_screen = diff_screen
    root.bind('<b>', out_boss)


def combined_command_hammer():
    '''sets the character and displays the difficulty screen'''
    global name, prev_screen
    name = "hammer"
    show_frame(diff_screen)
    prev_screen = diff_screen
    root.bind('<b>', out_boss)


back_to_menu_btn = tk.Button(char_screen,
                             text="Back to Main Menu",
                             font=("Arial", 14),
                             command=show_main)
back_to_menu_btn.place(x=600, y=200, height=50, width=200)
cloudy_btn = tk.Button(char_screen,
                       image=cloudy_icon,
                       command=combined_command_cloudy)
cloudy_btn.place(x=300, y=400)
hammer_btn = tk.Button(char_screen,
                       image=hammer_icon,
                       command=combined_command_hammer)
hammer_btn.place(x=900, y=400)
cloudy_label = tk.Label(char_screen,
                        text="shorter attack (cloudy)",
                        font=("Arial", 20),
                        bg="grey",
                        fg="white")
cloudy_label.place(x=400, y=600, anchor="n")
hammer_label = tk.Label(char_screen,
                        text="longer attack (hammer)",
                        font=("Arial", 20),
                        bg="grey",
                        fg="white")
hammer_label.place(x=1000, y=600, anchor="n")

# --- choose difficulty Screen ---


def set_difficulty(list):
    '''sets the difficulty and saves it for the leaderboard'''
    global chosen_diff, diff_level
    chosen_diff = list
    if list == DIFF1:
        diff_level = "z"
    elif list == DIFF2:
        diff_level = "mz"
    else:
        diff_level = "tmz"
    show_frame(game_screen)
    if num_games_played >= 1:
        # resets game when difficulty is selected
        reset_game()
    else:
        start_game()


diff_canvas = tk.Canvas(diff_screen,
                        width=FRAME_WIDTH,
                        height=FRAME_HEIGHT,
                        bg="black")
diff_canvas.pack()
diff_bg_image = image_resize("screen/Choose DIFF.png")
diff_canvas.create_image(0, 0, anchor="nw", image=diff_bg_image)
back_to_menu_btn = tk.Button(diff_screen,
                             text="Back to Main Menu",
                             font=("Arial", 14),
                             command=show_main)
back_to_menu_btn.place(x=600, y=200, height=50, width=200)
diff1_icon = tk.PhotoImage(file="buttons/diff1.png")
diff2_icon = tk.PhotoImage(file="buttons/diff2.png")
diff3_icon = tk.PhotoImage(file="buttons/diff3.png")
diff1_keys_btn = tk.Button(diff_screen,
                           image=diff1_icon,
                           command=lambda: set_difficulty(DIFF1))
diff1_keys_btn.place(x=700, y=300, anchor="n")
diff2_keys_btn = tk.Button(diff_screen,
                           image=diff2_icon,
                           command=lambda: set_difficulty(DIFF2))
diff2_keys_btn.place(x=700, y=450, anchor="n")
diff3_keys_btn = tk.Button(diff_screen,
                           image=diff3_icon,
                           command=lambda: set_difficulty(DIFF3))
diff3_keys_btn.place(x=700, y=600, anchor="n")


def go_to_ldr():
    '''displays the leaderboard screen and calls add score'''
    global prev_screen
    show_frame(leaderboard_screen)
    prev_screen = leaderboard_screen
    add_score()
    update_leaderboard()
    root.bind('<b>', out_boss)
    root.unbind('<p>')


# --- game over Screen ---
death_canvas = tk.Canvas(death_screen,
                         width=FRAME_WIDTH,
                         height=FRAME_HEIGHT,
                         bg="black")
death_canvas.pack()
death_bg_image = image_resize("screen/GAME OVER.png")
death_canvas.create_image(0, 0, anchor="nw", image=death_bg_image)
go_to_lboard = tk.Button(death_screen,
                         text="Go To Leaderboard",
                         font=("Arial", 14),
                         command=go_to_ldr)
go_to_lboard.place(x=600, y=200, height=50, width=200)

# --- victory Screen ---
victory_canvas = tk.Canvas(victory_screen,
                           width=FRAME_WIDTH,
                           height=FRAME_HEIGHT,
                           bg="black")
victory_canvas.pack()
victory_bg_image = image_resize("screen/VICTORY.png")
victory_canvas.create_image(0, 0, anchor="nw", image=victory_bg_image)
go_to_lboard = tk.Button(victory_screen,
                         text="Go To Leaderboard",
                         font=("Arial", 14),
                         command=go_to_ldr)
go_to_lboard.place(x=600, y=200, height=50, width=200)

leaderboard_data = []

# Load the leaderboard data from the file when the program starts


def load_leaderboard():
    '''
    loads the leaderboard from the text file

    reads the leaderboard textfile and adds each line to the
    leaderboard data list to be displayed on the leaderboard
    '''
    global leaderboard_data
    try:
        with open("leaderboard.txt", "r") as file:
            leaderboard_data = []
            for line in file:
                parts = line.strip().split(", ")
                name, score, difficulty, character = parts
                leaderboard_data.append({
                    "name": name,
                    "score": int(score),
                    "difficulty": difficulty,
                    "character": character
                })
    except FileNotFoundError:
        leaderboard_data = []
        # If the file doesn't exist, start with an empty leaderboard


# Save the leaderboard data to the file
def save_leaderboard():
    '''this writes the new entry into the leaderboard text file'''
    with open("leaderboard.txt", "w") as file:
        for entry in leaderboard_data:
            file.write(
                f"{entry['name']}, {entry['score']}, " +
                f"{entry['difficulty']}, {entry['character']}\n"
            )


# Update the leaderboard display
def update_leaderboard():
    '''updates the leaderboard to show the new entry'''
    sorted_data = sorted(leaderboard_data,
                         key=lambda x: x["score"],
                         reverse=True)

    leaderboard_listbox.delete(0, tk.END)

    for i, entry in enumerate(sorted_data):
        leaderboard_listbox.insert(
            tk.END,
            f"Rank {i + 1}: {entry['name']} - {entry['score']}, " +
            f"{entry['difficulty']}, {entry['character']}"
        )


# Add a new score to the leaderboard
def add_score():
    '''adds the details of the new game to the leaderboard'''
    global player_name, score, diff_level, fighter

    leaderboard_data.append({
        "name": player_name,
        "score": score,
        "difficulty": diff_level,
        "character": fighter.name
    })

    if len(leaderboard_data) > 12:
        leaderboard_data.sort(key=lambda x: x["score"], reverse=True)
        leaderboard_data.pop()

    update_leaderboard()
    save_leaderboard()
    # Save the updated leaderboard to the file


# Example to initialize the application and load leaderboard
load_leaderboard()

leaderboard_canvas = tk.Canvas(leaderboard_screen,
                               width=FRAME_WIDTH,
                               height=FRAME_HEIGHT,
                               bg="black")
leaderboard_canvas.pack()
leaderboard_bg_image = image_resize("screen/Leaderboard.png")
leaderboard_canvas.create_image(0, 0, anchor="nw", image=leaderboard_bg_image)
back_to_menu_btn = tk.Button(leaderboard_screen,
                             text="Back to Main Menu",
                             font=("Arial", 14),
                             command=show_main)
back_to_menu_btn.place(x=600, y=200, height=50, width=200)

leaderboard_listbox = tk.Listbox(leaderboard_screen,
                                 height=10,
                                 width=40,
                                 font=("Arial", 12))
leaderboard_listbox.place(x=700, y=300, anchor="n")
# update_leaderboard()

# --- pause Screen ---
pause_canvas = tk.Canvas(pause_screen,
                         width=FRAME_WIDTH,
                         height=FRAME_HEIGHT,
                         bg="black")
pause_canvas.pack()
pause_bg_image = image_resize("screen/Pause.png")
pause_canvas.create_image(0, 0, anchor="nw", image=pause_bg_image)


def boss_fn(event=None):
    '''
    functionality of the boss key inside game loop

    delays next zombie spawn after returning to the game
    pauses the game while boss screen is displayed
    '''
    global pause, boss, zombie_spawn_delay
    boss = not boss
    pause = not pause
    root.unbind('<p>')
    if boss:
        show_frame(boss_screen)
        if zombie_spawn_delay is not None:
            root.after_cancel(zombie_spawn_delay)
            zombie_spawn_delay = None
            root.unbind('<p>')
    else:
        show_frame(game_screen)
        for zombie in zombies:
            zombie.animate()
        if remaining_spawn_time is not None:
            zombie_spawn_delay = root.after(remaining_spawn_time,
                                            spawn_zombie_periodically)
        root.bind('<p>', pause_fn)


# --- boss Screen ---
boss_canvas = tk.Canvas(boss_screen,
                        width=FRAME_WIDTH,
                        height=FRAME_HEIGHT,
                        bg="black")
boss_canvas.pack()
boss_bg_image = image_resize("screen/boss key.jpeg")
boss_canvas.create_image(0, 0, anchor="nw", image=boss_bg_image)

show_frame(main_menu)

score_label = tk.Label(game_screen,
                       text=f"Score: {score}",
                       font=("Arial", 20),
                       bg="grey",
                       fg="white")
score_label.pack(anchor="nw")

final_score_label1 = tk.Label(death_screen,
                              text=f"Final Score: {score}",
                              font=("Arial", 20),
                              bg="grey",
                              fg="white")
final_score_label1.place(x=700, y=25, anchor="n")

final_score_label2 = tk.Label(victory_screen,
                              text=f"Final Score: {score}",
                              font=("Arial", 20),
                              bg="grey",
                              fg="white")
final_score_label2.place(x=700, y=25, anchor="n")


def reset_game():
    '''
    resets game values

    resets game values to initial values
    rebinds controls
    calls start game logic
    resets score label
    '''
    global score, zombies, zombies_num, fighter
    global game_started, pause, zombie_spawn_delay

    score = 0
    zombies_num = 0
    zombies.clear()
    fighter.hp = fighter.max_hp
    fighter.mana = fighter.max_mana
    fighter.attack = False
    fighter.alive = True
    pause = False
    game_started = False

    game_canvas.delete("all")

    background_image = image_resize("Game BG.png")
    game_canvas.create_image(0, 0, image=background_image, anchor="nw")

    fighter.update_health_bar()

    if zombie_spawn_delay:
        root.after_cancel(zombie_spawn_delay)
        zombie_spawn_delay = None

    start_game_logic()

    root.bind(chosen_keys[2], fighter.start_animation)
    root.bind(chosen_keys[0], fighter.move_up)
    root.bind(chosen_keys[1], fighter.move_down)
    root.bind('<p>', pause_fn)
    root.bind('<b>', boss_fn)

    # Reset the score display
    score_label.config(text=f"Score: {score}")
    final_score_label1.config(text=f"Score: {score}")
    final_score_label2.config(text=f"Score: {score}")


# Run the Tkinter event loop
root.mainloop()
