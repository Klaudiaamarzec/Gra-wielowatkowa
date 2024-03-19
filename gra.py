import pygame
import threading
import time
import random

class Player:
    def __init__(self, name, color, x, y, keys):
        self.name = name
        self.color = color
        self.rect = pygame.Rect(x, y, 50, 50)
        self.keys = keys

    def move(self, pressed_keys):
        if self.keys['up'] in pressed_keys:
            self.rect.move_ip(0, -5)
        elif self.keys['down'] in pressed_keys:
            self.rect.move_ip(0, 5)
        elif self.keys['left'] in pressed_keys:
            self.rect.move_ip(-5, 0)
        elif self.keys['right'] in pressed_keys:
            self.rect.move_ip(5, 0)

def player_movement(player):
    while True:
        keys = pygame.key.get_pressed()
        player.move(keys)
        time.sleep(0.02)

def event_handler():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

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

    # Two threads for players movement
    movement_thread1 = threading.Thread(target=player_movement, args=(player1,))
    movement_thread2 = threading.Thread(target=player_movement, args=(player2,))
    movement_thread1.start()
    movement_thread2.start()

    # Third thread for event handler
    event_thread = threading.Thread(target=event_handler)
    event_thread.start()

    running = True
    clock = pygame.time.Clock()
    while running:
        screen.fill(white)
        pygame.draw.rect(screen, player1.color, player1.rect)
        pygame.draw.rect(screen, player2.color, player2.rect)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
