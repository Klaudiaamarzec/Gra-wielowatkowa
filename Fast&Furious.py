import pygame
import threading
import time
import random


# Main thread - road
class Road:
    def __init__(self):
        pygame.init()
        self.cars = []
        # Window settings
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fast and Furious")

        # State variables
        self.start_button_rect = pygame.Rect(300, 250, 200, 100)  # Rectangle for the start button
        self.game_started = False  # Flag to track if the game has started

        # Players
        self.player1 = Player("Player 1", 'Images/pomaranczowe.png', 600, 400, self.width, self.height,
                              {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT,
                               'right': pygame.K_RIGHT})
        self.player2 = Player("Player 2", 'Images/zielony.png', 150, 400, self.width, self.height,
                              {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})

        # Thread for cash, cars and collisions
        self.cash_thread = Cash()
        self.car_thread = CarThread(self.screen, self.cars)
        self.player_collision = PlayerCollision(self.player1, self.player2)
        self.collision_thread = Collision(self.cars)
        self.player1_collision = GameOverCollision(self.player1, self.cars)
        self.player2_collision = GameOverCollision(self.player2, self.cars)
        self.cash_thread.start()
        self.car_thread.start()
        self.player_collision.start()
        self.collision_thread.start()
        self.player1_collision.start()
        self.player2_collision.start()

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

    def draw_game_screen(self):
        draw_background(self.screen, self.width, self.height)

        self.screen.blit(self.player1.image, (self.player1.x, self.player1.y))
        self.screen.blit(self.player2.image, (self.player2.x, self.player2.y))

        # drawing cash on the screen
        for cash in self.cash_thread.cash:
            pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(cash[0], cash[1], 20, 20))

        # drawing car on the screen
        for car in self.cars:
            self.screen.blit(car.image, (car.x, car.y))
            car.move()

        pygame.display.flip()
        self.clock.tick(60)

    def draw(self):
        if not self.game_started:
            draw_start_screen(self.screen, self.start_button_rect)
        else:
            self.draw_game_screen()

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        while self.running:
            self.handle_events()
            keys1 = pygame.key.get_pressed()
            keys2 = pygame.key.get_pressed()
            # if self.game_started:
            self.update_players(keys1, keys2)
            self.draw_game_screen()

            if self.player1.game_over or self.player2.game_over:
                self.running = False
                self.game_over()

        self.stop_threads()
        pygame.quit()

    def stop_threads(self):
        self.cash_thread.stop()
        self.car_thread.stop()
        self.player_collision.stop()
        self.collision_thread.stop()
        self.player1_collision.stop()
        self.player2_collision.stop()
        self.cash_thread.join()
        self.car_thread.join()
        self.player_collision.join()
        self.collision_thread.join()
        self.player1_collision.join()
        self.player2_collision.join()

    def game_over(self):
        game_over_screen = GameOverScreen(self.width, self.height)
        while True:
            if game_over_screen.handle_events():
                self.restart_game()
                break
            game_over_screen.display_game_over()
            pygame.display.flip()
            self.clock.tick(60)

    def restart_game(self):
        # Przywróć wszystkie ustawienia do stanu początkowego
        self.__init__()
        self.run()


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
        self.game_over = False

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
        self.speed = random.randint(1, 3)

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
    def __init__(self, screen, cars):
        super(CarThread, self).__init__()
        self.screen = screen
        self.cars = cars

        self.running = True
        self.lock = threading.Lock()  # Mutex

    def generate_car(self, x, y, direction):

        image_path = random_car_image()
        car = Car(image_path, x, y, direction)

        if direction == "down":
            # Odwrócenie obrazu dla samochodów poruszających się w dół
            car_image = pygame.image.load(image_path)
            car_image = pygame.transform.flip(car_image, False, True)
            car.image = pygame.transform.scale(car_image, (80, 160))

        # Sprawdź kolizje z istniejącymi samochodami
        with self.lock:
            for existing_car in self.cars:
                # Jeśli nowo tworzony samochód koliduje z istniejącym, wybierz nowe współrzędne
                if self.check_collision(car, existing_car):
                    if direction == "down":
                        car.x = random.randint(50, 375)
                        car.y = random.randint(-160, -80)
                    else:
                        car.x = random.randint(425, 750)
                        car.y = random.randint(600, 680)

            # Dodaj nowy samochód do listy
            self.cars.append(car)

    def generate_cars(self):
        # Samochody na lewej połowie ekranu poruszają się tylko w dół
        x = random.randint(50, 375)
        y = random.randint(-160, -80)
        direction = "down"

        self.generate_car(x, y, direction)

        # Samochody na prawej połowie ekranu poruszają się tylko w górę
        x = random.randint(425, 750)
        y = random.randint(600, 680)
        direction = "up"

        self.generate_car(x, y, direction)

    def run(self):
        while self.running:
            self.generate_cars()
            time.sleep(random.uniform(5, 10))  # Losowy czas między generacją samochodów

    def stop(self):
        self.running = False

    def check_collision(self, car1, car2):
        # Sprawdź, czy dwie samochody kolidują ze sobą
        distance = ((car1.x - car2.x) ** 2 + (car1.y - car2.y) ** 2) ** 0.5
        if distance < 100:  # Jeśli odległość jest mniejsza niż 100 pikseli, kolidują
            return True
        else:
            return False


