import pygame
import random

# Initialize Pygame
pygame.init()


# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

MAX_FIRES=50

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Urban Tree Impact")
clock = pygame.time.Clock()

buildingimg=pygame.image.load("building.png").convert()
fireimg=pygame.transform.scale(pygame.image.load("fire.png").convert(),(40,40))
backgroundimg=pygame.transform.scale(pygame.image.load("background.jpg").convert(),(WIDTH,HEIGHT))

# Game Variables
temperature = 40  # Starting temperature
pollution = 100  # Pollution level

trees = []  # List of tree positions
buildings = []  # List of buildings
people = []  # List of people
fires = []  # List of fire positions

# Font
font = pygame.font.Font(None, 36)

class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def move(self):
        if trees:
            nearest_tree = min(trees, key=lambda t: (self.x - t[0])**2 + (self.y - t[1])**2)
            dx = nearest_tree[0] - self.x
            dy = nearest_tree[1] - self.y
            self.x += (dx // abs(dx)) * random.randint(-8, 10)/3 if dx != 0 else random.choice([-1, 1])
            self.y += (dy // abs(dy)) * random.randint(-8, 10)/3 if dy != 0 else random.choice([-1, 1])
        else:
            self.x += random.choice([-2, -1, 1, 2])
            self.y += random.choice([-2, -1, 1, 2])
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

    def get_color(self):
        if temperature < 30:
            return BLUE
        elif temperature < 50:
            return ORANGE
        else:
            return RED

    def draw(self):
        pygame.draw.circle(screen, self.get_color(), (self.x, self.y), 5)

def draw_environment():
    screen.blit(backgroundimg,(0,0))
    for building in buildings:
        screen.blit(pygame.transform.scale(buildingimg,(building.width,building.height)),(building.left,building.top))
    for tree in trees:
        pygame.draw.circle(screen, GREEN, tree, 15)  # Draw trees
    for person in people:
        person.draw()
    for fire in fires:
        screen.blit(fireimg,fire)
    temp_text = font.render(f"Temperature: {round(temperature)}°C", True, RED)
    poll_text = font.render(f"Pollution: {round(pollution)}", True, GRAY)
    screen.blit(temp_text, (10, 10))
    screen.blit(poll_text, (10, 50))

def plant_tree(x, y):
    if any(building.collidepoint(x, y) for building in buildings):
        return
    trees.append((x, y))

def spawn_building():
    
    x = random.randint(100, WIDTH - 100)
    y = random.randint(100, HEIGHT - 100)
    width = random.randint(50, 100)
    height = random.randint(50, 100)
    building=pygame.Rect(x, y, width, height)
    buildings.append(building)
    for i in range(2):
        if len(trees)>0:
            trees.remove(trees[0])
    for i in range(len(trees)-1,-1,-1):
        if building.collidepoint(trees[i][0],trees[i][1]):
            trees.remove(trees[i])
    for i in range(len(people)-1,-1,-1):
        if building.collidepoint(people[i].x,people[i].y):
            people.remove(people[i])

def spawn_fire():
    if random.random() < (temperature - 30) / 500.0:
        x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
        fires.append((x, y))
        if len(fires)>MAX_FIRES:
            fires.remove(fires[0])


def tick_fire():
    for i in range(len(fires)-1,-1,-1):
        fireX,fireY=fires[i]
        if random.random() < (60 - temperature) / 500.0:
            fires.remove(fires[i])
        elif random.random() < (temperature - 30) / 100.0:
            x, y = fireX+random.randint(-20,20), fireY+random.randint(-20,20)
            fires.append((x, y))
            if len(fires)>MAX_FIRES:
                fires.remove(fires[0])
        fireRect=pygame.Rect(fireX,fireY,20,20)
        for i in range(len(trees)-1,-1,-1):
            if fireRect.collidepoint(trees[i][0],trees[i][1]):
                trees.remove(trees[i])
        for i in range(len(people)-1,-1,-1):
            if fireRect.collidepoint(people[i].x,people[i].y):
                people.remove(people[i])
        for i in range(len(buildings)-1,-1,-1):
            if fireRect.colliderect(buildings[i]) and random.randint(1,10)==1:
                buildings.remove(buildings[i])
        

def update_environment():
    global temperature, pollution
    temperature = max(20, temperature - len(trees) * 0.0005)
    pollution = max(0, pollution - len(trees) * 0.001)
    tick_fire()

def game_loop():
    global temperature, pollution
    running = True
    spawn_timer = 0
    max_people = 10
    previousPlant=0
    
    for _ in range(max_people):
        x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
        people.append(Person(x, y))
    
    for _ in range(10):
        spawn_building()
        
    for _ in range(20):
        x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
        plant_tree(x, y)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                time=pygame.time.get_ticks()
                if time-previousPlant>200:
                    previousPlant=time
                    x, y = pygame.mouse.get_pos()
                    plant_tree(x, y)
        
        if spawn_timer % 100 == 0 and len(trees)>=2 and len(people)>0:
            spawn_building()
        spawn_timer += 1
        
        for person in people:
            person.move()
        
        max_people=len(buildings)*2
        if len(people) < max_people and len(people)>1:
            x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
            people.append(Person(x, y))
        elif len(people) > max_people:
            people.pop(0)
        
        spawn_fire()

        update_environment()
        
        draw_environment()
        pygame.display.flip()
        
        if random.random() < 0.01:
            temperature += 1
            pollution += 2

        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    game_loop()