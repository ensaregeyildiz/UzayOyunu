from pygame import *
from random import randint
from time import time as timer

skor = 0
lost = 0
goal = 10
max_lost = 3
life = 3
reload_time = 3 
ammo_capacity = 10

# Yazı oluşturucusunun tanımlanması
font.init()
yazi = font.SysFont("Arial", 30)
yazi2 = font.SysFont("Arial", 50)

win = yazi2.render("KAZANDIN!", True, (255,255,255))
lose = yazi2.render("KAYBETTİN!", True, (180, 0, 0))

#Arkaplan müziğinin ayarlanması
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
fire_sound = mixer.Sound("fire.ogg")
boom_sound = mixer.Sound("explode.wav")


#Oyun penceresi oluşturulması
window_width, window_height = 700, 500
window = display.set_mode((window_width, window_height))
display.set_caption("Shooter")
background = transform.scale(image.load("galaxy.jpg"), (window_width, window_height))

# Gamesprite sınıfının oluşturulması
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()

        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Oyuncu sınıfının oluşturulması
class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < window_width - 90:
            self.rect.x += self.speed
    
    def fire(self):
        img_bullet = "bullet.png"
        bullet = Bullet(img_bullet, self.rect.centerx - 7, self.rect.top, 15, 20, 15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost

        if self.rect.y > window_height:
            self.rect.x = randint(80, window_width - 80)
            self.rect.y = 0
            lost = lost + 1

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed

        if self.rect.y > window_height:
            self.rect.x = randint(80, window_width - 80)
            self.rect.y = 0

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        # Ekranın kenarına ulaşıldığında sprite'ın kaldırılması
        if self.rect.y < 0:
            self.kill()


# Oyuncu nesnesinin oluşturulması
img_hero = "rocket.png"
ship = Player(img_hero, 5, window_height - 100, 80, 100, 10)

# Düşman grubunun oluşturulması
monsters = sprite.Group()

# Düşman nesnesinin oluşturulması
img_enemy = "ufo.png"
for i in range(1, 6):
    monster = Enemy(img_enemy,randint(80, window_width - 80), -40, 80, 50, randint(1, 3))
    monsters.add(monster)

# Asteroid grubunun oluşturulması

asteroids = sprite.Group()

# Asteroid nesnesinin oluşturulması
img_asteroid = "asteroid.png"
for i in range(1, 3):
    asteroid = Asteroid(img_asteroid, randint(30, window_width -30), -40, 80, 50, randint(1, 7))
    asteroids.add(asteroid)

# Mermi grubunun oluşturulması
bullets = sprite.Group()

# Oyunun bittiğine dair değişken oluşturulması
finish = False

#Oyun döngüsünün oluşturulması
clock = time.Clock()
FPS = 60
run = True

num_fire = 0
reltime = False

while run:
    #Pencere kapatılması
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN and e.key == K_SPACE:
            if num_fire < ammo_capacity and reltime == False:
                num_fire += 1
                fire_sound.play()
                ship.fire()
            
            if num_fire >= ammo_capacity and reltime == False:
                last_time = timer()
                reltime = True
    
    if not finish:
        window.blit(background, (0, 0))

        # Sayaç yazılarının tanımlanması
        skor_yazisi = yazi.render("Skor: " + str(skor), 1, (255, 255, 255))
        window.blit(skor_yazisi, (10, 10))

        lost_yazisi = yazi.render("Kayıp: " + str(lost), 1, (255, 255, 255))
        window.blit(lost_yazisi, (10, 35))

        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update()

        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        if reltime == True:
            now_time = timer()

            if (now_time - last_time) < reload_time:
                reloading = yazi.render("Bekleyin! Yeniden Dolduruluyor!", 1, (150, 0, 0))
                window.blit(reloading, (175, 460))
            else:
                num_fire = 0
                reltime = False

        collides = sprite.groupcollide(monsters, bullets, True, True)
        
        for c in collides:
            skor = skor + 1
            boom_sound.play()
            monster = Enemy(img_enemy,randint(80, window_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
        
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1
        
        if life == 0 or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))
        
        if skor >= goal:
            finish = True
            window.blit(win, (200, 200))
        
        if life == 3:
            life_color = (0, 150, 0)
        if life == 2:
            life_color = (150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)
        
        text_life = yazi2.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10)) 

        display.update()
    
    clock.tick(FPS)