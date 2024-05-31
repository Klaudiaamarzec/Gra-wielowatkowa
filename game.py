"""
Fast and Furious - Gra wyścigowa
"""
import sys
import time
import random
import threading
import pygame

class Road:
    """
    Główny wątek gry, zarządza logiką gry, włączając w to wyświetlanie ekranu startowego,
     obsługę zdarzeń, aktualizację graczy oraz zarządzanie innymi wątkami.
    """
    def draw(self):
        """
        Metoda rysuje ekran gry.
        Jeśli gra nie została jeszcze rozpoczęta, rysuje ekran startowy.
        W przeciwnym razie rysuje ekran gry.
        """
        if not self.game_started:
            draw_start_screen(self.screen, self.start_button_rect)
        else:
            self.draw_game_screen()

        pygame.display.flip()
        self.clock.tick(60)

    def __init__(self):
        pygame.init()
        self.cars = []
        self.cash = []
        # Window settings
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fast and Furious")

        # State variables
        self.start_button_rect = pygame.Rect(300, 250, 200, 100) #Rectangle for the start button
        self.game_started = False  # Flag to track if the game has started

        # Players
        self.player1 = Player("Player 1", 'Images/pomaranczowe.png', 600, 400, self.width, self.height,
                              {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT,
                               'right': pygame.K_RIGHT}, self.cars, self.cash)
        self.player2 = Player("Player 2", 'Images/zielony.png', 150, 400, self.width, self.height,
                              {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d},
                              self.cars, self.cash)

        # Thread for cash, cars and collisions
        self.cash_thread = CashThread(self.screen, self.cash)
        self.car_thread = CarThread(self.screen, self.cars)
        self.player_collision = PlayerCollision(self.player1, self.player2)
        self.collision_thread = Collision(self.cars)
        self.removecash_thread = RemoveCashThread(self.cash)

        self.cash_thread.start()
        self.car_thread.start()
        self.player_collision.start()
        self.collision_thread.start()
        self.removecash_thread.start()

        self.running = True
        self.clock = pygame.time.Clock()

    def handle_events(self):
        """
        Metoda obsługuje zdarzenia, takie jak naciśnięcie klawiszy lub zamknięcie okna.
        """
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
        for cash in self.cash:
            self.screen.blit(cash.dollar_image, (cash.x, cash.y))

        # drawing car on the screen
        for car in self.cars:
            self.screen.blit(car.image, (car.x, car.y))
            car.move()

        # Wyświetl ilość zebranych pieniędzy dla każdego gracza
        font = pygame.font.Font(None, 36)
        player1_text = font.render(f"COINS: {self.player2.cash_collected}", True, (255, 255, 0))
        player2_text = font.render(f"COINS: {self.player1.cash_collected}", True, (255, 255, 0))
        self.screen.blit(player1_text, (20, 20))
        self.screen.blit(player2_text, (self.width - player2_text.get_width() - 20, 20))

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        while self.running:
            self.handle_events()
            keys1 = pygame.key.get_pressed()
            keys2 = pygame.key.get_pressed()
            # if self.game_started:
            self.update_players(keys1, keys2)
            self.screen.fill((0, 0, 0))

            self.draw_game_screen()

            pygame.display.flip()
            self.clock.tick(60)

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
        self.removecash_thread.stop()

        self.cash_thread.join()
        self.car_thread.join()
        self.player_collision.join()
        self.collision_thread.join()
        self.removecash_thread.join()

    def game_over(self):
        winner = None
        if self.player1.game_over:
            winner ="Player 2"
        if self.player2.game_over:
            winner = "Player 1"
        game_over_screen = GameOverScreen(self.width, self.height, self.player1.cash_collected,self.player2.cash_collected, winner)

        while True:
            if game_over_screen.handle_events():
                self.restart_game()
                break
            game_over_screen.display_game_over()
            pygame.display.flip()
            self.clock.tick(60)

        game_over_screen.write_points_to_file()

    def restart_game(self):
        # Przywróć wszystkie ustawienia do stanu początkowego
        new_instance = type(self)()
        new_instance.run()


