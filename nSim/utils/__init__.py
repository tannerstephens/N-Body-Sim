import math

def r_theta(pos1, pos2):
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]

    r = math.sqrt(pow(dx,2) + pow(dy,2))

    if dx == 0:
        theta = 0
    else:
        theta = math.atan(dy/dx)

    return r,theta

def pos_to_pix(pos, screen_size, zoom):
    cx, cy = screen_size[0]/2, screen_size[1]/2

    x,y = pos

    x = x*zoom + cx
    y = y*zoom + cy

    return (round(x),round(y))

def pix_to_pos(pix, screen_size, zoom):
    cx, cy = screen_size[0]/2, screen_size[1]/2

    x,y = pix

    x = (x - cx) / zoom
    y = (y - cy) / zoom

    return (x,y)


def collision(pos1, r1, pos2, r2):
    r,theta = r_theta(pos1,pos2)
    dr = r1+r2

    return dr > r