class PlayerCollision(threading.Thread):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.running = True

    def check_collisions(self):
        # Calculate collision bounding boxes
        player1_rect = self.player1.image.get_rect(topleft=(self.player1.x, self.player1.y))
        player2_rect = self.player2.image.get_rect(topleft=(self.player2.x, self.player2.y))

        # Check for collision
        if player1_rect.colliderect(player2_rect):
            # Handle collision by moving players away from each other
            self.player1.x += 5
            self.player2.x -= 5

    def run(self):
        while self.running:
            self.check_collisions()

    def stop(self):
        self.running = False


def check_collisions(car1, car2):
    # Calculate collision bounding boxes
    car1_rect = car1.image.get_rect(topleft=(car1.x, car1.y))
    car2_rect = car2.image.get_rect(topleft=(car2.x, car2.y))

    # Check for collision
    if car1_rect.colliderect(car2_rect):
        # If cars are moving in opposite directions and car1 is faster than car2,
        # car1 passes car2
        if ((car1.direction == "down" and car2.direction == "up") or
                (car1.direction == "up" and car2.direction == "down")):
            # Check if car1 is to the left of car2
            if car1.x < car2.x:
                # Car1 is to the left, so it passes car2 to the right
                # Handle collision by moving cars to the right
                car1.x -= 2
                car2.x += 2
            else:
                # Car1 is to the right, so it passes car2 to the left
                # Handle collision by moving cars to the left
                car1.x += 2
                car2.x -= 2
        else:
            if car1.speed > car2.speed:
                faster_car = car1
                slower_car = car2
            else:
                faster_car = car2
                slower_car = car1

            # Random direction
            direction = random.choice([True, False])
            if direction:
                # Sprawdź czy można skręcić w lewo
                if faster_car.x > 5:  # Upewnij się, że jest wystarczająco miejsca po lewej stronie
                    faster_car.x += 5
                else:
                    # Jeśli nie ma wystarczająco miejsca po lewej, zwolnij
                    faster_car.speed = slower_car.speed
            else:
                # Sprawdź czy można skręcić w lewo
                if faster_car.x > 5:  # Upewnij się, że jest wystarczająco miejsca po lewej stronie
                    faster_car.x -= 5
                else:
                    # Jeśli nie ma wystarczająco miejsca po lewej, zwolnij
                    faster_car.speed = slower_car.speed


class Collision(threading.Thread):
    def __init__(self, cars):
        super(Collision, self).__init__()
        self.cars = cars
        self.running = True

    def run(self):
        while self.running:
            for car1 in self.cars:
                for car2 in self.cars:
                    if car1 != car2:
                        check_collisions(car1, car2)
            # time.sleep(0.1)  # Sprawdź kolizje co 0.1 sekundy

    def stop(self):
        self.running = False


class GameOverCollision(threading.Thread):
    def __init__(self, player, cars):
        super().__init__()
        self.player = player
        self.cars = cars
        self.running = True

    def check_collisions(self):
        player_rect = self.player.image.get_rect(topleft=(self.player.x, self.player.y))

        for car in self.cars:
            car_rect = car.image.get_rect(topleft=(car.x, car.y))
            if player_rect.colliderect(car_rect):
                # Game over for this player
                self.player.game_over = True

    def run(self):
        while self.running:
            self.check_collisions()
            # time.sleep(0.1)    # Opóźnienie, żeby nie obciążać procesora

    def stop(self):
        self.running = False


class GameOverScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game Over")
        self.font = pygame.font.Font(None, 36)
        self.restart_button_rect = pygame.Rect(300, 250, 200, 100)

    def display_game_over(self):
        self.screen.fill((250, 227, 239))  # background
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (300, 200))

        # Draw restart button
        pygame.draw.rect(self.screen, (0, 255, 0), self.restart_button_rect)
        restart_text = self.font.render("Restart", True, (255, 255, 255))
        self.screen.blit(restart_text, (350, 290))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button_rect.collidepoint(event.pos):
                    return True
        return False


# def game_over():
#     pygame.init()
#     game_over_screen = GameOverScreen(800, 600)
#     running = True
#     while running:
#         game_over_screen.display_game_over()
#         if game_over_screen.handle_events():
#             running = False


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


def draw_start_screen(screen, button):
    screen.fill((250, 227, 239))  # background
    font = pygame.font.Font(None, 36)
    start_text = font.render("   Start", True, (255, 255, 255))
    start_button_color = (228, 70, 152) if button.collidepoint(pygame.mouse.get_pos()) else (
        255, 105, 180)
    pygame.draw.rect(screen, start_button_color, button, border_radius=10)
    screen.blit(start_text, (350, 290))


if __name__ == "__main__":
    road = Road()
    road.run()
