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
        self.screen_size = (1600,900)
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
        d=1
        forces = dict.fromkeys(self.body_list)

        for body in self.body_list:
            forces[body] = [0,0]

        for body1 in self.body_list:
            for body2 in self.body_list[d:]:
                if body1 != body2:
                    r,theta = nSim.utils.r_theta(body1.pos, body2.pos)
                    m1 = body1.mass
                    m2 = body2.mass

                    f = (G*m1*m2)/pow(r,2)

                    fx = abs(math.cos(theta) * f)
                    fy = abs(math.sin(theta) * f)

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
            ax = fx / body.mass
            ay = fy / body.mass

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
                        m1x = body1.mass * body1.vel[0]
                        m1y = body1.mass * body1.vel[1]
                        m2x = body2.mass * body2.vel[0]
                        m2y = body2.mass * body2.vel[1]

                        mx = m1x + m2x
                        my = m1y + m2y

                        if body1.mass > body2.mass:
                            rem.append(body2)
                            body1.density = ((body1.density * body1.vol) + (body2.density*body2.vol))/(body1.vol+body2.vol)
                            body1.vol += body2.vol
                            body1.mass += body2.mass
                            body1.r = round(math.sqrt(body1.mass / (math.pi * body1.density)))

                            vx = mx / body1.mass
                            vy = my / body1.mass

                            body1.vel = [vx,vy]
                        else:
                            rem.append(body1)
                            body2.density = ((body1.density * body1.vol) + (body2.density*body2.vol))/(body1.vol+body2.vol)
                            body2.vol += body1.vol
                            body2.mass += body1.mass
                            body2.r = round(math.sqrt(body2.mass / (math.pi * body2.density)))

                            vx = mx / body2.mass
                            vy = my / body2.mass

                            body2.vel = [vx,vy]


            for r in rem:
                self.body_list.remove(r)

            i += 1

    def draw_bodies(self,r):
        self.screen.blit(self.background, (0, 0))
        for body in self.body_list:
            pix = nSim.utils.pos_to_pix(body.pos, self.screen_size, self.zoom)
            if pix[0] > self.screen_size[0] + round(body.r * self.zoom) or pix[0] < - round(body.r * self.zoom):
                continue
            if pix[1] > self.screen_size[1] + round(body.r * self.zoom) or pix[1] < - round(body.r * self.zoom):
                continue
            pygame.draw.circle(self.screen, body.color, pix, round(body.r * self.zoom))

        pix = pygame.mouse.get_pos()
        s = pygame.Surface(self.screen_size)
        s.fill((0,0,0))
        s.set_colorkey((0,0,0))
        pygame.draw.circle(s, (255,255,255), pix, round(r * self.zoom))
        s.set_alpha(25)
        self.screen.blit(s,(0,0))

    def run(self):
        dt = 10
        zoom_on = False
        r = 16
        drawing = False
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        drawing = True
                        pix = pygame.mouse.get_pos()
                        start_pos = nSim.utils.pix_to_pos(pix,self.screen_size,self.zoom)
                    elif event.button == 4:
                        if zoom_on:
                            self.zoom *= 2
                        else:
                            r *= 2
                    elif event.button == 5:
                        if zoom_on:
                            self.zoom /= 2
                        else:
                            r /= 2
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        drawing = False
                        pix = pygame.mouse.get_pos()
                        end_pos = nSim.utils.pix_to_pos(pix,self.screen_size,self.zoom)

                        v_x = (start_pos[0] - end_pos[0]) * .25
                        v_y = (start_pos[1] - end_pos[1]) * .25

                        vel = [v_x,v_y]

                        vol = math.pi * pow(r,2)

                        b = body(start_pos, r, 100000000000*pow(vol,.7))

                        b.vel = vel

                        self.body_list.append(b)



                elif event.type == KEYDOWN:
                    if event.key == K_d:
                        self.refresh = not self.refresh
                    elif event.key == K_c:
                        self.body_list = []
                    elif event.key == K_SPACE:
                        if dt == 0:
                            dt = 1/60
                        else:
                            dt = 0
                    elif event.key == K_z:
                        zoom_on = not zoom_on


            self.update_bodies(dt)
            self.draw_bodies(r)

            if drawing:
                pygame.draw.line(self.screen, (255,255,255), nSim.utils.pos_to_pix(start_pos,self.screen_size,self.zoom), pygame.mouse.get_pos())

            pygame.display.flip()