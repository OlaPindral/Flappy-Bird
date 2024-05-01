import pygame
import os
import random

WIDTH = 500
HEIGHT = 800

def load_images():
    bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
                   pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
                   pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
    pipe_image = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
    base_image = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
    bg_image = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
    return bird_images, pipe_image, base_image, bg_image

BIRD_IMG, PIPE_IMG, BASE_IMG, BG_IMG = load_images()

class Bird:
    MAX_ROTATION = 25
    ROT_VOL = 20
    ANIMATION_TIME = 5
    GRAVITY = 1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.tilt = 0
        self.tick_count = 0
        self.height = self.y
        self.img_count = 0
        self.img = BIRD_IMG[0]
        self.started = False

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
        self.started = True

    def move(self):
        if self.started:
            self.tick_count += 1
            self.vel += self.GRAVITY
            d = self.vel + 0.5 * self.GRAVITY * self.tick_count
            if d >= 16:
                d = 16
            if d < 0:
                d -= 2

            self.y = self.y + d
            if d < 0 or self.y < self.height + 50:
                if self.tilt < self.MAX_ROTATION:
                    self.tilt = self.MAX_ROTATION
            else:
                if self.tilt > -90:
                    self.tilt -= self.ROT_VOL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = BIRD_IMG[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = BIRD_IMG[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = BIRD_IMG[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = BIRD_IMG[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = BIRD_IMG[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = BIRD_IMG[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

def draw_window(win, bird, pipes, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    bird.draw(win)
    text = pygame.font.SysFont("comicsans", 20).render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()

def handle_events(bird):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()
    return True

def main():
    pygame.init()
    bird = Bird(200, 200)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    run = True
    while run:
        run = handle_events(bird)
        bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            if pipe.collide(bird):
                run = False
                break
            if pipe.x < bird.x and not pipe.passed:
                pipe.passed = True
                add_pipe = True
        if add_pipe:
            score += 1
            pipes.append(Pipe(700))
        for r in rem:
            pipes.remove(r)
        if not 0 < bird.y < HEIGHT - bird.img.get_height():
            run = False
        draw_window(win, bird, pipes, score)
        clock.tick(30)
    font = pygame.font.SysFont("comicsans", 36)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    press_space_text = font.render("Press Space to Play Again", True, (255, 255, 255))
    win.blit(game_over_text, (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2 - game_over_text.get_height() / 2))
    win.blit(press_space_text, (WIDTH / 2 - press_space_text.get_width() / 2, HEIGHT / 2 + game_over_text.get_height()))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()

if __name__ == "__main__":
    main()