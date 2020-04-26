"""solarsystem.py: A 2D solar system for PyGame."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


import pygame, math, datetime
from keplerorbit import KeplerOrbit
from zoomsprite import AbstractCelestialBody, Planet, Sun, PlanetGroup
from label import Label, LabelGroup
from sciformat import SciFormat
from dateutil.relativedelta import relativedelta
import tkinter as tk
from tkinter import simpledialog, messagebox

class SolarSystem:
    """Description of a 2D solar system for PyGame."""

    # Constants
    SPEED = [
        (relativedelta(years=-100), "-100 y/s"),
        (relativedelta(years=-50), "-50 y/s"),
        (relativedelta(years=-10), "-10 y/s"),
        (relativedelta(years=-5), "-5 y/s"),
        (relativedelta(years=-1), "-1 y/s"),
        (relativedelta(months=-6), "-6 mos/s"),
        (relativedelta(months=-1), "-1 mo/s"),
        (relativedelta(weeks=-1), "-1 w/s"),
        (relativedelta(days=-1), "-1 d/s"),
        (relativedelta(hours=-1), "-1 h/s"),
        (relativedelta(minutes=-1), "-1 min/s"),
        (relativedelta(seconds=-1), "-1 s/s"),
        (relativedelta(seconds=0), "Time freeze"),
        (relativedelta(seconds=1), "Real time"),
        (relativedelta(minutes=1), "1 min/s"),
        (relativedelta(hours=1), "1 h/s"),
        (relativedelta(days=1), "1 d/s"),
        (relativedelta(weeks=1), "1 w/s"),
        (relativedelta(months=1), "1 mo/s"),
        (relativedelta(months=6), "6 mos/s"),
        (relativedelta(years=1), "1 y/s"),
        (relativedelta(years=5), "5 y/s"),
        (relativedelta(years=10), "10 y/s"),
        (relativedelta(years=50), "50 y/s"),
        (relativedelta(years=100), "100 y/s")
    ]
    FREEZE_INDEX = 12 # SPEED index of time freeze
    MAX_ZOOM = 170
    MIN_ZOOM = 0.01
    JUPITER_RADIUS_AT_ZOOM_ONE = 15
    EPOCH = datetime.datetime(year=2000, month=1, day=1, hour=12)
    UP, DOWN = 1, -1
    "Label texts"
    HELP_LBL = "F1: Help"
    ZOOM_LBL = "Zoom: {}%"
    SPEED_LBL = "Speed: {}"
    TIME_LBL = "Time: {}"
    PAUSED_LBL = "Paused at: {}"
    ZOOM_HELP_LBL = "UP/DOWN: Zoom"
    SPEED_HELP_LBL = "LEFT/RIGHT: Speed"
    PAUSE_HELP_LBL = "SPACE: Pause"
    ORBIT_HELP_LBL = "1-9: Select planet"
    SET_DATE_HELP_LBL = "F2: Set date"
    PLANET_INFO_LBL = "{}"
    DISTANCE_INFO_LBL = "Distance to sun: {:.02} km"
    SPEED_INFO_LBL = "Speed: {:3.02} km/s"
    # Colors
    BACKGROUND = (0, 0, 0)
    SUN = (0xFF, 0xCC, 0x33)
    MERCURY = (0xB5, 0xA7, 0xA7)
    VENUS = (0xDD, 0xD8, 0xD4)
    EARTH = (0x8C, 0xB1, 0xDE)
    MARS = (0xE2, 0x7B, 0x58)
    JUPITER = (0xD3, 0x9C, 0x7E)
    SATURN = (0xA4, 0x9B, 0x72)
    URANUS = (0xBB, 0xE1, 0xE4)
    NEPTUNE = (0x60, 0x81, 0xFF)
    PLUTO = (0xFF, 0xF1, 0xD5)
    TEXT = SUN

    def __init__(self):
        """Create a new SolarSystem."""
        AbstractCelestialBody.referenceRadius = SolarSystem.JUPITER_RADIUS_AT_ZOOM_ONE
        self.screenSize = (800, 600)
        self.fps = 30
        self.zoomStepFactor = 1.1
        self.speedIndex = SolarSystem.FREEZE_INDEX + 6
        self.targetTime =  SolarSystem.EPOCH + SolarSystem.SPEED[self.speedIndex][0]
        self.updateTimeStep()
        self.screen = pygame.display.set_mode(self.screenSize, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
        self.cbSprites = PlanetGroup()
        self.cbSprites.zoom = 1
        self.initCelestialBodies()
        self.paused = False
        self.selectedPlanet = 2
        self.initLabels()
        self.updateLabelPositions()
        self.updateOrigo()
        self.isAlive = True

    def initCelestialBodies(self):
        """Create solar system object sprites."""
        mercuryOrbit = KeplerOrbit(e=0.21, a=57909050000, T=SolarSystem._toSeconds(87.9691), O=SolarSystem._toRadians(48.331), o=SolarSystem._toRadians(29.124), M=SolarSystem._toRadians(174.796))
        mercury = Planet("Mercury", mercuryOrbit, 0.034, SolarSystem.MERCURY)
        venusOrbit = KeplerOrbit(e=0.0068, a=1.08208628e11, T=SolarSystem._toSeconds(224.7), O=SolarSystem._toRadians(76.680), o=SolarSystem._toRadians(54.884), M=SolarSystem._toRadians(50.115))
        venus = Planet("Venus", venusOrbit, 0.085, SolarSystem.VENUS)
        earthOrbit = KeplerOrbit()
        earth = Planet("Earth", earthOrbit, 0.089, SolarSystem.EARTH)
        marsOrbit = KeplerOrbit(e=0.0934, a=2.27942276e11, T=SolarSystem._toSeconds(687.0), O=SolarSystem._toRadians(49.558), o=SolarSystem._toRadians(286.502), M=SolarSystem._toRadians(19.412))
        mars = Planet("Mars", marsOrbit, 0.048, SolarSystem.MARS)
        jupiterOrbit = KeplerOrbit(e=0.0489, a=7.7857e11, T=SolarSystem._toSeconds(4332.59), O=SolarSystem._toRadians(100.464), o=SolarSystem._toRadians(273.867), M=SolarSystem._toRadians(20.020))
        jupiter = Planet("Jupiter", jupiterOrbit, 1.0, SolarSystem.JUPITER)
        saturnOrbit = KeplerOrbit(e=0.0565, a=1.43353e12, T=SolarSystem._toSeconds(10759.22), O=SolarSystem._toRadians(113.665), o=SolarSystem._toRadians(339.392), M=SolarSystem._toRadians(317.020))
        saturn = Planet("Saturn", saturnOrbit, 0.843, SolarSystem.SATURN, [1.3, 1.6, 1.9])
        uranusOrbit = KeplerOrbit(e=0.046381, a=2.87504e12, T=SolarSystem._toSeconds(30688.5), O=SolarSystem._toRadians(74.006), o=SolarSystem._toRadians(96.998857), M=SolarSystem._toRadians(142.2386))
        uranus = Planet("Uranus", uranusOrbit, 0.358, SolarSystem.URANUS, [1.3, 1.6])
        neptuneOrbit = KeplerOrbit(e=0.009456, a=4.50439e12, T=SolarSystem._toSeconds(60182), O=SolarSystem._toRadians(131.784), o=SolarSystem._toRadians(276.336), M=SolarSystem._toRadians(256.228))
        neptune = Planet("Neptune", neptuneOrbit, 0.346, SolarSystem.NEPTUNE)
        plutoOrbit = KeplerOrbit(e=0.2488, a=5.90638e12, T=SolarSystem._toSeconds(90560), O=SolarSystem._toRadians(110.299), o=SolarSystem._toRadians(113.834), M=SolarSystem._toRadians(14.53))
        pluto = Planet("Pluto", plutoOrbit, 0.017, SolarSystem.PLUTO)
        sun = Sun(0.15, self.SUN, 3)
        self.cbSprites.add(mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto, sun)

    def initLabels(self):
        """Create info text labels."""
        font = pygame.font.SysFont("arial", 12, bold=True)
        self.labelGroups = {"static": LabelGroup(True), "help": LabelGroup(False), "state": LabelGroup(True), "realtime": LabelGroup(True)}
        helpLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.HELP_LBL, bottom=10, right=10)
        self.labelGroups["static"].add("help", helpLabel)
        labelHeight = helpLabel.rect.height

        zoomKeysLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.ZOOM_HELP_LBL, top=10, right=10)
        self.labelGroups["help"].add("zoom", zoomKeysLabel)
        speedKeysLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.SPEED_HELP_LBL, top=labelHeight + 10, right=10)
        self.labelGroups["help"].add("speed", speedKeysLabel)
        pauseKeyLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.PAUSE_HELP_LBL, top=labelHeight * 2 + 10, right=10)
        self.labelGroups["help"].add("pause", pauseKeyLabel)
        planetKeysLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.ORBIT_HELP_LBL, top=labelHeight * 3 + 10, right=10)
        self.labelGroups["help"].add("planet", planetKeysLabel)
        setDateLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.SET_DATE_HELP_LBL, top=labelHeight * 4 + 10, right=10)
        self.labelGroups["help"].add("date", setDateLabel)

        timeLabel = Label(font, SolarSystem.TEXT, top=10, left=10)
        self.labelGroups["realtime"].add("time", timeLabel)
        planetInfoLabel = Label(font, SolarSystem.TEXT, top=labelHeight + 10, left=10)
        self.labelGroups["realtime"].add("planetInfo", planetInfoLabel)
        distanceInfoLabel = Label(font, SolarSystem.TEXT, top=labelHeight * 2 + 10, left=10)
        self.labelGroups["realtime"].add("distanceInfo", distanceInfoLabel)
        speedInfoLabel = Label(font, SolarSystem.TEXT, top=labelHeight * 3 + 10, left=10)
        self.labelGroups["realtime"].add("speedInfo", speedInfoLabel)
        self.updateRealtimeLabels()

        zoomLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.ZOOM_LBL.format(SolarSystem._toPercent(self.cbSprites.zoom)), bottom=10, left=10)
        self.labelGroups["state"].add("zoom", zoomLabel)
        speedLabel = Label(font, SolarSystem.TEXT, text=SolarSystem.SPEED_LBL.format(SolarSystem.SPEED[self.speedIndex][1]), bottom=10, left=30 + zoomLabel.rect.width)
        self.labelGroups["state"].add("speed", speedLabel)

    def update(self):
        """Update orbits in game loop."""
        self.screen.fill(SolarSystem.BACKGROUND)
        self.cbSprites.update()
        self.cbSprites.draw(self.screen)
        Planet.time += self.timeStep
        if (self.labelGroups["realtime"].display):
            self.updateRealtimeLabels()
        self.showLabels()
        if (self.speedIndex > SolarSystem.FREEZE_INDEX and Planet.time >= self.targetTime) or (self.speedIndex < SolarSystem.FREEZE_INDEX and Planet.time <= self.targetTime):
            self.targetTimeReached = True
        if self.targetTimeReached:
            # This construction allows for other methods to set targetTimeReached to True
            # so that we'll be able to take immediate action on e.g. speed changes.
            self.updateTimeStep()

    def updateRealtimeLabels(self):
        """Update labels in the realtime group. This is done at every update call."""
        # Time label
        time = ""
        if (self.speedIndex > 7 and self.speedIndex < 17):
            time = Planet.time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time = Planet.time.strftime("%Y-%m-%d")
        text = SolarSystem.PAUSED_LBL if self.paused else SolarSystem.TIME_LBL
        self.labelGroups["realtime"].get("time").text = text.format(time)
        # Planet info
        selected = self.cbSprites.orbits[self.selectedPlanet]
        distance = SciFormat(selected.orbit.r / 1000)
        speed = SciFormat(selected.orbit.v / 1000)
        self.labelGroups["realtime"].get("planetInfo").text = SolarSystem.PLANET_INFO_LBL.format(selected.name)
        self.labelGroups["realtime"].get("distanceInfo").text = SolarSystem.DISTANCE_INFO_LBL.format(distance)
        self.labelGroups["realtime"].get("speedInfo").text = SolarSystem.SPEED_INFO_LBL.format(speed)
        # Render and position
        screenSize = self.screen.get_size()
        for label in self.labelGroups["realtime"]:
            label.renderLabel()
            label.udpatePosition(screenSize)

    def updateTimeStep(self):
        """Set timestep per frame from current speed and fps."""
        self.targetTime = Planet.time + SolarSystem.SPEED[self.speedIndex][0]
        self.timeStep = datetime.timedelta(seconds=(self.targetTime - Planet.time).total_seconds() / self.fps)
        self.targetTimeReached = False

    def updateOrigo(self):
        """Find origo on screen and update sprites."""
        width, height = self.screen.get_size()
        self.cbSprites.origo = (width // 2, height // 2)

    def updateLabelPositions(self, group=None):
        """Set on-screen positions of info text labels."""
        screenSize = self.screen.get_size()
        if group == None:
            for group in self.labelGroups.values():
                for label in group:
                    label.udpatePosition(screenSize)
        else:
            for label in group:
                label.udpatePosition(screenSize)

    def showLabels(self):
        """Print info on screen."""
        for group in self.labelGroups.values():
            if group.display:
                for label in group:
                    self.screen.blit(label.render, label.rect)

    def stepSpeed(self, direction):
        """Step speed in direction.
        
        Args:
            direction (int): 1 is one step up and -1 is one step down.
        """
        if not self.paused:
            self.targetTimeReached = True # Force immediate action on next update()
            newSpeedIndex = self.speedIndex + direction
            if (newSpeedIndex >= 0 and newSpeedIndex < len(SolarSystem.SPEED)):
                self.speedIndex += direction
                self.labelGroups["state"].get("speed").text = SolarSystem.SPEED_LBL.format(SolarSystem.SPEED[self.speedIndex][1])
                self.labelGroups["state"].get("speed").renderLabel()
                self.updateLabelPositions()

    def stepZoom(self, direction):
        """Step zoom in direction.
        
        Args:
            direction (int): 1 is one step up and -1 is one step down.
        """
        factor = 1 / self.zoomStepFactor if direction == SolarSystem.DOWN else self.zoomStepFactor
        newZoom = self.cbSprites.zoom * factor
        if newZoom >= SolarSystem.MIN_ZOOM and newZoom <= SolarSystem.MAX_ZOOM:
            self.cbSprites.zoom = newZoom
            self.labelGroups["state"].get("zoom").text = SolarSystem.ZOOM_LBL.format(SolarSystem._toPercent(self.cbSprites.zoom))
            self.labelGroups["state"].get("zoom").renderLabel()
            self.updateLabelPositions()

    def getUserInputDate(self):
        """Show dialog to get date from user.
        
        Returns:
            datetime or bool: False if cancelled or invalid user input, datetime object otherwise.
        """
        root = tk.Tk().wm_withdraw()
        dateStr = simpledialog.askstring("Set date", "Date (yyy-mm-dd [H[:M[:S]]])", parent=root)
        if dateStr == None:
            return False        
        try:
            time = datetime.datetime.fromisoformat(dateStr)
            return time
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return False

    def eventHandler(self, event):
        """Handle a pygame event.
        
        Args:
            event (Event): The PyGame event to handle.
        """
        if (event.type == pygame.QUIT):
            self.isAlive = False
        elif (event.type == pygame.VIDEORESIZE):
            self.screen = pygame.display.set_mode(event.dict['size'], pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
            self.updateOrigo()
            self.updateLabelPositions()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or (pygame.K_F4 and (event.mod & pygame.KMOD_ALT)):
                self.isAlive = False
            elif event.key == pygame.K_LEFT:
                self.stepSpeed(SolarSystem.DOWN)
            elif event.key == pygame.K_RIGHT:
                self.stepSpeed(SolarSystem.UP)
            elif event.key == pygame.K_UP:
                self.stepZoom(SolarSystem.UP)
            elif event.key == pygame.K_DOWN:
                self.stepZoom(SolarSystem.DOWN)
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
                if self.paused:
                    self.pausIndex = self.speedIndex
                    self.speedIndex = SolarSystem.FREEZE_INDEX
                else:
                    self.speedIndex = self.pausIndex
                self.targetTimeReached = True
            elif event.key == pygame.K_F1:
                self.labelGroups["help"].display = not self.labelGroups["help"].display
            elif event.key in range(pygame.K_1, pygame.K_9 + 1):
                self.selectedPlanet = event.key - pygame.K_1
            elif event.key == pygame.K_F2:
                time = self.getUserInputDate()
                if isinstance(time, datetime.datetime):
                    Planet.time = time

    @staticmethod
    def _toRadians(degrees):
        """Convert degrees to radians.

        Args:
            degrees (float): Angle expressed in degrees.
        
        Returns:
            float: Angle expressed in radians.
        """
        return degrees * math.pi / 180

    @staticmethod
    def _toSeconds(days):
        """Convert days to seconds.
        
        Args:
            days (int): Time expressed in days.

        Returns:
            float: Time expressed in seconds.
        """
        return days * 86400

    @staticmethod
    def _toPercent(value, precision=0):
        """Convert to percent.
        
        Args:
            value (float): The value to convert.
            precision: The precision which to round the result to to.

        Returns:
            float or int: Value expressed in percent. Given as int if precision is 0.
        """
        percent = round(value * 100, precision)
        if precision == 0:
            return int(percent)
        return percent


if __name__ == "__main__":
    print("Warning: solarsystem.py is not intended to run stand-alone.")
