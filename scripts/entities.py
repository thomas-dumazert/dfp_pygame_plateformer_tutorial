import math
import random

import pygame

from scripts.particle import Particle
from scripts.spark import Spark

TRANSITION_DELAY = 5    # Number of frames before transitioning from a 
                        # state to another

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size) -> None:
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 
                           'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

        self.fall_acceleration = 0.1
        self.terminal_velocity = 5
    
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.pos[0], self.pos[1], 
                           self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)) -> None:
        self.collisions = {'up': False, 'down': False, 
                           'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], 
                          movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
            
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.last_movement = movement

        self.velocity[1] = min(self.terminal_velocity, 
                               self.velocity[1] + self.fall_acceleration)

        if self.collisions['up'] or self.collisions['down']:
            self.velocity[1] = 0
        
        self.animation.update()
    
    def render(self, surf, offset=(0, 0)) -> None:
        surf.blit(pygame.transform.flip(self.animation.img(), 
                                        self.flip, False),
                                        (self.pos[0] - offset[0] + \
                                            self.anim_offset[0], 
                                            self.pos[1] - offset[1] + \
                                                self.anim_offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size) -> None:
        super().__init__(game, 'player', pos, size)
        self.air_time = 0

        self.jumps = 1
        self.remaining_jumps = self.jumps
        self.jump_velocity = -3

        self.wall_slide = False
        self.wall_slide_fall_velocity = 0.5
        self.wall_slide_impulse_velocity = (3.5, -2.5)

        self.dashing = 0
        self.dash_cooldown = 50
        self.dash_duration = 10
        self.dash_cycle = self.dash_cooldown + self.dash_duration
        self.dash_velocity = 8
        self.dash_final_brake = 0.1

        self.stream_velocity = 3
        self.fall_time_limit = 120
    
    def jump(self) -> bool:
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = self.wall_slide_impulse_velocity[0]
                self.velocity[1] = self.wall_slide_impulse_velocity[1]
                self.air_time = TRANSITION_DELAY
                self.remaining_jumps = max(self.remaining_jumps - 1, 0)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -self.wall_slide_impulse_velocity[0]
                self.velocity[1] = self.wall_slide_impulse_velocity[1]
                self.air_time = TRANSITION_DELAY
                self.remaining_jumps = max(self.remaining_jumps - 1, 0)
                return True

        elif self.remaining_jumps:
            self.remaining_jumps -= 1
            self.velocity[1] = self.jump_velocity
            self.air_time = TRANSITION_DELAY
            return True

        return False
    
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -self.dash_cycle
            else:
                self.dashing = self.dash_cycle

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        self.air_time += 1

        if self.collisions['down']:
            self.air_time = 0
            self.remaining_jumps = self.jumps
        
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and \
            self.air_time >= TRANSITION_DELAY:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 
                                   self.wall_slide_fall_velocity)

            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            
            self.set_action('wall_slide')
        
        if not self.wall_slide:
            if self.air_time >= TRANSITION_DELAY:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if abs(self.dashing) in {self.dash_cycle, self.dash_cooldown}:
            self.burst_particles()
        
        if self.dashing > 0:
            self.dashing = max(self.dashing - 1, 0)
        if self.dashing < 0:
            self.dashing = min(self.dashing + 1, 0)

        if abs(self.dashing) > self.dash_cooldown:
            direction = abs(self.dashing) / self.dashing
            self.velocity[0] = direction * self.dash_velocity
            if abs(self.dashing) == self.dash_cooldown + 1:
                self.velocity[0] *= self.dash_final_brake
            self.stream_particules()
        
        
        
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
    
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= self.dash_cooldown:
            super().render(surf, offset)
    
    def burst_particles(self):
        for _ in range(20):
            angle = random.random() * math.pi * 2
            speed = random.random() * 0.5 + 0.5
            p_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.game.particles.append(Particle(self.game, 'particle', 
                                                self.rect().center, 
                                                velocity=p_velocity,
                                                frame=random.randint(0, 7)))
    
    def stream_particules(self):
        p_velocity = [abs(self.dashing) / self.dashing \
                      * random.random() * self.stream_velocity, 0]
        self.game.particles.append(Particle(self.game, 'particle', 
                                                self.rect().center, 
                                                velocity=p_velocity,
                                                frame=random.randint(0, 7)))

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size) -> None:
        super().__init__(game, 'enemy', pos, size)
        
        self.wake_up_chance = 0.01

        self.walking = 0
        self.walking_speed = 0.5
        self.walking_duration_range = (30, 120)

        self.gun_pos = (4, 2)

        self.shooting_range = (0, 16)

    def update(self, tilemap, movement=(0, 0)) -> bool:
        if self.walking:
            # +/- 7 and 23 allow to check the tiles in front and below 
            # the enemy. Those can be computed from enemy and tile 
            # sizes.
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), 
                                    self.pos[1] + 23)):
                movement = (movement[0] - self.walking_speed \
                            if self.flip else self.walking_speed, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(self.walking - 1, 0)

            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], 
                       self.game.player.pos[1] - self.pos[1])
                if abs(dis[1]) < self.shooting_range[1]:
                    self.shoot(dis)
        elif random.random() < self.wake_up_chance:
            self.walking = random.randint(*self.walking_duration_range)

        super().update(tilemap, movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
        if abs(self.game.player.dashing) > self.game.player.dash_cooldown:
            if self.rect().colliderect(self.game.player.rect()):
                self.dying()
                return True
            
    def dying(self):
        for _ in range(30):
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.game.sparks.append(Spark(self.rect().center, 
                                        angle, 
                                        random.random() + 2))
            self.game.particles.append(Particle(self.game, 
                                            'particle', 
                                            self.rect().center, 
                                            velocity=[math.cos(angle + math.pi) * speed * 0.5, 
                                                        math.sin(angle + math.pi) * speed * 0.5], 
                                            frame=random.randint(0, 7)))
        self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
        self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
            
    def shoot(self, dis):
        if self.flip and dis[0] < 0:
            self.game.projectiles.append([[self.rect().centerx - 7, 
                                           self.rect().centery], 
                                          -1.5, 0])
            for _ in range(4):
                self.game.sparks.append(Spark(self.game.projectiles[-1][0], 
                                              random.random() - 0.5 + math.pi, 
                                              2 + random.random()))
        if not self.flip and dis[0] > 0:
            self.game.projectiles.append([[self.rect().centerx + 7, 
                                           self.rect().centery], 
                                          1.5, 0])
            for i in range(4):
                self.game.sparks.append(Spark(self.game.projectiles[-1][0], 
                                              random.random() - 0.5, 
                                              2 + random.random()))

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], 
                                            True, False), 
                                            (self.rect().centerx \
                                             - self.gun_pos[0] \
                                                - self.game.assets['gun'].get_width() \
                                                    - offset[0], 
                                             self.rect().centery \
                                                - self.gun_pos[1] \
                                                    - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], 
                      (self.rect().centerx + self.gun_pos[0] - offset[0], 
                       self.rect().centery - self.gun_pos[1] - offset[1]))