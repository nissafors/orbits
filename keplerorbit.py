"""keplerorbit.py: Describe planetary orbits using Kepler's methods."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


import math
import datetime

class KeplerOrbit:
    """Calculate planetary orbits."""
    _maxIterations = 100
    _accuracy = 0.0000000001

    def __init__(self, e=0.0167086, a=149.6E9, T=(365.256363004 * 24 * 60 * 60), O=(174.9 * math.pi / 180), o=(288.1 * math.pi / 180), M=(358.617 * math.pi / 180), my=1.327124400189e20):
        """Initialize a new orbit. Earth data is used as default values.

        Members:
        epoch (datetime.datetime): Reference time in terrestrial time. Default is J2000.
        f (float): True anomaly in radians.
        r (float): Distance to central body in m.
        v (float): Speed in m/s.
        
        Args:
        e (float): Eccentricity.
        a (int): Semi-major axis in m.
        T (float): Orbital period in s.
        O (float): Longitude of ascending node in radians.
        o (float): Argument of periapsis in radians.
        M (float): Mean anomaly at epoch in radians.
        my (float): Standard gravitational parameter for the central body. Default value is my for the sun.
        """
        self.e = e
        self.a = a
        self.T = T
        self.O = O
        self.o = o
        self.M = M
        self.my = my
        self.epoch = datetime.datetime(2000, 1, 1, 12)
        self.f, self.r, self.v = None, None, None
        self.updatePosition(self.epoch) # Initialize f, r and v

    def updatePosition(self, time):
        """update the planetary position for given time.
        
        Args:
            time (datetime.datetime): Date and time for the position to update to.
        """
        t = (time - self.epoch).total_seconds()
        M = self._getMeanAnomaly(t) + self.M
        E = self._getEccentricAnomaly(M)
        self.f = self._getTrueAnomaly(E)
        self.r = self._getDistance(E)
        self.v = self._getSpeed()

    def getCartesianPosition(self):
        """Return the position relative to the central body in cartesian coordinates."""
        phi = self.f + self.O + self.o
        x = self.r * math.cos(phi)
        y = self.r * math.sin(phi)
        return (x, y)

    def _getSpeed(self):
        return math.sqrt(self.my * (2 / self.r - 1 / self.a))

    def _getEccentricAnomaly(self, M):
        """Return eccentric anomly given mean anomaly M and the eccentricity e."""
        prevE = M
        iterations = 0
        while (True):
            E = M + self.e * math.sin(prevE)
            if (math.isclose(E, prevE, abs_tol=KeplerOrbit._accuracy) or iterations > KeplerOrbit._maxIterations):
                return E
            prevE = E

    def _getTrueAnomaly(self, E):
        """Return the true anomaly given the eccentric anomaly E."""
        return 2 * math.atan(math.sqrt((1 + self.e) / (1 - self.e)) * math.tan(E / 2))

    def _getDistance(self, E):
        """Return the distance from the main body given the eccentric anomaly E."""
        return self.a * (1 - self.e * math.cos(E))

    def _getMeanAnomaly(self, t):
        """Return the mean anomaly given the time t seconds past perihelion."""
        return 2 * math.pi * t / self.T


if __name__ == "__main__":
    # Demo: Calculate aphelion and perihelion distances and plot the orbit for Earth.
    import matplotlib.pyplot as plt
    orbit = KeplerOrbit()

    # Loop through orbit and sample coordinates every 6th hour.
    # Save closest and farthest distance from the sun and speed at those points.
    minDistance, maxDistance = math.inf, 0
    coordinates = list()
    time = orbit.epoch
    orbitCompleteTime = time + datetime.timedelta(seconds=orbit.T)
    perihelionSpeed, aphelionSpeed = 0, 0
    while time < orbitCompleteTime:
        time += datetime.timedelta(hours=6)
        orbit.updatePosition(time)
        tmpMin, tmpMax = minDistance, maxDistance
        minDistance = min(orbit.r, minDistance)
        maxDistance = max(orbit.r, maxDistance)
        if minDistance != tmpMin:
            perihelionSpeed = orbit.v
        elif maxDistance != tmpMax:
            aphelionSpeed = orbit.v
        coordinates.append(orbit.getCartesianPosition())

    # Print apsis info
    print(f"Perihelion - Speed: {round(perihelionSpeed / 1000, 3):.3f} km/s, Distance: {(minDistance / 1000):.4e} km")
    print(f"Aphelion - Speed: {round(aphelionSpeed / 1000, 3):.3f} km/s, Distance: {(maxDistance / 1000):.4e} km")
    
    # Plot orbit
    x, y = zip(*coordinates)
    plt.plot(x, y)
    plt.plot(0, 0, marker='o')
    plt.axis('equal')
    plt.title("Earth's orbit")
    plt.show()
