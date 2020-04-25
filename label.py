"""label.py: Create and group simple labels for PyGame."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


class Label:
    """Renders and positions a text label in a PyGame app."""

    def __init__(self, font, color, text="", top=0, left=0, bottom=None, right=None):
        """Create a new Label. Positions will not be set until updatePosition() is called.
        
        Args:
            font (Font): Pygame font object.
            color (int, int, int): RGB color.
            text (string): The text to render.
            top (int): Distance from top of screen. Ignored if bottom is set.
            left (int): Distance from left side of screen. Ignored if right is set.
            bottom (int): Distance from bottom of screen. Overrides top if not set to None.
            right (int): Distance from right side of screen. Overrides top if not set to None.
        """
        self.text = text
        self.font = font
        self.color = color
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
        self.renderLabel()

    def renderLabel(self):
        """Render label from string."""
        self.render = self.font.render(self.text, True, self.color)
        self.rect = self.render.get_rect()

    def udpatePosition(self, screenSize):
        """Update on-screen label position.
        
        Args:
            screenSize (int, int): Width and height of display area.
        """
        w, h = screenSize
        if self.bottom != None:
            self.rect.bottom = h - self.bottom
        else:
            self.rect.top = self.top
        if self.right != None:
            self.rect.right = w - self.right
        else:
            self.rect.left = self.left


class LabelGroup:
    """Class to group info text labels."""

    def __init__(self, display):
        """Create a new LabelGroup.

        Args:
            display (bool): Labels in group are visible if True, invisible otherwise.
        """
        self.display = display
        self.labels = dict()

    def add(self, key, label):
        """Add a label identified by key to the group."""
        self.labels[key] = label

    def get(self, key):
        """Get the label with given key."""
        return self.labels[key]

    def __iter__(self):
        """Make LabelGroup iterable."""
        return iter(self.labels.values())
