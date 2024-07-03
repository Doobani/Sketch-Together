import pygame


class Button:
    def __init__(self, x, y, width, height, color, text, screen):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.button = pygame.Rect(self.x, self.y, self.width, self.height)
        self.screen = screen

    def create_draw(self, size=0):
        if size != 0: #If no font was given in the parm defaults to 36, otherwise sets it as the size param
            self.font = pygame.font.Font(None, size)

        pygame.draw.rect(self.screen, self.color, self.button)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        self.screen.blit(text_surface, text_rect)

