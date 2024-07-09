import pygame

from scripts.entities import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.utils import load_image, load_images, Animation

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
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
        }
        
        self.player = Player(self, (50, 50), (8, 15))
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