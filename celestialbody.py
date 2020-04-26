"""celestialbody.py: Create and group celestial body sprites for PyGame."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


import pygame, math, datetime, types
from keplerorbit import KeplerOrbit

class CelestialBody(pygame.sprite.Sprite):
    """Base class for celestial body sprites.

    Class members:
        origo (int, int): Screen coordinats x0 and y0 to origo.
        zoom (int): Zoom factor.
        referenceRadius (int): Radius in pixels corresponding to a relative radius of one.
    """
    origo = (0, 0)
    referenceRadius = 15

    def __init__(self, radius, color, rings=[], minRadius=1):
        """Create a new Planet.
        
        Args:
            orbit (KeplerOrbit): Description of orbit.
            radius (float): Radius of planet relative to referenceRadius.
            color (int, int, int): RGB color.
            rings (list of float): Radii relative to the radius of rings around the planet. The largest ring must be last in list.
            minRadius (int): Minimum radius of on-screen planet.
        """
        super().__init__()
        self.radius = radius
        self.color = color
        self.rings = rings
        self.minRadius = minRadius
        self.zoom = 1
        self.drawCelestialBody()

    def drawCelestialBody(self):
        """Update sprite drawing of a celestial body."""
        r = max(self.minRadius, round(self.radius * CelestialBody.referenceRadius * self.zoom))
        side = r * 2
        if len(self.rings) > 0:
            side = max(r + 1, math.ceil(self.rings[-1] * 2 * r))
        self.image = pygame.Surface([side, side])
        white = (0xFF, 0xFF, 0xFF)
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.circle(self.image, self.color, (side // 2, side // 2), r)
        for ring in self.rings:
            ring = max(r + 1, round(ring * r))
            width = 0 if ring == r + 1 else 1
            pygame.draw.ellipse(self.image, self.color, (side // 2 - ring, side // 2 - max(1, r // 2), ring * 2, r), width)
        self.rect = self.image.get_rect()


class Sun(CelestialBody):
    """The sun, centered in the solar system."""

    def __init__(self, radius, color, minRadius):
        """Create a new sun."""
        super().__init__(radius, color, minRadius=minRadius)

    def update(self, *args):
        """Update sun position and size on screen."""
        x0, y0 = Planet.origo
        self.rect.x = x0 - self.rect.width // 2
        self.rect.y = y0 - self.rect.height // 2


class Planet(CelestialBody):
    """A planet sprite in a Kepler orbit around origo.
    
    Class members:
        time (datetime.datetime): Date and time in terrestrial time.
        scale (int): The orbital distance to the central body in m divided by this number gives the distance to origo in pixels when zoom is 1.
    """
    time = datetime.datetime(2000, 1, 1, 12)
    scale = 1e10

    def __init__(self, name, orbit, radius, color, rings=[], minRadius=1):
        """Create a new Planet.
        
        Args:
            name (string): The name of the planet.
            orbit (KeplerOrbit): Description of orbit.
        """
        super().__init__(radius, color, rings, minRadius)
        self.name = name
        self.orbit = orbit

    def update(self, *args):
        """Update screen coordinates to correspond to planet position at Planet.time."""
        x0, y0 = CelestialBody.origo
        self.orbit.updatePosition(Planet.time)
        x, y = self.orbit.getCartesianPosition()
        x = x * self.zoom // Planet.scale
        y = -y * self.zoom // Planet.scale # Minus y to convert cartesian coordinate to point on screen
        self.rect.x = x - self.rect.width // 2 + x0
        self.rect.y = y - self.rect.height // 2 + y0


class PlanetGroup(pygame.sprite.Group):
    """Container of sprites with access to Planet orbits in the order they were added."""

    def __init__(self, *sprites):
        """Create a new PlanetGroup."""
        self.orbits = []
        self._zoom = 1
        super().__init__()

    def add(self, *sprites):
        """Add any type of sprites. If the sprite is a Planet it's orbit is saved together with it's
            name in the orbits list. Example usage:
                s = pygame.sprite.Sprite()
                p1, p2 = Planet("Mars", mOrbit, *args), Planet("Jupiter", jOrbit, *args)
                pg = PlanetGroup(p1, s, p2)
                marsName, marsOrbit = pg.orbits[0].name, pg.orbits[0].orbit
                jupiterName, jupiterOrbit = pg.orbits[1].name, pg.orbits[1].orbit
        """
        for sprite in sprites:
            sprite.zoom = self._zoom
            if isinstance(sprite, Planet):
                self.orbits.append(types.SimpleNamespace(name=sprite.name, orbit=sprite.orbit))
        super().add(*sprites)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        """Change zoom and update planet drawings."""
        self._zoom = value
        for sprite in self:
            if isinstance(sprite, CelestialBody):
                sprite.zoom = value
                sprite.drawCelestialBody()


if __name__ == "__main__":
    print("Warning: celestialbody.py is not intended to run stand-alone.")
