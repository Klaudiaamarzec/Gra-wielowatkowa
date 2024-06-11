"""
Fast and Furious - Racing game
"""
import sys
import time
import random
import threading
import pygame
import pygame.mixer

class Road:
    """
    Main game thread, manages game logic including displaying the start screen,
    event handling, player updates, and managing other threads.
    """

    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = 545, 800
        pygame.init()
        self.flowers = []
        self.cars = []
        self.cash = []
        pygame.display.set_caption("Fast and Furious")

        # Load crashing sound
        self.car_sound = pygame.mixer.Sound('audio/DrivingCar.wav')
        self.car_sound.play()

        # Players
        self.player1 = Player("Player 1", 'Images/pomaranczowe.png', 600, 400,
                              self.width, self.height,{'up': pygame.K_UP, 'down': pygame.K_DOWN,
                              'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, self.cars, self.cash)
        self.player2 = Player("Player 2", 'Images/zielony.png', 150, 400,
                              self.width, self.height,{'up': pygame.K_w, 'down': pygame.K_s,
                              'left': pygame.K_a, 'right': pygame.K_d}, self.cars, self.cash)

        # Threads for cash, cars and collisions
        self.cash_thread = CashThread(self.screen, self.cash)
        self.car_thread = CarThread(self.screen, self.cars)
        self.flower_thread = FlowerThread(self.screen, self.flowers)
        self.player_collision = PlayerCollision(self.player1, self.player2)
        self.collision_thread = Collision(self.cars)
        self.removecash_thread = RemoveCashThread(self.cash)

        # Start threads
        self.cash_thread.start()
        self.player_collision.start()
        self.car_thread.start()
        self.flower_thread.start()

        self.collision_thread.start()
        self.removecash_thread.start()

        self.running = True
        self.clock = pygame.time.Clock()

        # The amount of money collected by each player
        self.font = pygame.font.Font(None, 36)
        self.player1_text = self.font.render(f"COINS: {self.player2.cash_collected}", True, (255, 255, 0))
        self.player2_text = self.font.render(f"COINS: {self.player1.cash_collected}", True, (255, 255, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


    #Update the players positions based on keyboard
    def update_players(self, keys1, keys2):
        self.player1.move(keys1)
        self.player2.move(keys2)

    def update_cash_texts(self): #the amount of collected cash
        player1_new_text = f"COINS: {self.player2.cash_collected}"
        player2_new_text = f"COINS: {self.player1.cash_collected}"
        if self.player1_text != player1_new_text:
            self.player1_text = self.font.render(player1_new_text, True, (255, 255, 0))
        if self.player2_text != player2_new_text:
            self.player2_text = self.font.render(player2_new_text, True, (255, 255, 0))

    def draw_game_screen(self):
        draw_background(self.screen, self.width, self.height)

        self.screen.blit(self.player1.image, (self.player1.x, self.player1.y))
        self.screen.blit(self.player2.image, (self.player2.x, self.player2.y))

        # Drawing cash on the screen
        for cash in self.cash:
            self.screen.blit(cash.dollar_image, (cash.x, cash.y))

        # Drawing cars on the screen
        for car in self.cars:
            self.screen.blit(car.image, (car.x, car.y))
            car.move()

        # Drawing flowers on the screen
        for flower in self.flowers:
            self.screen.blit(flower.image, (flower.x, flower.y))
            flower.move()

        self.update_cash_texts()

        self.screen.blit(self.player1_text, (20, 20))
        self.screen.blit(self.player2_text, (self.width - self.player2_text.get_width() - 20, 20))

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        while self.running:
            self.handle_events()
            keys1 = pygame.key.get_pressed()
            keys2 = pygame.key.get_pressed()
            self.update_players(keys1, keys2)
            self.screen.fill((0, 0, 0))

            self.draw_game_screen()

            pygame.display.flip()
            self.clock.tick(60)

            if self.player1.game_over or self.player2.game_over:
                self.car_sound.stop()
                self.running = False
                self.stop_threads()
                pygame.quit()
                game_over(self.player1, self.player2, self.width, self.height)

        self.stop_threads()
        pygame.quit()

    #Stop all threads when game ends
    def stop_threads(self):

        self.cash_thread.stop()
        self.player_collision.stop()
        self.removecash_thread.stop()
        self.collision_thread.stop()
        self.car_thread.stop()
        self.flower_thread.stop()

        self.cash_thread.join()
        self.removecash_thread.join()
        self.player_collision.join()
        self.collision_thread.join()
        self.car_thread.join()
        self.flower_thread.join()


class Player:
    def __init__(self, name, image_path, x, y, width, height, keys, cars, cash):
        self.name = name
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 160))
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.keys = keys
        self.cars = cars
        self.cash = cash
        self.cash_collected = 0
        self.game_over = False

        # Load crashing sound
        self.crash_sound = pygame.mixer.Sound('audio/Crashing.wav')
        self.collision_margin = 20  # Margin to reduce the collision distance


    def check_boundaries(self):
        if self.x < 0:
            self.x = 0
        elif self.x > self.width - self.image.get_width():
            self.x = self.width - self.image.get_width()
        if self.y < 0:
            self.y = 0
        elif self.y > self.height - self.image.get_height():
            self.y = self.height - self.image.get_height()

    #Checks for collisions with other cars.
    def check_collisions(self):
        player_rect = self.image.get_rect(topleft=(self.x, self.y))

        for car in self.cars:
            car_rect = car.image.get_rect(topleft=(car.x, car.y)).inflate(-self.collision_margin, -self.collision_margin)
            if player_rect.colliderect(car_rect):
                self.game_over = True
                self.crash_sound.play()

    def check_cash_collected(self):
        player_rect = self.image.get_rect(topleft=(self.x, self.y))

        for cash in self.cash:
            cash_rect = cash.dollar_image.get_rect(topleft=(cash.x, cash.y))
            if player_rect.colliderect(cash_rect):
                cash.collected = True
                self.cash_collected += 1

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
    """
    Represents cash that players can collect.
    """
    def __init__(self, screen, x, y):
        super().__init__()
        self.screen = screen
        self.dollar_image = pygame.image.load("Images/dollar.png")
        self.dollar_image = pygame.transform.scale(self.dollar_image, (25, 25))
        self.x = x
        self.y = y
        self.collected = False


class RemoveCashThread(threading.Thread):
    def __init__(self, cash):
        super().__init__()
        self.cash = cash
        self.running = True

    #continuously check for collected cash and remove it from the game.
    def run(self):
        while self.running:
            for c in self.cash:
                if c.collected:
                    self.cash.remove(c)
                    break

    def stop(self):
        self.running = False


class CashThread(threading.Thread):
    """
        Thread to generate cash at random positions on the screen.
    """
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
            self.generate_cash()
            time.sleep(3)

    def stop(self):
        self.running = False

class Flower:
    def __init__(self, image_path, x, y,direction):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (5, 5))
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 0.5

    def move(self):
       # Moves the car based on its direction and speed.
            self.y -= self.speed

class FlowerThread(threading.Thread):
    """
            A thread to create random flowers on grass
        """
    def __init__(self, screen,flowers):
        super(FlowerThread, self).__init__()
        self.screen = screen
        self.flowers = flowers
        self.running = True

    def generate_flower(self):
        # flowers on the left
        x = random.randint(0, 4)
        y = random.randint(800, 850)
        direction = "down"
        flower = Flower('Images/policja.png', x, y, direction)
        self.flowers.append(flower)

        # flowers on the right
        x = random.randint(535, 545)
        y = random.randint(800, 850)
        direction = "up"

        image_path = random_flower()
        flower = Flower(image_path, x, y, direction)
        self.flowers.append(flower)

    def run(self):
        while self.running:
            self.generate_flower()
            time.sleep(random.uniform(1, 10))  # Random time between flower generation

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
       # Moves the car based on its direction and speed.

        if self.direction == "up":
            self.y -= self.speed
        else:
            self.y += self.speed


class CarThread(threading.Thread):
    """
        Thread to generate cars at random positions and manage car movements.
    """
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
            # Image inversion for cars moving downwards
            car_image = pygame.image.load(image_path)
            car_image = pygame.transform.flip(car_image, False, True)
            car.image = pygame.transform.scale(car_image, (80, 160))

        # Check collisions with existing cars
        with self.lock:
            for existing_car in self.cars:
                # Select new coordinates if the new car colidates with an existing one
                if self.check_collision(car, existing_car):
                    if direction == "down":
                        car.x = random.randint(5, 170)
                        car.y = random.randint(-200, -160)
                    else:
                        car.x = random.randint(245, 460)
                        car.y = random.randint(900, 980)

            self.cars.append(car)

    def run(self):
        while self.running:
            self.generate_car(random.randint(50, 200), random.randint(-200, -160), "down")
            self.generate_car(random.randint(320, 460), random.randint(850, 900), "up")
            time.sleep(random.uniform(5, 20))

    def stop(self):
        self.running = False


    #        Check if two cars collide with each other.
    def check_collision(self, car1, car2):

        car1_rect = pygame.Rect(car1.x, car1.y, car1.image.get_width(), car1.image.get_height())
        car2_rect = pygame.Rect(car2.x, car2.y, car2.image.get_width(), car2.image.get_height())
        return car1_rect.colliderect(car2_rect)


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

    if car1_rect.colliderect(car2_rect):
        # If cars are moving in opposite directions and car1 is faster than car2,
        # car1 passes car2
        if ((car1.direction == "down" and car2.direction == "up") or
                (car1.direction == "up" and car2.direction == "down")):
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

            direction = random.choice([True, False])
            if direction:
                # Check, if it can turn right
                if can_move_right(faster_car, cars, car_width):
                    faster_car.x += 5
                else:
                    # Slow down if there isn't enough space on the left side
                    faster_car.speed = slower_car.speed
            else:
                if can_move_left(faster_car, cars, car_width):
                    faster_car.x -= 5
                else:
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
            time.sleep(1)  # Check collisions once per 1 second

    def stop(self):
        self.running = False


class PlayerCollision(threading.Thread):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.running = True

    def check_collisions(self):
        player1_rect = self.player1.image.get_rect(topleft=(self.player1.x, self.player1.y))
        player2_rect = self.player2.image.get_rect(topleft=(self.player2.x, self.player2.y))

        if player1_rect.colliderect(player2_rect):
            # Handle collision by moving players away from each other
            self.player1.x += 5
            self.player2.x -= 5

    def run(self):
        while self.running:
            self.check_collisions()
            # time.sleep(0.1)  # Reduced sleep time


    def stop(self):
        self.running = False


class GameOverScreen:
    def __init__(self, width, height, player1_points, player2_points, winner=None):
        self.width = width
        self.height = height
        self.file_path = "results.txt"

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game Over")
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.restart_button_rect = pygame.Rect(170, 320, 200, 50)
        self.player1_points = player1_points
        self.player2_points = player2_points
        self.read_points_from_file()
        self.exit_button_rect = pygame.Rect(170, 600, 200, 50)
        self.winner = winner

    def read_points_from_file(self): #Read points from the results file.
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.player1_points += int(file.readline().strip())
                self.player2_points += int(file.readline().strip())
        except FileNotFoundError:
            pass

    #Writes points to the results file and exit the game.
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

        player1_points_text = self.font.render(f"Orange Player Points: {self.player1_points}", True, (0, 0, 255))
        player2_points_text = self.font.render(f"Green Player Points: {self.player2_points}", True, (0, 0, 255))

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
            winner_text = self.big_font.render(f"{self.winner} Player won!", True, (0, 255, 0))
            winner_text_rect = winner_text.get_rect(center=(self.width // 2, 200))
            self.screen.blit(winner_text, winner_text_rect)

        pygame.draw.rect(self.screen, (255, 0, 0), self.exit_button_rect)
        exit_text = self.font.render("Finish game", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.restart_button_rect.collidepoint(event.pos):
                    return True
                if self.exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        return False


def random_car_image(): #random car from images.
    car_images = ['Images/pomaranczowe.png', 'Images/policja.png', 'Images/karetka.png', 'Images/taxi.png',
                  'Images/van.png', 'Images/zielony.png']
    return random.choice(car_images)

def random_flower():
    flower_image=['Images/grass/f_pom.png','Images/grass/f_fiolet.png']
    return random.choice(flower_image)

def draw_background(screen, width, height):
    # Background
    screen.fill((128, 128, 128))

    # Drawing grass next to the road
    grass_width = 7
    grass_color = (50, 128, 0)
    pygame.draw.rect(screen, grass_color, pygame.Rect(0, 0, grass_width, height))
    pygame.draw.rect(screen, grass_color, pygame.Rect(width - grass_width, 0, grass_width, height))

    # Drawing stripes on the road
    lane_width = 5
    num_lanes = 10
    lane_color = (255, 255, 255)
    dash_length = 20  # Length of each dash
    gap_length = 10  # Length of gap between dashes

    # Draw lanes
    for i in range(num_lanes):
        if i == num_lanes // 2:
            # Draw solid line in the middle
            middle_lane_x = screen.get_width() // 2 - lane_width // 2
            middle_lane_y = 0
            middle_lane_height = screen.get_height()
            pygame.draw.rect(screen, lane_color,
                             pygame.Rect(middle_lane_x, middle_lane_y, lane_width, middle_lane_height))
            # Draw dashed lines on the sides
            lane_y = screen.get_height() // 2 - lane_width // 2
            lane_y += (i - num_lanes // 2) * (screen.get_height() // num_lanes)
            num_dashes = screen.get_width() // (dash_length + gap_length)
            for j in range(1,num_dashes):
                dash_x = j * (dash_length + gap_length)
                if j % 3 == 0:  # Draw dashes only on even iterations
                    pygame.draw.rect(screen, lane_color, pygame.Rect(dash_x, lane_y, lane_width, dash_length))

        else:
            # Draw dashed lines on the sides
            lane_y = screen.get_height() // 2 - lane_width // 2
            lane_y += (i - num_lanes // 2) * (screen.get_height() // num_lanes)
            num_dashes = screen.get_width() // (dash_length + gap_length)
            for j in range(1,num_dashes):
                dash_x = j * (dash_length + gap_length)
                if j % 3 == 0:  # Draw dashes only on even iterations
                    pygame.draw.rect(screen, lane_color, pygame.Rect(dash_x, lane_y, lane_width, dash_length))


def draw_start_screen(screen):
    screen.fill((250, 227, 239))
    button_width, button_height = 200, 100
    button_x = (screen.get_width() - button_width) // 2
    button_y = (screen.get_height() - button_height) // 2
    start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    font = pygame.font.Font(None, 36)
    start_text = font.render("START", True, (255, 255, 255))
    start_button_color = (228, 70, 152) if start_button_rect.collidepoint(pygame.mouse.get_pos()) else (255, 105, 180)
    pygame.draw.rect(screen, start_button_color, start_button_rect, border_radius=10)
    text_x = button_x + (button_width - start_text.get_width()) // 2
    text_y = button_y + (button_height - start_text.get_height()) // 2
    screen.blit(start_text, (text_x, text_y))
    pygame.display.flip()


def game_over(player1, player2, width, height):
    winner = None
    if player1.game_over:
        winner ="Green"
    if player2.game_over:
        winner = "Orange"

    game_over_screen = GameOverScreen(width, height, player1.cash_collected, player2.cash_collected, winner)

    while True:
        if game_over_screen.handle_events():
            restart_game(width, height)
            break
        game_over_screen.display_game_over()
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    game_over_screen.write_points_to_file()


def restart_game(width, height):
    pygame.quit()
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    road = Road(screen)
    road.run()


def main():

    pygame.init()


    width, height = 545, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Start Screen")

    clock = pygame.time.Clock()
    start_screen_active = True

    while start_screen_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_pos = pygame.mouse.get_pos()
                    if pygame.Rect(175, 350, 200, 100).collidepoint(mouse_pos):
                        start_screen_active = False

        draw_start_screen(screen)
        clock.tick(30)

    road = Road(screen)
    road.run()


if __name__ == "__main__":
    main()
