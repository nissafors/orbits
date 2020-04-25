"""sciformat.py: Print scientific notation with more control."""

__author__ = "Andreas Andersson"
__copyright__ = "Copyright 2020, Andreas Andersson"
__contact__ = "andreas.andersson@tutanota.com"


import math

class SciFormat:
    """Pretty print in scientific notation with utf-8 superscript, e.g. 1.23x10⁻⁵."""

    superscriptMap = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻"}

    def __init__(self, num):
        """Create a new SciFormat.
        
        Args:
            num (int or float): The number to format.
        """
        self.num = num
        self.magnitude = math.floor(math.log10(num))
        self.base = self.num / (10**self.magnitude)

    def __format__(self, format):
        """Return num as a string formatted according to given format string.
        
        Args:
            format (string): Format string given as '[magnitude limit][.[0]precision]'
                    - Magnitude limit is the lowest magnitude that should be returned in scientific format.
                    If the magnitude is lower than the limit the number will be returned rounded according
                    to precision (if given, otherwise it will be returned as is).
                    - A 0 after the . and before precision enables fill to precision.
                    - Precision is the number of digits given after the decimal point. If precision is 0
                    no decimal point will be printed.
                Examples:
                    n = SciFormat(12345)
                    print(f"{n}")               -> 1.2345x10⁴
                    print(f"{n:.2}")            -> 1.23x10⁴
                    print(f"{n:.06}")           -> 1.234500x10⁴
                    print(f"{n:.0}")            -> 1x10⁴
                    n = SciFormat(123.456)
                    print(f"{n:3.2}")           -> 123.45
                    print(f"{n:2.2}")           -> 1.23x10²
                    print(f"{n:3.05}")          -> 123.45600
                    n = SciFormat(0.00012345)
                    print(f"{n}")               -> 1.2345x10⁻⁴
                    print(f"{n:4.2}")           -> 1.23x10⁻⁴
                    print(f"{n:5.5}")           -> 0.00012
        """
        magLim = 0
        precision = math.inf
        fill = False
        fSplit = format.split('.')
        if (fSplit[0]) != '':
            magLim = int(fSplit[0])
        if len(fSplit) == 2:
            pStr = fSplit[1]
            if pStr[0] == '0' and len(pStr) > 1:
                fill = True
                pStr = pStr[1:]
            precision = int(pStr)
        result = ""
        if abs(self.magnitude) < magLim:
            num = self.num if precision == math.inf else round(self.num, precision)
            if precision == 0:
                result = str(int(num))
            elif fill:
                result = str(num)
                if not '.' in result:
                    result += '.'
                result = result.ljust(self.magnitude + precision + 2, '0')
            else:
                result = str(num)
        else:
            base = round(self.base, precision) if precision != math.inf else self.base
            if base.is_integer() and precision == 0:
                base = int(base)
            pad = (2 if precision > 0 and fill else 0) + (precision if fill else 0)
            exp = "".join(map(lambda x: SciFormat.superscriptMap[x], str(self.magnitude)))
            result = f"{str(base).ljust(pad, '0')}x10{exp}"
        return result


if __name__ == "__main__":
    print("Warning: sciformat.py is not intended to run stand-alone.")
