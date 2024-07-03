import ctypes
import Protocol
import pygame
import button
from enum import Enum
from Server import commands

logo_path = "./logo.png"


# **states are indactions of what screen the client should see**
# Enums as the states for easier understanding.
class user(Enum):
    guest = 0
    login = 1
    sign_up = 2
    user = 3
    joins = 4
    creates = 5
    playing = 6
    leave = 7


# Check valid input from users
def check_letters(letter):
    return len(letter) == 1 and ((47 < ord(letter) < 58) or (64 < ord(letter) < 91) or (96 < ord(letter) < 123))


def check_numbers(number):
    return len(number) == 1 and ((47 < ord(number) < 58))


class User_interface:

    def __init__(self, canvas):

        self.canvas = canvas
        self.display = canvas.screen
        self.app = True
        self.user = user.guest

    # Main interface loop
    def interface(self):

        pygame.display.set_caption("SketchTogether")
        # Control all the diffrent screens, each screen has its own loop
        while self.app:
            self.loop_guest()

            self.loop_login()

            self.loop_sign_up()

            self.loop_user()

            self.loop_joins()

            self.loop_creates()

            self.loop_playing()

        pygame.quit()

    # Runs the guest loop
    def loop_guest(self):

        bg_color = (255, 251, 232)

        login = button.Button(325, 600, 150, 100, (38, 40, 46), "Login-in", self.display)

        sign_up = button.Button(525, 600, 150, 100, (38, 40, 46), "Sign-up", self.display)

        quit = button.Button(425, 750, 150, 100, (38, 40, 46), "Quit", self.display)

        # Calls to start the screen of the state
        self.start_guest_screen(login, sign_up, bg_color, quit)

        # Looks at all the input the client gave while they are in this screen
        while self.user == user.guest:
            # Check which button the client clicked
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if quit.button.collidepoint(event.pos):
                        self.app = False
                        self.user = user.leave

                    elif login.button.collidepoint(event.pos):
                        # Changes the state of the user sends him to login
                        self.user = user.login

                    elif sign_up.button.collidepoint(event.pos):
                        # Changes the state of the user sends him to signup
                        self.user = user.sign_up

    # initialize the guest screen
    def start_guest_screen(self, login, sign_up, bg_color, quit):
        self.display = pygame.display.set_mode((self.canvas.width, self.canvas.height))

        self.display.fill(bg_color)

        logo = pygame.image.load(logo_path)

        self.display.blit(logo, (240, 40))

        login.screen = self.display
        sign_up.screen = self.display
        quit.screen = self.display

        quit.create_draw()
        login.create_draw()
        sign_up.create_draw()

        pygame.display.flip()

    # Manages the login page
    def loop_login(self):
        # Creating all the variables once, so we can interact with them
        bg_color = (255, 251, 232)

        font = pygame.font.SysFont('Courier New', 30)

        label_username = font.render("Username:", True, (0, 0, 0))
        label_password = font.render("Password:", True, (0, 0, 0))

        submit = button.Button(450, 800, 120, 60, (38, 40, 46), "Submit", self.display)

        back = button.Button(450, 900, 120, 60, (0, 0, 0), "Back", self.display)

        clear_buttons = pygame.Rect(0, 600, 1000, 600)
        input_box_user = pygame.Rect(350, 600, 300, 50)
        input_box_pass = pygame.Rect(350, 700, 300, 50)

        color_inactive = (169, 169, 169)

        color_active = (0, 0, 0)
        pass_color = color_inactive
        color = color_inactive

        user_active = False
        pass_active = False

        user_text = ''
        pass_text = ''
        ui_pass = ''
        # Call to the function to initialize, needs to be param so we can interact with it.
        self.start_login_input_screen(bg_color, input_box_user, input_box_pass, color, label_username, label_password,
                                      submit, back, clear_buttons)

        while self.user == user.login:
            # Checks for clicks and typing
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if back.button.collidepoint(event.pos):

                        # Change state
                        self.user = user.guest

                    elif submit.button.collidepoint(event.pos):
                        clear_error = pygame.Rect(0, 525, 1000, 35)
                        error_text = ""
                        if len(user_text) < 4 and len(pass_text) < 5:
                            error_text = "Password & Username too short"

                        elif len(user_text) < 4:
                            error_text = "Username too short, least 4"
                        elif len(pass_text) < 5:
                            error_text = "Password too short, least 5"

                        if len(user_text) > 3 and len(pass_text) > 4:
                            Protocol.send_gen(self.canvas.key, [user_text, pass_text], self.canvas.socket,
                                              commands.login.value)
                            match, server_text = Protocol.recv_gen(self.canvas.key, self.canvas.socket)
                            print(f"From server: {type(match)}")
                            error_text = server_text
                            if match == "True":
                                self.clear_1_input(clear_error)
                                # Change state
                                self.user = user.user

                        print(f"error msg: {error_text}")
                        user_text = ""
                        pass_text = ""
                        ui_pass = ""
                        self.clear_1_input(input_box_user)

                        self.clear_1_input(input_box_pass)

                        error_len_x = 500 - (18 * len(error_text) / 2)

                        error_txt_surface = font.render(error_text, True, (255, 0, 0))
                        self.clear_1_input(clear_error, bg_color)

                        # 500 middle of the screen, 18 width of a snigle char, make sure its in the middle
                        self.display.blit(error_txt_surface, (error_len_x, 525))

                    # Check for pressing the input boxes, highlight and un highlight.
                    elif input_box_user.collidepoint(event.pos):
                        user_active = not user_active
                        if pass_active:
                            pass_active = False

                    # Check for pressing the input boxes, highlight and un highlight.
                    elif input_box_pass.collidepoint(event.pos):
                        if user_active:
                            user_active = False
                        pass_active = not pass_active

                    else:
                        user_active = False
                        pass_active = False
                    # Change the current color of the input box.
                    color = color_active if user_active else color_inactive
                    pass_color = color_active if pass_active else color_inactive
                # Check for typing
                if event.type == pygame.KEYDOWN:
                    if user_active:
                        # Check for deleting char
                        if event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                            self.clear_1_input(input_box_user)
                            txt_surface = font.render(user_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_user.x + 5, input_box_user.y + 5))
                        else:
                            # Only if char is legal and not more than total 16 add it
                            if len(user_text) < 16 and check_letters(event.unicode):
                                user_text += event.unicode
                    # Same as user but keeps the password input and showing '*' instead
                    elif pass_active:
                        if event.key == pygame.K_BACKSPACE:
                            pass_text = pass_text[:-1]
                            ui_pass = ui_pass[:-1]
                            self.clear_1_input(input_box_pass)
                            txt_surface = font.render(ui_pass, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_pass.x + 5, input_box_pass.y + 13))
                        else:
                            if len(pass_text) < 16 and check_letters(event.unicode):
                                pass_text += event.unicode
                                ui_pass += "*"

            # Update the screen with what was wrote + color of input box
            user_txt_surface = font.render(user_text, True, (0, 0, 0))

            ui_pass_surface = font.render(ui_pass, True, (0, 0, 0))

            self.display.blit(user_txt_surface, (input_box_user.x + 5, input_box_user.y + 5))
            self.display.blit(ui_pass_surface, (input_box_pass.x + 5, input_box_pass.y + 13))

            pygame.draw.rect(self.display, color, input_box_user, 5)
            pygame.draw.rect(self.display, pass_color, input_box_pass, 5)

            pygame.display.flip()

    # initialize the login screen
    def start_login_input_screen(self, bg_color, input_box_user, input_box_pass, color, label_username, label_password,
                                 submit, back, clear_buttons):
        # del old screen info
        self.display.fill(bg_color, clear_buttons)

        # make boxes white
        self.clear_2_input(input_box_user, input_box_pass)

        pygame.draw.rect(self.display, color, input_box_user, 5)
        pygame.draw.rect(self.display, color, input_box_pass, 5)

        self.display.blit(label_username, (input_box_user.x - 160, input_box_user.y + 10))
        self.display.blit(label_password, (input_box_pass.x - 160, input_box_pass.y + 10))

        submit.create_draw()
        back.create_draw()
        pygame.display.flip()

    # SIGNUP Loop-----------------------------------------------
    def loop_sign_up(self):
        # Creating all the variables once, so we can interact with them
        bg_color = (255, 251, 232)

        label_font = pygame.font.SysFont('Courier New', 25)
        font = pygame.font.SysFont('Courier New', 30)

        label_create_user = label_font.render("Create a Username:", True, (0, 0, 0))
        label_create_pass = label_font.render("Create a Password:", True, (0, 0, 0))

        submit = button.Button(450, 800, 120, 60, (38, 40, 46), "Submit", self.display)

        back = button.Button(450, 900, 120, 60, (0, 0, 0), "Back", self.display)

        clear_buttons = pygame.Rect(0, 600, 1000, 600)

        input_box_user = pygame.Rect(350, 600, 300, 50)
        input_box_pass = pygame.Rect(350, 700, 300, 50)
        color_inactive = (169, 169, 169)

        color_active = (0, 0, 0)
        pass_color = color_inactive
        color = color_inactive

        user_active = False
        pass_active = False

        user_text = ''
        pass_text = ''

        ui_pass = ''
        # Call to the function to initialize, needs to be param so we can interact with it.
        self.start_sign_up_input_screen(bg_color, input_box_user, input_box_pass, color, label_create_user,
                                        label_create_pass, submit, back,
                                        clear_buttons)
        # Same loop as login
        while self.user == user.sign_up:
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Checks where client clicked to know if in focus of box
                    if input_box_user.collidepoint(event.pos):
                        user_active = not user_active
                        if pass_active:
                            pass_active = False

                    elif input_box_pass.collidepoint(event.pos):
                        if user_active:
                            user_active = False
                        pass_active = not pass_active

                    elif back.button.collidepoint(event.pos):
                        # Change the state
                        self.user = user.guest

                    elif submit.button.collidepoint(event.pos):
                        clear_error = pygame.Rect(0, 525, 1000, 35)
                        error_text = ""
                        if len(user_text) < 4 and len(pass_text) < 5:
                            error_text = "Password & Username too short"

                        elif len(user_text) < 4:
                            error_text = "Username too short, least 4"
                        elif len(pass_text) < 5:
                            error_text = "Password too short, least 5"

                        if len(user_text) > 3 and len(pass_text) > 4:
                            Protocol.send_gen(self.canvas.key, [user_text, pass_text], self.canvas.socket,
                                              commands.sign_up.value)
                            answer, server_text = Protocol.recv_gen(self.canvas.key, self.canvas.socket)
                            print(answer)
                            error_text = server_text
                            if answer == "True":
                                self.clear_1_input(clear_error)
                                # Change state
                                self.user = user.user

                        user_text = ""
                        pass_text = ""
                        ui_pass = ""
                        self.clear_1_input(input_box_user)

                        self.clear_1_input(input_box_pass)

                        error_len_x = 500 - (18 * len(error_text) / 2)

                        error_txt_surface = font.render(error_text, True, (255, 0, 0))
                        self.clear_1_input(clear_error, bg_color)

                        # 500 middle of the screen, 18 width of a snigle char, make sure its in the middle

                        self.display.blit(error_txt_surface, (error_len_x, 525))

                    else:
                        user_active = False
                        pass_active = False
                    # Change the current color of the input box.
                    color = color_active if user_active else color_inactive
                    pass_color = color_active if pass_active else color_inactive

                if event.type == pygame.KEYDOWN:
                    if user_active:
                        # delete a char
                        if event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                            self.clear_1_input(input_box_user)
                            txt_surface = font.render(user_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_user.x + 5, input_box_user.y + 5))
                        else:
                            # only if legal can add the text
                            if len(user_text) < 16 and check_letters(event.unicode):
                                user_text += event.unicode

                    # If we focuesd on this box, in it and want to write in it
                    elif pass_active:

                        if event.key == pygame.K_BACKSPACE:
                            pass_text = pass_text[:-1]
                            ui_pass = ui_pass[:-1]
                            self.clear_1_input(input_box_pass)
                            txt_surface = font.render(ui_pass, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_pass.x + 5, input_box_pass.y + 13))
                        else:
                            if len(pass_text) < 16 and check_letters(event.unicode):
                                pass_text += event.unicode
                                ui_pass += "*"

            # Updates the input boxes to show what we wrote + color of boxes
            user_txt_surface = font.render(user_text, True, (0, 0, 0))

            ui_pass_surface = font.render(ui_pass, True, (0, 0, 0))

            self.display.blit(user_txt_surface, (input_box_user.x + 5, input_box_user.y + 5))
            self.display.blit(ui_pass_surface, (input_box_pass.x + 5, input_box_pass.y + 13))

            pygame.draw.rect(self.display, color, input_box_user, 5)
            pygame.draw.rect(self.display, pass_color, input_box_pass, 5)

            pygame.display.flip()

    # initialize the sign_up screen
    def start_sign_up_input_screen(self, bg_color, input_box_user, input_box_pass, color, label_create_user,
                                   label_create_pass, submit, back, clear_buttons):
        # del old screen info
        self.display.fill(bg_color, clear_buttons)

        # make boxes white
        self.clear_2_input(input_box_user, input_box_pass)

        pygame.draw.rect(self.display, color, input_box_user, 5)
        pygame.draw.rect(self.display, color, input_box_pass, 5)

        self.display.blit(label_create_user, (input_box_user.x - 270, input_box_user.y + 10))
        self.display.blit(label_create_pass, (input_box_pass.x - 270, input_box_pass.y + 10))

        submit.create_draw()
        back.create_draw()
        pygame.display.flip()

    # User logged in the system
    def loop_user(self):

        bg_color = (255, 251, 232)

        joins = button.Button(250, 600, 200, 100, (38, 40, 46), "Join a room", self.display)
        creates = button.Button(550, 600, 200, 100, (38, 40, 46), "Create a room", self.display)
        log_out = button.Button(425, 750, 150, 80, (38, 40, 46), "Log-out", self.display)

        # #Call to the function to initialize, needs to be param so we can interact with it.
        self.start_user_screen(bg_color, joins, creates, log_out)

        # Checks if state
        while self.user == user.user:
            # Checks what button we clicked
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if joins.button.collidepoint(event.pos):
                        # start join
                        self.user = user.joins

                    elif log_out.button.collidepoint(event.pos):
                        self.user = user.guest

                    elif creates.button.collidepoint(event.pos):
                        # start creation
                        self.user = user.creates

    # initialize the user home screen
    def start_user_screen(self, bg_color, joins, creates, log_out):

        clear_everything_but_logo = pygame.Rect(0, 600, 1000, 600)

        pygame.draw.rect(self.display, bg_color, clear_everything_but_logo)

        joins.create_draw()
        creates.create_draw()
        log_out.create_draw()

        pygame.display.flip()

    def loop_joins(self):
        # Creating all the variables once, so we can interact with them
        bg_color = (255, 251, 232)

        font = pygame.font.SysFont('Courier New', 30)
        label_room = font.render("Room Name:", True, (0, 0, 0))
        label_code = font.render("Enter Code:", True, (0, 0, 0))

        join = button.Button(425, 800, 150, 50, (38, 40, 46), "Join", self.display)

        back = button.Button(425, 900, 150, 50, (38, 40, 46), "Back", self.display)

        clear_buttons = pygame.Rect(0, 600, 1000, 600)
        input_box_room = pygame.Rect(350, 600, 300, 50)
        input_box_code = pygame.Rect(350, 700, 300, 50)

        color_inactive = (169, 169, 169)

        color_active = (0, 0, 0)
        color = color_inactive
        room_color = color_inactive
        code_active = False
        room_active = False
        code_text = ''
        room_text = ''
        scr_width, scr_height = self.get_screen_size()

        # Call to the function to initialize, needs to be param so we can interact with it.
        self.start_joins(bg_color, input_box_room, input_box_code, color, label_room, label_code, join, back,
                         clear_buttons)

        while self.user == user.joins:
            for event in pygame.event.get():

                # Checked what buttons were clicked and focus and out focus of input boxes
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if back.button.collidepoint(event.pos):

                        self.user = user.user

                    elif join.button.collidepoint(event.pos):
                        clear_error = pygame.Rect(0, 525, 1000, 35)
                        error_text = ""
                        if len(room_text) < 4 and len(code_text) < 5:
                            error_text = "Room & Password too short"

                        elif len(room_text) < 4:
                            error_text = "Room too short, least 4"
                        elif len(code_text) < 5:
                            error_text = "Password too short, least 5"

                        if len(room_text) > 3 and len(code_text) > 4:
                            Protocol.send_gen(self.canvas.key, [room_text, code_text, scr_width, scr_height],
                                              self.canvas.socket, commands.join.value)
                            match, server_text, server_width, server_height = Protocol.recv_gen(self.canvas.key,
                                                                                                self.canvas.socket)
                            error_text = server_text
                            print(f"my {scr_width}")
                            print(f"my {scr_height}")
                            print(server_width)
                            print(server_height)
                            if match == "True":
                                self.canvas.width = int(server_width)
                                self.canvas.height = int(server_height)
                                self.clear_1_input(clear_error)
                                # Change state
                                self.user = user.playing

                        print(f"error msg: {error_text}")
                        room_text = ""
                        code_text = ""
                        self.clear_1_input(input_box_room)

                        self.clear_1_input(input_box_code)

                        error_len_x = 500 - (18 * len(error_text) / 2)

                        error_txt_surface = font.render(error_text, True, (255, 0, 0))
                        self.clear_1_input(clear_error, bg_color)
                        # 500 middle of the screen, 18 width of a snigle char, make sure its in the middle
                        self.display.blit(error_txt_surface, (error_len_x, 525))


                    elif input_box_room.collidepoint(event.pos):
                        room_active = not room_active
                        code_active = False
                    elif input_box_code.collidepoint(event.pos):
                        code_active = not code_active
                        room_active = False

                    else:
                        code_active = False
                        room_active = False

                    # Change the current color of the input box.
                    color = color_active if code_active else color_inactive
                    room_color = color_active if room_active else color_inactive

                # Same as all the input boxes before
                if event.type == pygame.KEYDOWN:
                    if code_active:

                        if event.key == pygame.K_BACKSPACE:
                            code_text = code_text[:-1]
                            self.clear_1_input(input_box_code)
                            txt_surface = font.render(code_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_code.x + 5, input_box_code.y + 8))
                        else:
                            if len(code_text) < 16 and check_letters(event.unicode):
                                code_text += event.unicode
                    # Write or delete text from input box
                    elif room_active:
                        if event.key == pygame.K_BACKSPACE:
                            room_text = room_text[:-1]
                            self.clear_1_input(input_box_room)
                            txt_surface = font.render(room_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_room.x + 5, input_box_room.y + 8))
                        else:
                            if len(room_text) < 16 and check_letters(event.unicode):
                                room_text += event.unicode

            # Update the screen and box state
            code_txt_surface = font.render(code_text, True, (0, 0, 0))
            room_txt_surface = font.render(room_text, True, (0, 0, 0))
            self.display.blit(code_txt_surface, (input_box_code.x + 5, input_box_code.y + 8))
            self.display.blit(room_txt_surface, (input_box_room.x + 5, input_box_room.y + 8))

            pygame.draw.rect(self.display, color, input_box_code, 5)
            pygame.draw.rect(self.display, room_color, input_box_room, 5)
            pygame.display.flip()

    # initialize the join a room screen
    def start_joins(self, bg_color, input_box_room, input_box_code, color, label_room, label_code, join, back,
                    clear_buttons):

        # del old screen info
        self.display.fill(bg_color, clear_buttons)

        # make boxes white
        self.clear_1_input(input_box_code)
        self.clear_1_input(input_box_room)

        pygame.draw.rect(self.display, color, input_box_code, 5)
        pygame.draw.rect(self.display, color, input_box_room, 5)

        self.display.blit(label_code, (input_box_code.x - 200, input_box_code.y + 10))
        self.display.blit(label_room, (input_box_room.x - 180, input_box_room.y + 10))

        join.create_draw()
        back.create_draw()
        pygame.display.flip()

    def loop_creates(self):
        # Creating all the variables once, so we can interact with them
        bg_color = (255, 251, 232)

        font = pygame.font.SysFont('Courier New', 30)
        error_font = pygame.font.SysFont('Courier New', 20)
        label_room = font.render("Create a Room id:", True, (0, 0, 0))

        label_code = font.render("Create a Code:", True, (0, 0, 0))

        label_width = font.render("Choose the width:", True, (0, 0, 0))

        label_height = font.render("Choose the height:", True, (0, 0, 0))

        create = button.Button(300, 910, 150, 40, (38, 40, 46), "Create", self.display)

        back = button.Button(550, 910, 150, 40, (38, 40, 46), "Back", self.display)

        clear_buttons = pygame.Rect(0, 600, 1000, 600)

        input_box_room = pygame.Rect(350, 525, 300, 50)

        input_box_code = pygame.Rect(350, 625, 300, 50)

        input_box_width = pygame.Rect(350, 725, 300, 50)

        input_box_height = pygame.Rect(350, 825, 300, 50)

        color_inactive = (169, 169, 169)

        color_active = (0, 0, 0)

        code_color = color_inactive

        width_color = color_inactive

        height_color = color_inactive

        room_color = color_inactive

        code_active = False
        width_active = False
        height_active = False
        room_active = False

        room_text = ''
        code_text = ''
        width_text = ''
        height_text = ''

        error_text = ''
        scr_width, scr_height = self.get_screen_size()
        # Call to the function to initialize, needs to be param so we can interact with it.
        self.start_creates(bg_color, input_box_code, code_color, label_code, label_width, label_height, create, back,
                           clear_buttons, input_box_width,
                           input_box_height, label_room,
                           input_box_room)

        while self.user == user.creates:
            for event in pygame.event.get():

                # Checked what buttons were clicked and focus and out focus of input boxes
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back.button.collidepoint(event.pos):

                        self.user = user.user

                    elif create.button.collidepoint(event.pos):
                        clear_error = pygame.Rect(0, 480, 1000, 50)
                        size = True
                        print(scr_height)
                        print(scr_width)
                        print(f"{len(height_text)}")
                        print(f"{len(width_text)}")
                        if (len(height_text) < 3) or (len(width_text) < 3) or (int(width_text) < 300) or (
                                int(height_text) < 300) or (
                                int(width_text) > int(scr_width)) or (int(height_text) > int(scr_height)):
                            size = False
                            error_text = "Height or Width are bigger than the screen, must be at least 300px"
                        elif len(room_text) < 4:
                            error_text = "Room name too short, least 4"
                            size = False
                        elif len(code_text) < 5:
                            error_text = "Code too short, least 5"
                            size = False

                        if len(room_text) > 3 and len(code_text) > 4 and size:
                            Protocol.send_gen(self.canvas.key, [room_text, code_text, width_text, height_text],
                                              self.canvas.socket, commands.create.value)
                            to_create, server_text = Protocol.recv_gen(self.canvas.key, self.canvas.socket)
                            print(f"From server: {type(create)}")
                            error_text = server_text
                            if to_create == "True":
                                self.canvas.width = int(width_text)
                                self.canvas.height = int(height_text)
                                # Change state
                                self.user = user.playing

                        print(f"error msg: {error_text}")
                        width_text = ""
                        height_text = ""
                        code_text = ""
                        room_text = ""
                        self.clear_1_input(input_box_room)

                        self.clear_1_input(input_box_code)

                        self.clear_1_input(input_box_height)

                        self.clear_1_input(input_box_width)

                        error_len_x = 100

                        error_txt_surface = error_font.render(error_text, True, (255, 0, 0))
                        self.clear_1_input(clear_error, bg_color)
                        # 480 bcuz text is smaller, needs to fit in screen
                        self.display.blit(error_txt_surface, (error_len_x, 480))




                    elif input_box_code.collidepoint(event.pos):
                        code_active = not code_active
                        width_active = False
                        height_active = False
                        room_active = False


                    elif input_box_width.collidepoint(event.pos):
                        width_active = not width_active
                        code_active = False
                        height_active = False
                        room_active = False

                    elif input_box_height.collidepoint(event.pos):
                        height_active = not height_active
                        code_active = False
                        width_active = False
                        room_active = False

                    elif input_box_room.collidepoint(event.pos):
                        room_active = not room_active
                        code_active = False
                        width_active = False
                        height_active = False

                    else:
                        code_active = False
                        width_active = False
                        height_active = False
                        room_active = False
                    # Change the current color of the input box.
                    code_color = color_active if code_active else color_inactive
                    width_color = color_active if width_active else color_inactive
                    height_color = color_active if height_active else color_inactive
                    room_color = color_active if room_active else color_inactive

                if event.type == pygame.KEYDOWN:
                    if code_active:

                        if event.key == pygame.K_BACKSPACE:
                            # Deleting a char
                            code_text = code_text[:-1]
                            # Removing from the string
                            self.clear_1_input(input_box_code)
                            txt_surface = font.render(code_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_code.x + 5, input_box_code.y + 5))
                        else:
                            if len(code_text) < 16 and check_letters(event.unicode):
                                code_text += event.unicode
                    elif width_active:

                        if event.key == pygame.K_BACKSPACE:
                            # Deleting a char
                            width_text = width_text[:-1]
                            # Removing from the string
                            self.clear_1_input(input_box_width)
                            txt_surface = font.render(width_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_width.x + 5, input_box_width.y + 5))
                        else:
                            if len(width_text) < 16 and check_numbers(event.unicode):
                                width_text += event.unicode

                    elif height_active:

                        # Deleting a char
                        if event.key == pygame.K_BACKSPACE:
                            # Removing from the string
                            height_text = height_text[:-1]
                            self.clear_1_input(input_box_height)
                            txt_surface = font.render(height_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_height.x + 5, input_box_height.y + 5))
                        else:
                            if len(height_text) < 16 and check_numbers(event.unicode):
                                height_text += event.unicode
                    elif room_active:
                        # Deleting a char
                        if event.key == pygame.K_BACKSPACE:
                            # Removing from the string
                            room_text = room_text[:-1]
                            self.clear_1_input(input_box_room)
                            txt_surface = font.render(room_text, True, (0, 0, 0))
                            self.display.blit(txt_surface, (input_box_room.x + 5, input_box_room.y + 5))
                        else:
                            if len(room_text) < 16 and check_letters(event.unicode):
                                room_text += event.unicode

            # Update the written text in the boxes + color.
            code_txt_surface = font.render(code_text, True, (0, 0, 0))

            width_txt_surface = font.render(width_text, True, (0, 0, 0))

            height_txt_surface = font.render(height_text, True, (0, 0, 0))

            room_txt_surface = font.render(room_text, True, (0, 0, 0))

            self.display.blit(room_txt_surface, (input_box_room.x + 5, input_box_room.y + 5))

            self.display.blit(code_txt_surface, (input_box_code.x + 5, input_box_code.y + 5))

            self.display.blit(width_txt_surface, (input_box_width.x + 5, input_box_width.y + 5))

            self.display.blit(height_txt_surface, (input_box_height.x + 5, input_box_height.y + 5))

            pygame.draw.rect(self.display, code_color, input_box_code, 5)

            pygame.draw.rect(self.display, width_color, input_box_width, 5)

            pygame.draw.rect(self.display, height_color, input_box_height, 5)

            pygame.draw.rect(self.display, room_color, input_box_room, 5)

            pygame.display.flip()

    # initialize the create a room screen
    def start_creates(self, bg_color, input_box_code, color, label_code, label_width, label_height, create, back,
                      clear_buttons, input_box_width, input_box_height, label_room,
                      input_box_room):

        # del old screen info
        self.display.fill(bg_color, clear_buttons)

        # make boxes white
        self.clear_1_input(input_box_code)
        self.clear_1_input(input_box_width)
        self.clear_1_input(input_box_height)
        self.clear_1_input(input_box_room)
        pygame.draw.rect(self.display, color, input_box_code, 5)

        pygame.draw.rect(self.display, color, input_box_width, 5)

        pygame.draw.rect(self.display, color, input_box_height, 5)

        pygame.draw.rect(self.display, color, input_box_height, 5)

        pygame.draw.rect(self.display, color, input_box_room, 5)

        self.display.blit(label_code, (input_box_code.x - 250, input_box_code.y + 10))

        self.display.blit(label_width, (input_box_width.x - 305, input_box_width.y + 10))

        self.display.blit(label_height, (input_box_height.x - 325, input_box_height.y + 10))

        self.display.blit(label_room, (input_box_room.x - 305, input_box_room.y + 10))

        create.create_draw()
        back.create_draw()
        pygame.display.flip()

    # Calls the Canvas to manage all the user interactions.
    def loop_playing(self):
        if self.user == user.playing:
            Protocol.send_gen(self.canvas.key, ["nothing"], self.canvas.socket, commands.canvas.value)
            self.canvas.run_room()
            self.canvas.width = 1000
            self.canvas.height = 1000
            # When inside the canvas we press the button to go back to the user main screen we change the state here
            self.user = user.user

    def clear_2_input(self, input1, input2):
        self.display.fill((255, 255, 255), input1)
        self.display.fill((255, 255, 255), input2)

    def clear_1_input(self, input1, color=(255, 255, 255)):
        self.display.fill(color, input1)

    def get_screen_size(self):
        # On Windows
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        return screen_width, screen_height
