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
        if pressed_keys[self.keys['up']]:
            self.rect.move_ip(0, -5)
        elif pressed_keys[self.keys['down']]:
            self.rect.move_ip(0, 5)
        elif pressed_keys[self.keys['left']]:
            self.rect.move_ip(-5, 0)
        elif pressed_keys[self.keys['right']]:
            self.rect.move_ip(5, 0)

class CashThread(threading.Thread):
    def __init__(self, player1, player2, screen):
        super(CashThread, self).__init__()
        self.player1 = player1
        self.player2 = player2
        self.screen = screen
        self.cash = []
        self.running = True

    def generate_cash(self):
        # Cash position draw
        x = random.randint(0, 750)
        y = random.randint(0, 550)
        self.cash.append((x, y))

    def run(self):
        while self.running:

            # Cash generate
            self.generate_cash()
            time.sleep(5)  # Example delay for generated cash

    def stop(self):
        self.running = False

def main():
    pygame.init()

    # Window settings
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fast and Furious")

    # Colors
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)

    # Players
    player1 = Player("Player 1", red, 150, 500, {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT})
    player2 = Player("Player 2", blue, 600, 500, {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})

    # Thread for cash
    cash_thread = CashThread(player1, player2, screen)
    cash_thread.start()

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

        # drawing cash on the screen
        for cash in cash_thread.cash:
            pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(cash[0], cash[1], 10, 10))

        pygame.display.flip()
        clock.tick(60)

        # Stop cash thread
    cash_thread.stop()
    cash_thread.join()
    pygame.quit()

if __name__ == "__main__":
    main()