"""orbanimation.py: Animate the orbits of the solar system."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


import pygame
from solarsystem import SolarSystem
from celestialbody import Planet

# Init game
pygame.init()
clock = pygame.time.Clock()
solarSystem = SolarSystem()
pygame.display.set_caption("Our Solar System")

# Game loop
while solarSystem.isAlive:
    for event in pygame.event.get():
        solarSystem.eventHandler(event)

    solarSystem.update()
    pygame.display.flip()
    clock.tick(solarSystem.fps)

pygame.quit()