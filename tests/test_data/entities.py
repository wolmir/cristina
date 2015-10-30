import pygame
import level as l

class Entity(pygame.sprite.Sprite):

    speed   = 3
    max_speed    = 8
    accel_atm    = 1
    airaccel_atm = 1
    deaccel_atm  = 5

    fall_accel     = 3.75
    jump_mod       = 2.5
    jump_accel     = 25
    max_fall_speed = 30    
    
    def __init__(self, (x, y)):
        super(Entity, self).__init__()

        self.life = 100
        self.vx      = x
        self.vy      = y
        self.jumping  = False
        self.falling  = False
        self.runing   = False
        self.on_block = False
        
        self.sprite        = []
        self.normal_frames = []
        self.run_frames    = []
        self.jump_frames   = []
        
        self.direction = 'ltr'
        self.current_frame = 0

        self.clock = pygame.time.Clock()
        self.fps = 8

    def get_frame(self, frames):
        if self.current_frame  < len(frames) - 1:
            self.current_frame += 1
        else:
            self.current_frame = 0

        return self.current_frame

    

    def accelerate(self, accel, speed):
        if accel != 0:
            if  ((speed < 0) and (accel > 0)) or\
                ((speed > 0 ) and (accel < 0)):
                speed = accel
            else:
                speed += accel

        if speed > self.max_speed:
            speed = self.max_speed
        if speed < -self.max_speed:
            speed = -self.max_speed

        

        return speed

    def jump(self, speed, on_block):
        if on_block: 
            speed -= self.jump_accel
            current_frame = self.get_frame(self.jump_frames)
            if self.direction == 'ltr':
                self.image = self.jump_frames[current_frame]
            else:
                self.image = pygame.transform.flip(self.jump_frames[current_frame],1,0)

        speed += self.fall_accel - self.jump_mod
        if self.direction == 'ltr':
            self.image = self.fall_frame
        else:
            self.image = pygame.transform.flip(self.fall_frame,1,0)

        if speed > self.max_fall_speed:
            speed = self.max_fall_speed



        return speed

    def fall(self, speed):
        # print 'por aqui'
        speed += self.fall_accel
        if self.direction == 'ltr':
            self.image = self.fall_frame
        else:
            self.image = pygame.transform.flip(self.fall_frame,1,0)

        if speed > self.max_fall_speed:
            speed = self.max_fall_speed

        return speed

    def run(self):

        current_frame = self.get_frame(self.run_frames)
        if self.direction == 'ltr':
            self.vx = +self.speed
            self.image = self.run_frames[current_frame]
        else:
            self.vx = -self.speed
            self.image = pygame.transform.flip(self.run_frames[current_frame],1,0)

    def normal(self):
        current_frame = self.get_frame(self.normal_frames)
        if self.direction == 'ltr':
            self.image = self.normal_frames[current_frame]
        else:
            self.image = pygame.transform.flip(self.normal_frames[current_frame],1,0)

        

    def collide(self, vx, vy, level, o_b):
        for y in range(level.height):
            for x in range(level.width):
                t = level.gt(x, y, level.collition_layer)
                if t == 0:
                    continue
                else:
                    r = pygame.Rect(x*level.tw, y*level.th, 
                                    level.tw, level.th)
                    if self.rect.colliderect(r):
                        if vx > 0:
                            self.rect.right = r.left
                        if vx < 0:
                            self.rect.left = r.right
                        if vy > 0:
                            self.rect.bottom = r.top
                            self.on_block = True
                            self.vy = 0
                            self.jumping = False
                            self.falling = False
                        if vy < 0:
                            self.rect.top = r.bottom

        for o in o_b:
            if pygame.sprite.collide_rect(self, o):
                if vx > 0:
                    self.rect.right = o.rect.left
                if vx < 0:
                    self.rect.left = o.rect.right
                if vy > 0:
                    self.rect.bottom = o.rect.top
                    self.on_block = True
                    self.vy = 0
                    self.jumping = False
                    self.falling = False
                if vy < 0:
                    self.rect.top = o.rect.bottom


    def update(self, level, o_b):
       

        if not self.jumping and not self.runing and self.on_block:
            current_frame = self.get_frame(self.normal_frames)
            if self.direction == 'ltr':
                self.image = self.normal_frames[current_frame]
            else:
                self.image = pygame.transform.flip(self.normal_frames[current_frame],1,0)

        if self.runing:
            current_frame = self.get_frame(self.run_frames)
            if self.direction == 'ltr':
                self.vx = self.accelerate(self.accel_atm, self.vx)
                self.image = self.run_frames[current_frame]
            else:
                self.vx = self.accelerate(-self.accel_atm, self.vx)
                self.image = pygame.transform.flip(self.run_frames[current_frame],1,0)
        else:
            self.vx = 0

        if self.jumping and self.on_block:
            self.vy -= self.jump_accel
            if self.direction == 'ltr':
                self.image = self.fall_frame
            else:
                self.image = pygame.transform.flip(self.fall_frame,1,0)

        if not self.on_block:
            self.vy += self.fall_accel
            
            if self.vy > self.max_fall_speed:
                self.vy = self.max_fall_speed

        if self.falling:
            if self.direction == 'ltr':
                self.image = self.fall_frame
            else:
                self.image = pygame.transform.flip(self.fall_frame,1,0)

        self.rect.left += self.vx
        self.collide(self.vx, 0, level, o_b)

        self.rect.top += self.vy
        self.on_block = False
        self.collide(0, self.vy, level, o_b)

        self.clock.tick(self.fps)


    def damage(self, hp):
        self.life -= hp
        self.image = self.damage_frame
        self.vy -= 6
        self.vx -= 6
        if self.life == 0:
            print 'Die'




