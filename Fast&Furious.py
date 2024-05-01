import pygame
import threading
import time
import random


# Main thread - road
class Road:
    def __init__(self):
        pygame.init()
        # Window settings
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fast and Furious")

        # State variables
        self.game_started = False  # Flag to track if the game has started
        self.start_button_rect = pygame.Rect(300, 250, 200, 100)  # Rectangle for the start button

        # Players
        self.player1 = Player("Player 1", 'Images/pomaranczowe.png', 600, 400, self.width, self.height,
                              {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT,
                               'right': pygame.K_RIGHT})
        self.player2 = Player("Player 2", 'Images/zielony.png', 150, 400, self.width, self.height,
                              {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})

        # Thread for cash and cars
        self.cash_thread = Cash()
        self.car_thread = CarThread(self.screen)
        self.cash_thread.start()
        self.car_thread.start()

        self.running = True
        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_started:
                # Check if the start button is clicked
                if self.start_button_rect.collidepoint(event.pos):
                    self.game_started = True

    def update_players(self, keys1, keys2):
        self.player1.move(keys1)
        self.player2.move(keys2)
        self.check_collisions()

    def check_collisions(self):
        # Calculate collision bounding boxes
        player1_rect = self.player1.image.get_rect(topleft=(self.player1.x, self.player1.y))
        player2_rect = self.player2.image.get_rect(topleft=(self.player2.x, self.player2.y))

        # Check for collision
        if player1_rect.colliderect(player2_rect):
            # Handle collision by moving players away from each other
            self.player1.x += 5
            self.player2.x -= 5

    def draw_start_screen(self):
        self.screen.fill((250, 227, 239))  #  background
        font = pygame.font.Font(None, 36)
        start_text = font.render("   Start", True, (255, 255, 255))
        start_button_color = (228, 70, 152) if self.start_button_rect.collidepoint(pygame.mouse.get_pos()) else (
        255, 105, 180)
        pygame.draw.rect(self.screen, start_button_color, self.start_button_rect, border_radius=10)
        self.screen.blit(start_text, (350, 290))

    def draw_game_screen(self):
        draw_background(self.screen, self.width, self.height)

        self.screen.blit(self.player1.image, (self.player1.x, self.player1.y))
        self.screen.blit(self.player2.image, (self.player2.x, self.player2.y))

        # drawing cash on the screen
        for cash in self.cash_thread.cash:
            pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(cash[0], cash[1], 20, 20))

        # drawing car on the screen
        for car in self.car_thread.cars:
            self.screen.blit(car.image, (car.x, car.y))
            car.move()

    def draw(self):
        if not self.game_started:
            self.draw_start_screen()
        else:
            self.draw_game_screen()

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        while self.running:
            self.handle_events()
            keys1 = pygame.key.get_pressed()
            keys2 = pygame.key.get_pressed()
            if self.game_started:
                self.update_players(keys1, keys2)
            self.draw()

        # Stop cash and car thread
        self.cash_thread.stop()
        self.car_thread.stop()
        self.cash_thread.join()
        self.car_thread.join()
        pygame.quit()


class Player:
    def __init__(self, name, image_path, x, y, width, height, keys):
        self.name = name
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 160))  # Przykładowa skala dla samochodu
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.keys = keys

    def check_boundaries(self):
        if self.x < 0:
            self.x = 0
        elif self.x > self.width - self.image.get_width():
            self.x = self.width - self.image.get_width()
        if self.y < 0:
            self.y = 0
        elif self.y > self.height - self.image.get_height():
            self.y = self.height - self.image.get_height()

    def move(self, pressed_keys):
        if pressed_keys[self.keys['up']]:
            self.y -= 5
        elif pressed_keys[self.keys['down']]:
            self.y += 5
        elif pressed_keys[self.keys['left']]:
            self.x -= 5
        elif pressed_keys[self.keys['right']]:
            self.x += 5

        self.check_boundaries()


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


class Cash(threading.Thread):
    def __init__(self):
        super(Cash, self).__init__()
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
            time.sleep(3)  # Example delay for generated cash

    def stop(self):
        self.running = False


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


def random_car_image():
    car_images = ['Images/pomaranczowe.png', 'Images/policja.png', 'Images/karetka.png', 'Images/taxi.png',
                  'Images/van.png', 'Images/zielony.png']
    return random.choice(car_images)


def draw_background(screen, width, height):
    # Background
    screen.fill((128, 128, 128))  # Grey background

    # Drawing stripes on the road
    lane_width = 10
    num_lanes = 10
    lane_color = (255, 255, 255)
    for i in range(num_lanes):
        lane_x = width // 2 - lane_width // 2
        lane_x += (i - num_lanes // 2) * (width // num_lanes)
        pygame.draw.rect(screen, lane_color, pygame.Rect(lane_x, 0, lane_width, height))


if __name__ == "__main__":
    road = Road()
    road.run()
