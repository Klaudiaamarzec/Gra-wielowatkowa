import pygame
import time
import random

class Player:
    def __init__(self, name, color, x, y, keys):
        self.name = name
        self.color = color
        self.rect = pygame.Rect(x, y, 50, 50)
        self.keys = keys

    def move(self, pressed_keys):
        if pressed_keys[self.keys['up']]:
            self.rect.move_ip(0, -5)
        elif pressed_keys[self.keys['down']]:
            self.rect.move_ip(0, 5)
        elif pressed_keys[self.keys['left']]:
            self.rect.move_ip(-5, 0)
        elif pressed_keys[self.keys['right']]:
            self.rect.move_ip(5, 0)

def main():
    pygame.init()

    # Window settings
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fireboy and Watergirl")

    # Colors
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)

    # Players
    player1 = Player("Player 1", red, 50, 50, {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT})
    player2 = Player("Player 2", blue, 700, 500, {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys1 = pygame.key.get_pressed()
        keys2 = pygame.key.get_pressed()
        player1.move(keys1)
        player2.move(keys2)

        screen.fill(white)
        pygame.draw.rect(screen, player1.color, player1.rect)
        pygame.draw.rect(screen, player2.color, player2.rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
