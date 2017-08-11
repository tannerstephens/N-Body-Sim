#!/usr/bin/env python3.6

import pygame, math, random, nSim.utils
pygame.init()
from pygame.locals import *

G = 6.674 * pow(10,-11)

class body:
    def __init__(self,pos,r,mass):
        self.pos = list(pos)
        self.vel = [0,0]
        self.r = r
        self.vol = (math.pi*pow(r,2))

        self.mass = mass
        self.density = mass / self.vol

        self.color = []
        for i in range(3):
            self.color.append(random.randint(128,255))

    def move(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt


class nSim_app:
    def __init__(self):
        self.screen_size = (1024,768)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('N-Body Sim')

        self.background = pygame.Surface(self.screen_size).convert()
        self.background.fill((0,0,0))
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        self.body_list = []
        self.clock = pygame.time.Clock()
        self.zoom = 1.0
        self.refresh = True

    def update_bodies(self, dt):
        d=0
        forces = dict.fromkeys(self.body_list)

        for body in self.body_list:
            forces[body] = [0,0]

        for body1 in self.body_list:
            fx = 0
            fy = 0
            for body2 in self.body_list[d:]:
                if body1 != body2:
                    r,theta = nSim.utils.r_theta(body1.pos, body2.pos)
                    m1 = body1.mass
                    m2 = body2.mass

                    f = (G*m1*m2)/pow(r,2)

                    fx += abs(math.cos(theta) * f)
                    fy += abs(math.sin(theta) * f)

                    if body1.pos[0] > body2.pos[0]:
                        forces[body1][0] -= fx
                        forces[body2][0] += fx
                    else:
                        forces[body1][0] += fx
                        forces[body2][0] -= fx

                    if body1.pos[1] > body2.pos[1]:
                        forces[body1][1] -= fy
                        forces[body2][1] += fy
                    else:
                        forces[body1][1] += fy
                        forces[body2][1] -= fy

            d += 1


        for body in self.body_list:
            [fx,fy] = forces[body]
            ax = fx * body.mass
            ay = fy * body.mass

            dvx = ax * dt
            dvy = ay * dt

            body.vel[0] += dvx
            body.vel[1] += dvy

            body.move(dt)

        i = 0

        while i < len(self.body_list):
            body1 = self.body_list[i]
            rem = []
            for body2 in self.body_list:
                if body1 != body2:
                    if nSim.utils.collision(body1.pos,body1.r,body2.pos,body2.r):
                        rem.append(body2)

                        m1x = body1.mass * body1.vel[0]
                        m1y = body1.mass * body1.vel[1]
                        m2x = body2.mass * body2.vel[0]
                        m2y = body2.mass * body2.vel[1]

                        mx = m1x + m2x
                        my = m1y + m2y

                        body1.density = ((body1.density * body1.vol) + (body2.density*body2.vol))/(body1.vol+body2.vol)
                        body1.vol += body2.vol
                        body1.mass += body2.mass
                        body1.r = round(math.sqrt(body1.mass / (math.pi * body1.density)))

                        vx = mx / body1.mass
                        vy = my / body1.mass

                        body1.vel = [vx,vy]
            for r in rem:
                self.body_list.remove(r)

            i += 1

    def draw_bodies(self):
        if self.refresh:
            self.screen.blit(self.background, (0, 0))
        for body in self.body_list:
            pix = nSim.utils.pos_to_pix(body.pos, self.screen_size, self.zoom)
            if pix[0] > self.screen_size[0]+100 or pix[0] < -100:
                continue
            if pix[1] > self.screen_size[1]+100 or pix[1] < -100:
                continue
            pygame.draw.circle(self.screen, body.color, pix, round(body.r * self.zoom))

        pygame.display.flip()

    def run(self):
        dt = 60
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        can_add = False
                        pix = pygame.mouse.get_pos()
                        pos = nSim.utils.pix_to_pos(pix,self.screen_size,self.zoom)
                        self.body_list.append(body(pos,15,1000000))
                    elif event.button == 4:
                        self.zoom *= 2
                    elif event.button == 5:
                        self.zoom /= 2
                elif event.type == KEYDOWN:
                    if event.key == K_d:
                        self.refresh = not self.refresh
                    elif event.key == K_c:
                        self.body_list = []

            self.update_bodies(1/dt)
            self.draw_bodies()