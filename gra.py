import pygame
import threading
import time
import random

class Player:
    def __init__(self, name, image_path, x, y, keys):
        self.name = name
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 160))  # Przykładowa skala dla samochodu
        self.x = x
        self.y = y
        self.keys = keys

    def move(self, pressed_keys):
        if pressed_keys[self.keys['up']]:
            #self.rect.move_ip(0, -5)
            self.y -= 5
        elif pressed_keys[self.keys['down']]:
            #self.rect.move_ip(0, 5)
            self.y += 5
        elif pressed_keys[self.keys['left']]:
            #self.rect.move_ip(-5, 0)
            self.x -= 5
        elif pressed_keys[self.keys['right']]:
            #self.rect.move_ip(5, 0)
            self.x += 5
class Car:
    def __init__(self, image_path, x, y, direction):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 160))
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = random.randint(1, 5)

    def move(self):
        if self.direction == "up":
            self.y -= self.speed
        else:
            self.y += self.speed



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
def random_car_image():
    car_images = ['Images/pomaranczowe.png', 'Images/policja.png', 'Images/karetka.png', 'Images/taxi.png', 'Images/van.png', 'Images/zielony.png']
    return random.choice(car_images)

class CarThread(threading.Thread):
    def __init__(self, screen):
        super(CarThread, self).__init__()
        self.screen = screen
        self.cars = []
        self.running = True

    def generate_cars(self):
        # Samochody na lewej połowie ekranu poruszają się tylko w dół
        x = random.randint(50, 375)
        y = random.randint(-160, -80)
        direction = "down"
        car = Car('Images/policja.png', x, y, direction)
        self.cars.append(car)

        # Samochody na prawej połowie ekranu poruszają się tylko w górę
        x = random.randint(425, 750)
        y = random.randint(600, 680)
        direction = "up"

        image_path = random_car_image()
        car = Car(image_path, x, y, direction)
        self.cars.append(car)

    def run(self):
        while self.running:
            self.generate_cars()
            time.sleep(random.uniform(1, 5))  # Losowy czas między generacją samochodów

    def stop(self):
        self.running = False


def draw_background(screen, width, height):
    # Rysowanie tła
    screen.fill((128, 128, 128))  # Szare tło

    # Rysowanie pasów na drodze
    lane_width = 10
    num_lanes = 10
    lane_color = (255, 255, 255)  # Biały kolor
    for i in range(num_lanes):
        lane_x = width // 2 - lane_width // 2
        lane_x += (i - num_lanes // 2) * (width // num_lanes)
        pygame.draw.rect(screen, lane_color, pygame.Rect(lane_x, 0, lane_width, height))


def main():
    pygame.init()

    # Window settings
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fast and Furious")

    # Players
    player1 = Player("Player 1", 'Images/pomaranczowe.png', 150, 400, {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT})
    player2 = Player("Player 2", 'Images/zielony.png', 600, 400, {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})

    # Thread for cash and cars
    cash_thread = CashThread(player1, player2, screen)
    car_thread = CarThread(screen)
    cash_thread.start()
    car_thread.start()

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

        # Sprawdzenie granic ekranu dla gracza 1
        if player1.x < 0:
            player1.x = 0
        elif player1.x > width - player1.image.get_width():
            player1.x = width - player1.image.get_width()
        if player1.y < 0:
            player1.y = 0
        elif player1.y > height - player1.image.get_height():
            player1.y = height - player1.image.get_height()

        # Sprawdzenie granic ekranu dla gracza 2
        if player2.x < 0:
            player2.x = 0
        elif player2.x > width - player2.image.get_width():
            player2.x = width - player2.image.get_width()
        if player2.y < 0:
            player2.y = 0
        elif player2.y > height - player2.image.get_height():
            player2.y = height - player2.image.get_height()

        draw_background(screen, width, height)
        screen.blit(player1.image, (player1.x, player1.y))
        screen.blit(player2.image, (player2.x, player2.y))

        # drawing cash on the screen
        for cash in cash_thread.cash:
            pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(cash[0], cash[1], 20, 20))

        # drawing car on the screen
        for car in car_thread.cars:
            screen.blit(car.image, (car.x, car.y))
            car.move()

        pygame.display.flip()
        clock.tick(60)

        # Stop cash and car thread
    cash_thread.stop()
    car_thread.stop()
    cash_thread.join()
    car_thread.join()
    pygame.quit()

if __name__ == "__main__":
    main()