class Player:
    def __init__(self, name, image_path, x, y, width, height, keys, cars, cash):
        self.name = name
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 160))  #Przykładowa skala dla samochodu
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.keys = keys
        self.cars = cars
        self.cash = cash
        self.cash_collected = 0
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

    def check_collisions(self):
        player_rect = self.image.get_rect(topleft=(self.x, self.y))

        for car in self.cars:
            car_rect = car.image.get_rect(topleft=(car.x, car.y))
            if player_rect.colliderect(car_rect):
                # Game over for this player
                self.game_over = True

    def check_cash_collected(self):
        player_rect = self.image.get_rect(topleft=(self.x, self.y))

        for cash in self.cash:
            cash_rect = cash.dollar_image.get_rect(topleft=(cash.x, cash.y))
            if player_rect.colliderect(cash_rect):
                cash.collected = True
                self.cash_collected += 1
                print("Player ", self.name, "has collected: ", self.cash_collected, " coins")

    def move(self, pressed_keys):
        if pressed_keys[self.keys['up']]:
            self.y -= 5
        elif pressed_keys[self.keys['down']]:
            self.y += 5
        elif pressed_keys[self.keys['left']]:
            self.x -= 5
        elif pressed_keys[self.keys['right']]:
            self.x += 5

        self.check_collisions()
        self.check_cash_collected()
        self.check_boundaries()


class Cash:
    def __init__(self, screen, x, y):
        super().__init__()
        self.screen = screen
        self.dollar_image = pygame.image.load("Images/dollar.png")
        self.dollar_image = pygame.transform.scale(self.dollar_image, (25, 25))  # Dostosuj rozmiar obrazka
        self.x = x
        self.y = y
        self.collected = False


class RemoveCashThread(threading.Thread):
    def __init__(self, cash):
        super().__init__()
        self.cash = cash
        self.running = True

    def run(self):
        while self.running:
            for c in self.cash:
                if c.collected:
                    self.cash.remove(c)
                    break

    def stop(self):
        self.running = False


class CashThread(threading.Thread):
    def __init__(self, screen, cash):
        super().__init__()
        self.cash = cash
        self.screen = screen
        self.running = True
        self.lock = threading.Lock()  # Mutex

    def generate_cash(self):
        # Cash position draw
        x = random.randint(0, 750)
        y = random.randint(0, 550)
        with self.lock:
            cash = Cash(self.screen, x, y)
            self.cash.append(cash)

    def run(self):
        while self.running:
            # Cash generate
            self.generate_cash()
            time.sleep(3)  # Example delay for generated cash

    def stop(self):
        self.running = False


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


class CarThread(threading.Thread):
    def __init__(self, screen, cars):
        super().__init__()
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

    def run(self):
        while self.running:
            self.generate_car(random.randint(50, 375), random.randint(-160, -80), "down")
            self.generate_car(random.randint(375, 750), random.randint(600, 700), "up")
            time.sleep(random.uniform(5, 10))  # Losowy czas między generacją samochodów 5 10

    def stop(self):
        self.running = False

    def check_collision(self, car1, car2):
        # Sprawdź, czy dwie samochody kolidują ze sobą
        # distance = ((car1.x - car2.x) ** 2 + (car1.y - car2.y) ** 2) ** 0.5
        # if distance < 50:  # Jeśli odległość jest mniejsza niż 100 pikseli, kolidują
        #     return True
        # else:
        #     return False
        car1_rect = pygame.Rect(car1.x, car1.y, car1.image.get_width(), car1.image.get_height())
        car2_rect = pygame.Rect(car2.x, car2.y, car2.image.get_width(), car2.image.get_height())
        return car1_rect.colliderect(car2_rect)


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


# Check if there's enough space on the left side
def can_move_left(faster_car, cars, car_width):
    for car in cars:
        if car != faster_car and pygame.Rect(car.x, car.y, car.image.get_width(),
                                             car.image.get_height()).colliderect(
                pygame.Rect(faster_car.x - 5, faster_car.y, car_width,
                            faster_car.image.get_height())):
            return False
    return True


