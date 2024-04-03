import pygame
import os
import random

screen_height = 800
screen_width = 500

pipe_frame = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
base_frame = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
bg_frame = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
bird_frames = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))), 
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))), 
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
font_score = pygame.font.SysFont('arial', 50)

class Bird:
    imgs = bird_frames
    max_rotation = 25
    rotation_speed = 20
    animation_time = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.frame_counter = 0
        self.frame = self.imgs[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        movement = 1.5 * (self.time**2) + self.speed * self.time

        if (movement > 16):
            movement = 16
        elif (movement < 0):
            movement -= 2
    
        self.y += movement

        if (movement < 0 or self.y < (self.height + 50)):
            if (self.angle < self.max_rotation):
                self.angle = self.max_rotation
            else:
                if (self.angle > -90):
                    self.angle -= self.rotation_speed

    def draw(self, screen):
        self.frame_counter += 1

        if (self.frame_counter < self.animation_time):
            self.frame = self.imgs[0]
        elif (self.frame_counter < self.animation_time*2):
            self.frame = self.imgs[1]
        elif (self.frame_counter < self.animation_time*3):
            self.frame = self.imgs[2]
        elif (self.frame_counter < self.animation_time*4):
            self.frame = self.imgs[1]
        elif (self.frame_counter >= self.animation_time*4 + 1):
            self.frame = self.imgs[0]
            self.frame_counter = 0

        if (self.angle <= -80):
            self.frame = self.imgs[1]
            self.frame_counter = self.animation_time*2

        rotated_image = pygame.transform.rotate(self.frame, self.angle)
        pos_center_frame = self.frame.get_rect(topleft=(self.x, self.y)).center
        box = rotated_image.get_rect(center=pos_center_frame)
        screen.blit(rotated_image, box.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.frame)

class Pipe:
    distance = 200
    speed = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.pos_top = 0
        self.pos_base = 0
        self.top_pipe = pygame.transform.flip(pipe_frame, False, True)
        self.base_pipe = pipe_frame
        self.passed = False
        self.define_height()
        
    def define_height(self):
        self.height = random.randrange(50, 450)
        self.pos_top = self.height - self.top_pipe.get_height()
        self.pos_base = self.height + self.distance

    def move(self):
        self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.top_pipe, (self.x, self.pos_top))
        screen.blit(self.base_pipe, (self.x, self.pos_base))

    def colision(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_pipe)
        base_mask = pygame.mask.from_surface(self.base_pipe)

        distance_top = (self.x - bird.x, self.pos_top - round(bird.y))
        distance_base = (self.x - bird.x, self.pos_base - round(bird.y))

        top_spot = bird_mask.overlap(top_mask, distance_top)
        base_spot = bird_mask.overlap(base_mask, distance_base)

        if (top_spot or base_spot):
            return True
        else:
            return False

class Base:
    speed = 5
    width = base_frame.get_width()
    frame = base_frame

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if (self.x1 + self.width < 0):
            self.x1 = self.x2 + self.width
        if (self.x2 + self.width < 0):
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        screen.blit(self.frame, (self.x1, self.y))
        screen.blit(self.frame, (self.x2, self.y))

def draw_screen(screen, birds, pipes, base, score):
    screen.blit(bg_frame, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = font_score.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(text, (screen_width - 10 - text.get_width(), 10))
    base.draw(screen)  # Corrigido para chamar o método draw com parênteses
    pygame.display.update()

def main():
    birds = [Bird(230, 350)]
    base = Base(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((screen_width, screen_height))
    score = 0
    timer = pygame.time.Clock()

    playing = True
    while playing:
        timer.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        for bird in birds:
            bird.move()
        
        base.move()  # Corrigido para chamar o método move com parênteses

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds): 
                if pipe.colision(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()  # Corrigido para chamar o método move com parênteses
            if pipe.x + pipe.top_pipe.get_width() < 0:
                remove_pipes.append(pipe)

        if (add_pipe):
            score += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)  # Corrigido para chamar o método remove na lista de pipes

        birds_to_remove = []
        for i, bird in enumerate(birds):
            if ((bird.y + bird.frame.get_height()) > base.y) or (bird.y < 0):
                birds_to_remove.append(i)
        for index in sorted(birds_to_remove, reverse=True):
            birds.pop(index)

        draw_screen(screen, birds, pipes, base, score)

if __name__ == "__main__":
    main()
