import pygame
import Protocol
import threading
import time

import button
import cords

from Server import commands

bg_color = (255, 251, 232)
red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white =(255,255,255)
eraser = (219, 183, 187)
size_color = (38, 40, 46)


def line_intersects_rect(start_pos, end_pos, rect):
    line_rect = pygame.Rect(*start_pos, end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
    return line_rect.colliderect(rect)


class Canvas:

    def __init__(self, width, height, aes_key, socket=None):

        # Intizaltions happens when the start of the room happens so we can start the thread as many times as we need
        self.update_thread = None
        pygame.init()
        self.key = aes_key
        self.width = width
        self.height = height
        self.screen = None
        self.socket = socket
        self.color = 1
        self.radius = 5
        # State of the canvas if false canvas is not active therefore all the info is dealt in the user interface
        self.active = False

        self.background_color = (255, 255, 255)

        # Is the client drawing flag
        self.drawing = False

        self.last_pos = None

    def ratio_width(self, x):

        # Checks the ratio of the normal pixels that work in the 1000, 1000 adjusts based on the screen parameters
        return int(( x / 1000) * self.width)

    def ratio_height(self, y):
        # Checks the ratio of the normal pixels that work in the 1000, 1000 adjusts based on the screen parameters
        return int((y / 1000) * self.height)

    def run_room(self):

        # Creating a new thread that runs check updates, where we as the client check for incoming lines from other clients. needs a thread so we can continue to draw but also get new lines
        self.update_thread = threading.Thread(target=self.check_updates)
        self.update_thread.daemon = True

        self.screen = pygame.display.set_mode((self.width, self.height))

        self.screen.fill(self.background_color)
        # Creation of the pallet------------------------

        config_pallet = pygame.Rect(0, -100, self.width, self.ratio_height(200))

        button_color_red = button.Button(self.ratio_width(25), self.ratio_height(20), self.ratio_width(50),
                                         self.ratio_height(50), red, "", self.screen)

        button_color_blue = button.Button(self.ratio_width(100), self.ratio_height(20), self.ratio_width(50),
                                          self.ratio_height(50), blue, "", self.screen)

        button_color_black = button.Button(self.ratio_width(175), self.ratio_height(20), self.ratio_width(50),
                                           self.ratio_height(50), black, "", self.screen)

        button_color_eraser = button.Button(self.ratio_width(250), self.ratio_height(20), self.ratio_width(85),
                                            self.ratio_height(50), eraser, "Eraser", self.screen)

        button_size_up = button.Button(self.ratio_width(930), self.ratio_height(20), self.ratio_width(50),
                                       self.ratio_height(50), size_color, "+", self.screen)

        button_size_down = button.Button(self.ratio_width(860), self.ratio_height(20), self.ratio_width(50),
                                         self.ratio_height(50), size_color, "-", self.screen)
        print(self.ratio_width(930))
        print(self.ratio_width(860))

        pygame.draw.rect(self.screen, bg_color, config_pallet)

        button_size_up.create_draw()
        button_size_down.create_draw()
        button_color_red.create_draw()
        button_color_blue.create_draw()
        button_color_black.create_draw()
        button_color_eraser.create_draw(20)
        # -------------------------------------
        # Activting the canvas
        self.active = True
        leave = button.Button(self.ratio_width(850), self.ratio_height(900),
                              self.ratio_width(150), self.ratio_height(100), (38, 40, 46), "Leave", self.screen)
        leave.create_draw()

        # Starting the threads
        self.update_thread.start()
        pygame.display.flip()

        # Main loop where we check if app closed
        while self.active:
            # Gets the buttons as a param so we can interact with it and based of collison now what changes to make
            self.handle_events(
                leave, config_pallet, button_color_red, button_color_blue, button_color_black, button_color_eraser,
                button_size_up,
                button_size_down)

            pygame.display.update()
            time.sleep(0.01)

    # Main event loop, checking for every input the client inserted to the screen, and acting accrodingly
    def handle_events(self, leave, config_pallet, button_color_red, button_color_blue, button_color_black,
                      button_color_eraser, button_size_up,
                      button_size_down):


        config_pallet = pygame.Rect(0, 0, self.width, self.ratio_height(100))
        for event in pygame.event.get():
            # Left mouse button
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # If mouse on the button
                if leave.button.collidepoint(event.pos):
                    self.active = False
                    self.drawing = False
                    self.last_pos = None
                    Protocol.send_gen(self.key, ["NOT"], self.socket, commands.canvas_quit.value)

                if config_pallet.collidepoint(event.pos):
                    self.drawing = False
                    if button_color_black.button.collidepoint(event.pos):
                        self.color = 1

                    elif button_color_red.button.collidepoint(event.pos):
                        self.color = 2
                    elif button_color_blue.button.collidepoint(event.pos):
                        self.color = 3

                    elif button_color_eraser.button.collidepoint(event.pos):
                        self.color = 4
                    elif button_size_up.button.collidepoint(event.pos):
                        if self.radius < 15:
                            self.radius += 1
                    elif button_size_down.button.collidepoint(event.pos):
                        if self.radius > 3:
                            self.radius -= 1

                else:
                    # Mouse clicked down
                    self.drawing = True

                    # We are drawing and the first time we started it is last_pos and so it is also the last point we drew at
                    self.last_pos = event.pos

            # Left mouse button , stopped drawing
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.drawing = False


            elif event.type == pygame.MOUSEMOTION and self.drawing and not config_pallet.collidepoint(event.pos):

                # Ensure drawing only occurs within the window boundaries and not on the leave button
                if 0 < event.pos[0] < self.width and 0 < event.pos[1] < self.height and not leave.button.collidepoint(
                        event.pos):

                    if not line_intersects_rect(self.last_pos, event.pos, leave.button):
                        self.draw_smooth_line(self.last_pos, event.pos, self.radius, self.color)

                        Protocol.send_gen(self.key, [self.last_pos, event.pos, self.radius, self.color], self.socket,
                                          commands.line.value)

                        self.last_pos = event.pos
        # Ensure not drawing on leave button
        if self.drawing and self.last_pos and not leave.button.collidepoint(self.last_pos):
            if not line_intersects_rect(self.last_pos, self.last_pos, leave.button):
                self.draw_smooth_line(self.last_pos, self.last_pos, self.radius, self.color)
                Protocol.send_gen(self.key, [self.last_pos, self.last_pos, self.radius, self.color], self.socket,
                                  commands.line.value)

    # Thread that checks for incoming lines
    def check_updates(self):
        # If the canvas is active
        while self.active:
            line = 0
            if self.active:
                print("WAITING RECV...")
                # If there is information (bytes) then recv it
                line = Protocol.recv_gen(self.  key, self.socket)
                print("RECVS DA LINE")

            # If the given line from the server has atleast 4 letters, it is enough to extract the info we need to create a line
            if line  and len(
                    line) >= 4 and self.active:

                # Try so we wont crash the client
                try:

                    # Extraction of the info for a line
                    start_pos = cords.Cords(line[0])
                    print(start_pos)
                    end_pos = cords.Cords(line[1])
                    print(end_pos)
                    radius = int(line[2])
                    print(radius)
                    color = int(line[3])
                    # Send the line from the server to a function to draw the line on our own canvas
                    self.draw_smooth_line(start_pos.tup, end_pos.tup, radius, color)

                # If we couldn't for some reason compelte the line explain error
                except Exception as e:
                    print(f"Error drawing line from server: {e}")

            # Not to overload the system so to check with rest
            time.sleep(0.001)
        print("Finished the thread IM FULL IM FULL IM FULL")

    # The function works by getting the biggest diffrences x,y. and making it the line along
    # the points but instead of adding 1px at each we have a circle  so we for sure cover the
    # biggest axis diffrences and along the way becuase of the radius also the other axis
    def draw_smooth_line(self, start_pos, end_pos, radius, color):

        if color == 1:
            color = black
        elif color == 2:
            color = red
        elif color == 3:
            color = blue
        else:
            color = white
        # Finds the biggest diffrences between the 2 ponits
        distance = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))

        # If diffrence is too small or same point we just create the point once, further more to make sure we wont divide by zero
        if distance == 0:
            distance = 1

        # Split the whole distance to fractions so we can add at part of it a point
        for i in range(1, distance + 1):
            # Ratio to the whole distance
            fraction = i / distance

            # Takes the inital start_pos and adds the ratio amount of the whole distance
            x = int(start_pos[0] + fraction * (end_pos[0] - start_pos[0]))

            # Takes the inital start_pos and adds the ratio amount of the whole distance
            y = int(start_pos[1] + fraction * (end_pos[1] - start_pos[1]))

            # Create the point on the relative cords to the whole distance

            pygame.draw.circle(self.screen, color, (x, y),radius)

        pygame.display.update()