def can_move_right(faster_car, cars, car_width):
    for car in cars:
        if car != faster_car and pygame.Rect(car.x, car.y, car.image.get_width(), car.image.get_height()).colliderect(
                pygame.Rect(faster_car.x + 5, faster_car.y, car_width, faster_car.image.get_height())):
            return False
    return True


def check_collisions(car1, car2, cars):
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

            faster_car.speed = slower_car.speed
            car_width = faster_car.image.get_width()

            # Random direction
            direction = random.choice([True, False])
            if direction:
                # Sprawdź czy można skręcić w prawo
                if can_move_right(faster_car, cars, car_width):
                    faster_car.x += 5
                else:
                    # Jeśli nie ma wystarczająco miejsca po lewej, zwolnij
                    faster_car.speed = slower_car.speed
            else:
                # Sprawdź czy można skręcić w lewo
                if can_move_left(faster_car, cars, car_width):
                    faster_car.x -= 5
                else:
                    # Jeśli nie ma wystarczająco miejsca po lewej, zwolnij
                    faster_car.speed = slower_car.speed


class Collision(threading.Thread):
    def __init__(self, cars):
        super().__init__()
        self.cars = cars
        self.running = True

    def run(self):
        while self.running:
            for car1 in self.cars:
                for car2 in self.cars:
                    if car1 != car2:
                        check_collisions(car1, car2, self.cars)
            # time.sleep(0.1)  # Sprawdź kolizje co 0.1 sekundy

    def stop(self):
        self.running = False


class GameOverScreen:
    def __init__(self, width, height, player1_points, player2_points, winner=None):
        self.width = width
        self.height = height
        self.file_path = "baza.txt"

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game Over")
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.restart_button_rect = pygame.Rect(300, 320, 200, 50)
        self.player1_points = player1_points
        self.player2_points = player2_points
        self.read_points_from_file()
        self.exit_button_rect = pygame.Rect(300, 500, 200, 50)
        self.winner = winner


    def read_points_from_file(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.player1_points += int(file.readline().strip())
                self.player2_points += int(file.readline().strip())
        except FileNotFoundError:
            pass

    def write_points_to_file(self):
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(str(self.player1_points) + "\n")
            file.write(str(self.player2_points) + "\n")
        sys.exit()

    def display_game_over(self):
        self.screen.fill((250, 227, 239))

        game_over_text = self.big_font.render("GAME OVER!", True, (255, 0, 0))
        game_over_text_rect = game_over_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(game_over_text, game_over_text_rect)

        player1_points_text = self.font.render(f"Player 1 Points: {self.player1_points}", True, (0, 0, 255))
        player2_points_text = self.font.render(f"Player 2 Points: {self.player2_points}", True, (0, 0, 255))

        player_points_x = self.width // 2 - player1_points_text.get_width() // 2
        player1_points_y = 400
        player2_points_y = 440

        self.screen.blit(player1_points_text, (player_points_x, player1_points_y))
        self.screen.blit(player2_points_text, (player_points_x, player2_points_y))

        pygame.draw.rect(self.screen, (0, 255, 0), self.restart_button_rect)
        restart_text = self.font.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        if self.winner:
            winner_text = self.big_font.render(f"Gracz {self.winner} wygrał!", True, (0, 255, 0))
            winner_text_rect = winner_text.get_rect(center=(self.width // 2, 200))
            self.screen.blit(winner_text, winner_text_rect)

        pygame.draw.rect(self.screen, (255, 0, 0), self.exit_button_rect)
        exit_text = self.font.render("Zakończ grę", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

        pygame.display.flip()

    def handle_events(self):
        # Obsługa zdarzeń myszy
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button_rect.collidepoint(event.pos):
                    return True
                if self.exit_button_rect.collidepoint(event.pos):  # Obsługa przycisku "Zakończ grę"
                    pygame.quit()
                    sys.exit()
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
    pygame.display.flip()  # Dodajemy to wywołanie, aby zaktualizować widoczny obraz



if __name__ == "__main__":
    road = Road()
    road.run()
