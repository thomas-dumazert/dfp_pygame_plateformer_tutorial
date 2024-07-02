import pygame

from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.utils import load_image, load_images

class Player:
    def __init__(self, pos_x: int=0, pos_y: int=0, 
                 colorkey: tuple=(0, 0, 0)) -> None:
        self.pos = pygame.Vector2(pos_x, pos_y)
        self.size = 40
        self.movement = pygame.Vector2(0, 0)
        self.speed = 300
        self.img = pygame.image.load('data/images/clouds/cloud_1.png')
        self.colorkey = colorkey
        self.img.set_colorkey(self.colorkey)
        self.collision_box = pygame.Rect(self.pos.x, self.pos.y, 
                                         self.img.get_width(), 
                                         self.img.get_height())

    def run(self, dt, events=None) -> None:
        if events is not None:
            self.handle_events(events)
            self.update_pos(dt)

    def update_pos(self, dt):
        self.pos += self.movement * self.speed * dt
        self.collision_box = pygame.Rect(self.pos.x, self.pos.y, 
                                         self.img.get_width(), 
                                         self.img.get_height())

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.movement.y += 1
                if event.key == pygame.K_z:
                    self.movement.y -= 1
                if event.key == pygame.K_d:
                    self.movement.x += 1
                if event.key == pygame.K_q:
                    self.movement.x -= 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    self.movement.y -= 1
                if event.key == pygame.K_z:
                    self.movement.y += 1
                if event.key == pygame.K_d:
                    self.movement.x -= 1
                if event.key == pygame.K_q:
                    self.movement.x += 1
    
    def check_collision(self, objects: list=None) -> None:
        if objects is not None:
            for obj in objects:
                if self.collision_box.colliderect(obj.collision_box):
                    obj.collide_reaction(self)

    def draw(self, screen):
        screen.blit(self.img, self.pos)

class CollisionRect:
    def __init__(self, x, y, width, height, base_color: tuple, collision_color: tuple) -> None:
        self.collision_box = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.collision_color = collision_color
        self.actual_color = self.base_color

    def collide_reaction(self, _):
        self.actual_color = self.collision_color

    def run(self):
        self.actual_color = self.base_color

    def draw(self, screen) -> None:
        pygame.draw.rect(screen, self.actual_color, self.collision_box)

class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.bg_color = (14, 219, 248)

        self.clock = pygame.time.Clock()
        self.dt = 0

        self.running = True

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
        }
        
        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))
        self.movement = [False, False]

        self.tilemap = Tilemap(self, tile_size=16)
        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.scroll = [0, 0]
        self.camera_acc = 30
    
    def handle_events(self) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.movement[0] = True
                if event.key == pygame.K_d:
                    self.movement[1] = True
                if event.key == pygame.K_z:
                    self.player.velocity[1] = -3
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    self.movement[0] = False
                if event.key == pygame.K_d:
                    self.movement[1] = False

    def run(self) -> None:
        while self.running:
            self.display.blit(self.assets['background'], (0, 0))

            self.scroll[0] += (self.player.rect().centerx - \
                               self.display.get_width() / 2 - \
                                self.scroll[0]) / self.camera_acc

            self.scroll[1] += (self.player.rect().centery - \
                               self.display.get_height() / 2 - \
                                self.scroll[1]) / self.camera_acc
            
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.clouds.update()
            
            self.player.update(self.tilemap, 
                               (self.movement[1] - self.movement[0], 0))

            self.handle_events()

            self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)
            self.player.render(self.display, offset=render_scroll)

            self.screen.blit(pygame.transform.scale(self.display, 
                                                    self.screen.get_size()), 
                                                    (0, 0))
            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000

if __name__ == '__main__':
    Game().run()