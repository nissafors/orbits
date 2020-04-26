"""zoomsprite.py: Create and group celestial body sprites for PyGame."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


import pygame, math, datetime, types
from keplerorbit import KeplerOrbit

class AbstractZoomSprite(pygame.sprite.Sprite):
    """Base class for zoomable sprites."""

    def __init__(self, zoom=1, origo=(0, 0)):
        """Create a new AbstractZoomSprite.
        
        Args:
            zoom (float): Zoom factor.
            origo (int, int): Coordinate system center.
        """
        self._zoom = zoom
        self._origo = origo
        super().__init__()

    def redraw(self):
        """Override this method to perform a redraw of your sprite when zoom or origo changes."""
        pass

    @property
    def zoom(self):
        """Return current zoom factor."""
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        """Set new zoom factor."""
        self._zoom = value
        self.redraw()

    @property
    def origo(self):
        return self._origo

    @origo.setter
    def origo(self, value):
        self._origo = value
        self.redraw()


class AbstractCelestialBody(AbstractZoomSprite):
    """Base class for celestial body sprites.

    Class members:
        referenceRadius (int): Radius in pixels corresponding to a relative radius of one.
    """
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
        self.redraw()

    def redraw(self):
        """Update sprite drawing of a celestial body."""
        r = max(self.minRadius, round(self.radius * AbstractCelestialBody.referenceRadius * self.zoom))
        side = r * 2
        if len(self.rings) > 0:
            side = max(r + 1, math.ceil(self.rings[-1] * 2 * r))
        self.image = pygame.Surface([side, side])
        transparent = (0, 0, 0) if self.color == (0xFF, 0xFF, 0xFF) else (0xFF, 0xFF, 0xFF)
        self.image.fill(transparent)
        self.image.set_colorkey(transparent)
        pygame.draw.circle(self.image, self.color, (side // 2, side // 2), r)
        for ring in self.rings:
            ring = max(r + 1, round(ring * r))
            width = 0 if ring == r + 1 else 1
            pygame.draw.ellipse(self.image, self.color, (side // 2 - ring, side // 2 - max(1, r // 2), ring * 2, r), width)
        self.rect = self.image.get_rect()


class Sun(AbstractCelestialBody):
    """The sun, centered in the solar system."""

    def __init__(self, radius, color, minRadius):
        """Create a new sun."""
        super().__init__(radius, color, minRadius=minRadius)

    def update(self, *args):
        """Update sun position and size on screen."""
        x0, y0 = self.origo
        self.rect.x = x0 - self.rect.width // 2
        self.rect.y = y0 - self.rect.height // 2


class Planet(AbstractCelestialBody):
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
        x0, y0 = self.origo
        self.orbit.updatePosition(Planet.time)
        x, y = self.orbit.getCartesianPosition()
        x = x * self.zoom // Planet.scale
        y = -y * self.zoom // Planet.scale # Minus y to convert cartesian coordinate to point on screen
        self.rect.x = x - self.rect.width // 2 + x0
        self.rect.y = y - self.rect.height // 2 + y0


class OrbitEllipse(AbstractZoomSprite):
    """Trace an orbit and draw the resulting ellipse.
    
    Class members:
        scale (int): The orbital distance to the central body in m divided by this number gives the distance to origo in pixels when zoom is 1.
    """
    scale = 1e10

    def __init__(self, orbit, color, nSamples=300):
        """Create a new OrbitEllipse.
        
        Args:
            orbit (KeplerOrbit): The orbit to trace.
            color (int, int, int): RGB color of ellipse.
            nSamples (int): Number of orbit coordinates used as vertices in trace. More is smoother but slower.
        """
        super().__init__()
        self.orbit = orbit
        self.color = color
        self.nSamples = nSamples
        self.vertices = []
        self.createVertexList()
        self.redraw()

    def createVertexList(self):
        """Trace orbit and save coordinates to a list."""
        self.vertices.clear()
        delta = datetime.timedelta(0)
        timeStep = datetime.timedelta(seconds=self.orbit.T / self.nSamples)
        for _ in range(self.nSamples):
            self.orbit.updatePosition(self.orbit.epoch + delta)
            x, y = self.orbit.getCartesianPosition()
            self.vertices.append((x, -y))
            delta += timeStep

    def redraw(self):
        """Draw the ellipse and set rect coordinates."""
        width, height = pygame.display.get_surface().get_size()
        x0, y0 = width // 2, height // 2
        self.image = pygame.Surface([width, height])
        transparent = (0, 0, 0) if self.color == (0xFF, 0xFF, 0xFF) else (0xFF, 0xFF, 0xFF)
        self.image.fill(transparent)
        self.image.set_colorkey(transparent)
        points = []
        for x, y in self.vertices:
            points.append((self.zoom * x // self.scale + x0, self.zoom * y // self.scale + y0))
        self.rect = pygame.draw.polygon(self.image, self.color, points, 1)
        self.rect.x = self.rect.y = 0


class ZoomGroup(pygame.sprite.OrderedUpdates):
    """Container of sprites that can bulk-update all it's AbstractZoomSprites."""

    def __init__(self, zoom=1, origo=(0, 0)):
        """Create a new zoomGroup.
        
        Args:
            zoom (float): Zoom factor.
            origo (int, int): Coordinate system center.
        """
        self._zoom = zoom
        self._origo = origo
        super().__init__()

    def add(self, *sprites):
        """Add sprites to container. For all AbstractZoomSprite:s, set zoom and origo."""
        for sprite in sprites:
            if isinstance(sprite, AbstractZoomSprite):
                sprite.zoom = self._zoom
                sprite.origo = self._origo
        super().add(*sprites)

    @property
    def zoom(self):
        """Return current zoom factor."""
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        """Set new zoom value and update all contained AbstractZoomSprite:s."""
        self._zoom = value
        for sprite in self:
            if isinstance(sprite, AbstractZoomSprite):
                sprite.zoom = value

    @property
    def origo(self):
        """Return current origo."""
        return self._origo

    @origo.setter
    def origo(self, value):
        """Set new origo and update all contained AbstractZoomSprite:s."""
        self._origo = value
        for sprite in self:
            if isinstance(sprite, AbstractZoomSprite):
                sprite.origo = value


class PlanetGroup(ZoomGroup):
    """Container of sprites with access to Planet orbits in the order they were added."""

    def __init__(self, *sprites):
        """Create a new PlanetGroup."""
        self.orbits = []
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
            if isinstance(sprite, Planet):
                self.orbits.append(types.SimpleNamespace(name=sprite.name, orbit=sprite.orbit))
        super().add(*sprites)


if __name__ == "__main__":
    print("Warning: zoomsprite.py is not intended to run stand-alone.")
