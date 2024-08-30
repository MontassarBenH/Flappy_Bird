import pygame
import random
import math
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
LIGHT_RED = (255, 102, 102)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
PINK = (255, 192, 203)




# Game Variables
gravity = 0.3
bird_movement = 0
game_active = False
start_screen = True
score = 0
high_score = 0
high_score_name = ""

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Fish')

# Game Font
game_font = pygame.font.Font('freesansbold.ttf', 32)
small_font = pygame.font.Font('freesansbold.ttf', 24)
title_font = pygame.font.Font('freesansbold.ttf', 48)

# fish dimensions and starting position
#bird_rect = pygame.Rect(100, SCREEN_HEIGHT // 2, 40, 30)
fish_rect = pygame.Rect(100, SCREEN_HEIGHT // 2, 60, 40)

# Load background image
background = pygame.image.load('background.jpg').convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Pipe variables
pipe_width = 60
pipe_gap = 200
pipe_list = []
pipe_height = [200, 300, 400]

# Create a custom event for spawning pipes
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)

# Cloud class
class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(10, 100)
        self.y = random.randint(50, 200)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(30, 60)

    def move(self):
        self.x -= self.speed
        if self.x < -self.size:
            self.x = SCREEN_WIDTH + random.randint(10, 100)
            self.y = random.randint(50, 200)

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.size, self.size // 2))
        pygame.draw.ellipse(screen, WHITE, (self.x + self.size // 4, self.y - self.size // 4, self.size // 2, self.size // 2))

# Create cloud list
clouds = [Cloud() for _ in range(5)]

def draw_ground():
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    for i in range(0, SCREEN_WIDTH, 30):
        pygame.draw.line(screen, BLACK, (i, SCREEN_HEIGHT - GROUND_HEIGHT), (i + 15, SCREEN_HEIGHT - GROUND_HEIGHT + 15), 2)

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pygame.Rect(SCREEN_WIDTH, random_pipe_pos, pipe_width, SCREEN_HEIGHT - random_pipe_pos)
    top_pipe = pygame.Rect(SCREEN_WIDTH, 0, pipe_width, random_pipe_pos - pipe_gap)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return [pipe for pipe in pipes if pipe.right > -50]

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            pygame.draw.rect(screen, GREEN, pipe)
            pygame.draw.rect(screen, BLACK, pipe, 3)
            pygame.draw.rect(screen, (0, 150, 0), (pipe.left, pipe.top, pipe_width, 30))
        else:
            pygame.draw.rect(screen, GREEN, pipe)
            pygame.draw.rect(screen, BLACK, pipe, 3)
            pygame.draw.rect(screen, (0, 150, 0), (pipe.left, pipe.bottom - 30, pipe_width, 30))


def draw_flying_fish(screen, x, y, time):
    # Colors
    BODY_COLOR = (100, 149, 237)  
    WING_COLOR = (173, 216, 230)  
    EYE_COLOR = (0, 0, 0)  

    # Body
    body_rect = pygame.Rect(x, y, 80, 40)
    pygame.draw.ellipse(screen, BODY_COLOR, body_rect)

    # Wings
    wing_angle = math.sin(time * 0.1) * 30  
    wing_points = [
        (x + 20, y + 20),
        (x - 20, y - 20),
        (x + 20, y - 20)
    ]
    rotated_wing = pygame.transform.rotate(
        pygame.Surface((40, 40), pygame.SRCALPHA),
        wing_angle
    )
    pygame.draw.polygon(rotated_wing, WING_COLOR, wing_points)
    screen.blit(rotated_wing, rotated_wing.get_rect(center=(x+20, y+20)))

    # Eye
    pygame.draw.circle(screen, EYE_COLOR, (x + 70, y + 15), 5)


def draw_fish(rect, movement):
    # Fish body
    body_rect = pygame.Rect(rect.left, rect.top, rect.width, rect.height)
    pygame.draw.ellipse(screen, LIGHT_BLUE, body_rect)
    
    # Gradient effect on body
    for i in range(5):
        grad_rect = pygame.Rect(rect.left + i * rect.width // 5, rect.top, rect.width // 5, rect.height)
        grad_color = [max(0, c - i * 15) for c in LIGHT_BLUE]
        pygame.draw.ellipse(screen, grad_color, grad_rect)
    
    # Belly
    belly_rect = pygame.Rect(rect.left + rect.width // 4, rect.centery, rect.width * 2 // 3, rect.height // 2)
    pygame.draw.ellipse(screen, WHITE, belly_rect)
    
    # Tail 
    tail_angle = math.sin(pygame.time.get_ticks() * 0.01) * 30 - movement * 2
    tail_surf = pygame.Surface((rect.width // 2, rect.height), pygame.SRCALPHA)
    tail_points = [
        (rect.width // 2, rect.height // 2),
        (0, rect.height // 4),
        (0, rect.height * 3 // 4)
    ]
    pygame.draw.polygon(tail_surf, LIGHT_BLUE, tail_points)
    pygame.draw.polygon(tail_surf, DARK_BLUE, tail_points, 2)  
    rotated_tail = pygame.transform.rotate(tail_surf, tail_angle)
    tail_pos = (rect.left - rect.width // 8, rect.centery)
    screen.blit(rotated_tail, rotated_tail.get_rect(center=tail_pos))
    
    # Eye
    eye_x = rect.right - rect.width // 5
    eye_y = rect.top + rect.height // 3
    pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 8)
    pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 4)
    pygame.draw.circle(screen, WHITE, (eye_x - 1, eye_y - 1), 1)  
    
    # Mouth
    mouth_points = [
        (rect.right, rect.centery),
        (rect.right - rect.width // 8, rect.centery + rect.height // 8),
        (rect.right - rect.width // 8, rect.centery - rect.height // 8)
    ]
    pygame.draw.polygon(screen, PINK, mouth_points)
    pygame.draw.polygon(screen, DARK_BLUE, mouth_points, 2)  
    
    # Wings (stationary)
    # Top wing
    top_wing_surf = pygame.Surface((rect.width // 2, rect.height // 2), pygame.SRCALPHA)
    top_wing_points = [
        (0, rect.height // 4),
        (rect.width // 4, 0),
        (rect.width // 2, rect.height // 4)
    ]
    pygame.draw.polygon(top_wing_surf, LIGHT_BLUE, top_wing_points)
    pygame.draw.polygon(top_wing_surf, DARK_BLUE, top_wing_points, 2)  
    top_wing_pos = (rect.centerx, rect.top)
    screen.blit(top_wing_surf, top_wing_surf.get_rect(center=top_wing_pos))

    # Bottom wing
    bottom_wing_surf = pygame.Surface((rect.width // 2, rect.height // 2), pygame.SRCALPHA)
    bottom_wing_points = [
        (0, 0),
        (rect.width // 4, rect.height // 4),
        (rect.width // 2, 0)
    ]
    pygame.draw.polygon(bottom_wing_surf, LIGHT_BLUE, bottom_wing_points)
    pygame.draw.polygon(bottom_wing_surf, DARK_BLUE, bottom_wing_points, 2)  

    bottom_wing_offset = rect.height // 5

    bottom_wing_pos = (rect.centerx, rect.bottom + bottom_wing_offset)
    screen.blit(bottom_wing_surf, bottom_wing_surf.get_rect(center=bottom_wing_pos))
    
    # Body outline
    pygame.draw.ellipse(screen, DARK_BLUE, body_rect, 2)
    
    # Scales (simple version)
    for i in range(3):
        for j in range(4):
            scale_x = rect.left + rect.width // 3 + i * rect.width // 8
            scale_y = rect.top + rect.height // 4 + j * rect.height // 6
            scale_rect = pygame.Rect(scale_x, scale_y, rect.width // 16, rect.height // 12)
            pygame.draw.arc(screen, DARK_BLUE, scale_rect, math.pi, 2 * math.pi, 1)
    
    # Bubbles
    for i in range(3):
        bubble_x = rect.left - i * 15 - 10
        bubble_y = rect.centery - 10 + math.sin(pygame.time.get_ticks() * 0.01 + i) * 5
        pygame.draw.circle(screen, WHITE, (bubble_x, bubble_y), 3 - i)
        pygame.draw.circle(screen, DARK_BLUE, (bubble_x, bubble_y), 3 - i, 1)

def draw_bird(rect, movement):
    # Bird body
    body_rect = pygame.Rect(rect.left, rect.top, rect.width, rect.height)
    pygame.draw.ellipse(screen, RED, body_rect)
    
    # Belly
    belly_rect = pygame.Rect(rect.left + rect.width // 4, rect.centery, rect.width // 2, rect.height // 2)
    pygame.draw.ellipse(screen, LIGHT_RED, belly_rect)
    
    # Wing
    wing_rect = pygame.Rect(rect.left, rect.centery - 10, rect.width - 15, rect.height // 2)
    wing_angle = math.sin(pygame.time.get_ticks() * 0.01) * 30 - movement * 2
    wing_surf = pygame.Surface((wing_rect.width, wing_rect.height), pygame.SRCALPHA)
    pygame.draw.ellipse(wing_surf, ORANGE, (0, 0, wing_rect.width, wing_rect.height))
    rotated_wing = pygame.transform.rotate(wing_surf, wing_angle)
    wing_pos = (rect.left + 5, rect.centery - 5)
    screen.blit(rotated_wing, rotated_wing.get_rect(center=wing_pos))
    
    # Eye
    eye_x = rect.right - 8
    eye_y = rect.top + rect.height // 3
    pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 6)
    pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 4)
    
    # Beak
    beak_points = [
        (rect.right - 2, rect.centery),
        (rect.right + 10, rect.centery - 4),
        (rect.right + 10, rect.centery + 4)
    ]
    pygame.draw.polygon(screen, YELLOW, beak_points)
    
    # Outline
    pygame.draw.ellipse(screen, BLACK, body_rect, 2)
    
    # Tail feathers
    tail_points = [
        (rect.left, rect.centery),
        (rect.left - 10, rect.centery - 5),
        (rect.left - 10, rect.centery + 5)
    ]
    pygame.draw.polygon(screen, ORANGE, tail_points)
    pygame.draw.polygon(screen, BLACK, tail_points, 2)

def check_collision(pipes):
    for pipe in pipes:
        if fish_rect.colliderect(pipe):
            return False

    if fish_rect.top <= 0 or fish_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
        return False

    return True

def display_score(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)
    elif game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'Best Score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(high_score_surface, high_score_rect)

        name_surface = small_font.render(f'by {high_score_name}', True, WHITE)
        name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(name_surface, name_rect)

def update_score(score, high_score, high_score_name):
    if score > high_score:
        high_score = score
        high_score_name = ask_name()
        save_high_score(high_score, high_score_name)
    return high_score, high_score_name

def ask_name():
    name = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        
        screen.fill(BLUE)
        text_surface = game_font.render("Enter your name:", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text_surface, text_rect)

        name_surface = game_font.render(name, True, WHITE)
        name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(name_surface, name_rect)

        pygame.display.flip()
    
    return name

def save_high_score(score, name):
    data = {'score': score, 'name': name}
    with open('high_score.json', 'w') as f:
        json.dump(data, f)

def load_high_score():
    try:
        with open('high_score.json', 'r') as f:
            data = json.load(f)
        return data['score'], data['name']
    except FileNotFoundError:
        return 0, ""

def draw_start_screen():
    screen.blit(background, (0, 0))
    
    # Draw title
    title_surface = title_font.render('Flappy Fish', True, WHITE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_surface, title_rect)
    
    # Draw start instruction
    start_surface = game_font.render('Press SPACE to start', True, WHITE)
    start_rect = start_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(start_surface, start_rect)
    
    # Draw high score
    high_score_surface = small_font.render(f'High Score: {int(high_score)} by {high_score_name}', True, WHITE)
    high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4))
    screen.blit(high_score_surface, high_score_rect)
    
    # Draw fish
    draw_fish(fish_rect, 0)
    
    # Draw ground
    draw_ground()

# Load high score
high_score, high_score_name = load_high_score()

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if start_screen:
                    start_screen = False
                    game_active = True
                    pipe_list.clear()
                    fish_rect.center = (100, SCREEN_HEIGHT // 2)
                    bird_movement = 0
                    score = 0
                elif game_active:
                    bird_movement = -8  
                else:
                    game_active = True
                    pipe_list.clear()
                    fish_rect.center = (100, SCREEN_HEIGHT // 2)
                    bird_movement = 0
                    score = 0

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    if start_screen:
        draw_start_screen()
    elif game_active:
        screen.blit(background, (0, 0))

        # Bird
        bird_movement += gravity
        fish_rect.centery += bird_movement
        draw_fish(fish_rect, bird_movement)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        score += 0.01
        display_score('main_game')

        # Clouds
        for cloud in clouds:
            cloud.move()
            cloud.draw()

        # Ground
        draw_ground()
    else:
        screen.blit(background, (0, 0))
        high_score, high_score_name = update_score(score, high_score, high_score_name)
        display_score('game_over')
        draw_ground()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
