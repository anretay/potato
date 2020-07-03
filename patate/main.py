import pygame
import os
import time
import random
pygame.font.init()

#écran
WIDTH, HEIGHT = 750, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Return of the Potato: Legendary Edition")

#chargement des images
KITTEN = pygame.image.load(os.path.join("kitten.png"))
KITTEN = pygame.transform.scale(KITTEN, (35, 35))
PIANO = pygame.image.load(os.path.join("piano.png"))
PIANO = pygame.transform.scale(PIANO, (35, 35))
COW = pygame.image.load(os.path.join("cow.png"))
COW = pygame.transform.scale(COW, (35, 35))

POTATOR = pygame.image.load(os.path.join("potator_kalash.png"))
POTATOR = pygame.transform.scale(POTATOR, (70, 70))

FRIDGE = pygame.image.load(os.path.join("fridge.png"))
FRIDGE = pygame.transform.scale(FRIDGE, (65, 65))

VACUUM = pygame.image.load(os.path.join("vacuum.png"))
VACUUM = pygame.transform.scale(VACUUM, (57, 65))

WASHING_MACHINE = pygame.image.load(os.path.join("washing.png"))
WASHING_MACHINE = pygame.transform.scale(WASHING_MACHINE, (42, 65))

BULLET = pygame.image.load(os.path.join("bullet.png"))
BULLET = pygame.transform.scale(BULLET, (30, 30))

BACKGROUND = pygame.image.load(os.path.join("background.png"))

class Projectile:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x += vel

    def off_screen(self, width):
        return not(self.x <= width and self.x >= 0)

    def collision(self, obj):
        return collide(self, obj)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask , (offset_x, offset_y)) != None #(x,y)



class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.projectile_img = None
        self.projectiles = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for projectile in self.projectiles:
            projectile.draw(window)

    def move_projectiles(self, vel, obj):
        self.cooldown()
        for projectile in self.projectiles:
            projectile.move(vel)
            if projectile.off_screen(WIDTH):
                self.projectiles.remove(projectile)
            elif projectile.collision(obj):
                obj.health -= 10
                self.projectiles.remove(projectile)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            projectile = Projectile(self.x+10, self.y+22, self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) #utilise l'initialisation de player dans Player
        self.ship_img = POTATOR
        self.projectile_img = BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_projectiles(self, vel, objs):
        self.cooldown()
        for projectile in self.projectiles:
            projectile.move(vel)
            if projectile.off_screen(WIDTH):
                self.projectiles.remove(projectile)
            else:
                for obj in objs:
                    if projectile.collision(obj):
                        objs.remove(obj)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 7, self.ship_img.get_width() - 3, 7))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 7, (self.ship_img.get_width() - 3)* (self.health/self.max_health), 7 ))

class Enemy(Ship):
    
    GENRE_MAP = {
                "fridge": (FRIDGE, KITTEN),
                "washing_machine": (WASHING_MACHINE, COW),
                "vacuum_cleaner": (VACUUM, PIANO),
                }

    def __init__(self, x, y, genre, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.projectile_img = self.GENRE_MAP[genre]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.x -= vel 

    def shoot(self):
        if self.cool_down_counter == 0:
            projectile = Projectile(self.x, self.y + 8, self.projectile_img)
            self.projectiles.append(projectile)
            self.cool_down_counter = 1


#fonction principale
def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 40) 
    lost_font = pygame.font.SysFont("comicsans", 60) 

    enemies = []
    wave_lenght = 5
    enemy_vel = 1

    score = 0

    player_vel = 5 
    projectile_vel = -7
    player = Player(300,300)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WINDOW.blit(BACKGROUND, (0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))

        WINDOW.blit(lives_label, (620,20))
        WINDOW.blit(level_label, (620,450))
        WINDOW.blit(score_label, (20,450))

        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("Game Over", 1, (255,255,255))
            WINDOW.blit(lost_label, ((WIDTH/2 - lost_label.get_width()/2), 200))


        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        score += 1

        if player.health <= 0:
        	lives -= 1
        	player.health = 100


        if lives <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else: 
                continue
        
        if len(enemies) == 0:
            level += 1 
            wave_lenght += 5
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(850, 2250), random.randrange(50, 450), random.choice(["fridge", "washing_machine", "vacuum_cleaner"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: #gauche
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #droite
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #haut
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 7 < HEIGHT: #bas
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel) 
            enemy.move_projectiles(-5, player)

            if random.randrange(0, 180) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.x + enemy.get_width() < 0:
                lives -= 1
                enemies.remove(enemy)


        player.move_projectiles(-projectile_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 60)
    studio_font = pygame.font.SysFont("comicsans", 22)
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        studio_label = studio_font.render("Cool Studios®", 1, (255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 220))
        WINDOW.blit(studio_label, (630, 470))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    
    pygame.quit()

main_menu()