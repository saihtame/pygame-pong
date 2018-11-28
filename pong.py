import pygame
import random


screen_size = screen_width, screen_height = 800, 550
score_size = 24

pong_size = pong_width, pong_height = 20, 60
pong_speed = 35

ball_size = ball_width, ball_height = 20, 20
ball_speed = 20
ball_speed_increment = 3


def main():
    # Initialization
    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont("arial", score_size)
    display = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()

    # Object creation.
    left_pong = Pong(pong_width, pong_height, screen_width * 0.05, -1)
    right_pong = Pong(pong_width, pong_height, screen_width * 0.95, 1)
    ball = Ball(ball_width, ball_height, ball_speed, (left_pong, right_pong))

    # Runtime
    running = True

    while running:
        tick = clock.tick() / 100

        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Score text rendering.
        left_score_text = font.render(str(ball.left_score), True, (255, 255, 255))
        right_score_text = font.render(str(ball.right_score), True, (255, 255, 255))

        # Game input and controls.
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_UP]:
            right_move = -pong_speed * tick
        elif keystate[pygame.K_DOWN]:
            right_move = pong_speed * tick
        else:
            right_move = 0

        if keystate[pygame.K_w]:
            left_move = -pong_speed * tick
        elif keystate[pygame.K_s]:
            left_move = pong_speed * tick
        else:
            left_move = 0

        if keystate[pygame.K_SPACE]:
            ball.speed = 2

        # Pong movement
        left_pong.move(left_move)
        right_pong.move(right_move)

        # Ball update
        ball.tick(tick)

        # Screen update.
        display.fill((0, 0, 0))

        left_pong.draw(display)
        right_pong.draw(display)
        ball.draw(display)

        display.blit(left_score_text, (screen_width * 0.05, screen_height * 0.05))
        display.blit(right_score_text, (screen_width * 0.95 - right_score_text.get_width(), screen_height * 0.05))

        pygame.display.update()


class Drawable:
    def __init__(self, width, height, x_position, y_position):
        self.width = width
        self.height = height
        self.x_position = x_position
        self.y_position = y_position

    def draw(self, display):
        pygame.draw.rect(display, (255, 255, 255), self.rect)

    def update_rect(self):
        self.rect = pygame.Rect(self.x_position, self.y_position, self.width, self.height)


class Pong(Drawable):
    def __init__(self, width, height, x_position, direction):
        super().__init__(width, height, x_position - width / 2, screen_height / 2 - height / 2)
        self.direction = direction
        self.update_rect()

    def move(self, length):
        new_pos = self.y_position + length

        if new_pos <= 0:
            self.y_position = 0
        elif new_pos >= screen_height - self.height:
            self.y_position = screen_height - self.height
        else:
            self.y_position = new_pos

        self.update_rect()


class Ball(Drawable):
    def __init__(self, width, height, speed, obstacles):
        super().__init__(width, height, 0, 0)
        self.speed = speed
        self.obstacles = obstacles
        self.left_score = 0
        self.right_score = 0
        self._bounce_cooldown = 0
        self.reset_position()
        self.update_rect()

    def reset_position(self):
        self.x_position = screen_width / 2 - self.width / 2
        self.y_position = screen_height / 2 - self.height / 2
        self.slope = random.uniform(-0.8, 0.8)
        self.direction = random.choice((-1, 1))

    def bounce(self, other):
        if self._bounce_cooldown <= 0:
            self.direction = other.direction * -1
            self.speed += ball_speed_increment

            if other.direction == -1:
                self.x_position = other.x_position + other.width
            else:
                self.x_position = other.x_position - self.width

            # Slope calculation
            self_center = self.y_position + self.height / 2
            other_center = other.y_position + other.height / 2

            if self_center <= other_center:
                self.slope = -((other_center - self_center) / (other.height / 2 + self.height / 2)) / 2
            else:
                self.slope = ((self_center - other_center) / (other.height / 2 + self.height / 2)) / 2

            self._bounce_cooldown = 1

    def tick(self, tick):
        # Movement
        self.x_position += ball_speed * self.direction * tick
        if self.x_position <= 0:
            self.right_score += 1
            return self.reset_position()
        elif self.x_position >= screen_width - self.width:
            self.left_score += 1
            return self.reset_position()

        self.y_position += self.speed * self.slope * tick
        if self.y_position <= 0:
            self.y_position = 0
            self.slope = -self.slope
        elif self.y_position >= screen_height - self.height:
            self.y_position = screen_height - self.height
            self.slope = -self.slope

        self.update_rect()
        self._bounce_cooldown += -tick

        # Collision detection
        for obs in self.obstacles:
            if obs.y_position + obs.height >= self.y_position >= obs.y_position - self.height:
                if obs.direction == 1:
                    if self.x_position + self.width >= obs.x_position and self.x_position <= obs.x_position + obs.width:
                        self.bounce(obs)
                    continue

                if self.x_position <= obs.x_position + obs.width and self.x_position + self.width >= obs.x_position:
                    self.bounce(obs)


if __name__ == "__main__":
    main()
