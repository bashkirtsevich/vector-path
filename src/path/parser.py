import re

from . import path
from .point import Point

COMMANDS = set("MmZzLlHhVvCcSsQqTtAa")
UPPERCASE = set("MZLHVCSQTA")

COMMAND_RE = re.compile("([MmZzLlHhVvCcSsQqTtAa])")
FLOAT_RE = re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")


def _tokenize_path(pathdef):
    for x in COMMAND_RE.split(pathdef):
        if x in COMMANDS:
            yield x
        for token in FLOAT_RE.findall(x):
            yield token


def parse_path(pathdef, current_pos=None):
    current_pos = current_pos or Point(0, 0)
    # In the SVG specs, initial movetos are absolute, even if
    # specified as "m". This is the default behavior here as well.
    # But if you pass in a current_pos variable, the initial moveto
    # will be relative to that current_pos. This is useful.
    elements = list(_tokenize_path(pathdef))
    # Reverse for easy use of .pop()
    elements.reverse()

    segments = path.Path()
    start_pos = None
    command = None

    absolute = None

    while elements:
        if elements[-1] in COMMANDS:
            # New command.
            last_command = command  # Used by S and T
            command = elements.pop()
            absolute = command in UPPERCASE
            command = command.upper()
        else:
            # If this element starts with numbers, it is an implicit command
            # and we don"t change the command. Check that it"s allowed:
            if command is None:
                raise ValueError("Unallowed implicit command in %s, position %s" % (
                    pathdef, len(pathdef.split()) - len(elements)))

            last_command = command  # Used by S and T

        if command == "M":
            # Moveto command.
            x = elements.pop()
            y = elements.pop()

            pos = Point(float(x), float(y))

            if absolute:
                current_pos = pos
            else:
                current_pos += pos

            segments.append(path.Move(current_pos.c))
            # when M is called, reset start_pos
            # This behavior of Z is defined in path spec:
            # http://www.w3.org/TR/SVG/paths.html#PathDataClosePathCommand
            start_pos = current_pos

            # Implicit moveto commands are treated as lineto commands.
            # So we set command to lineto here, in case there are
            # further implicit commands after this moveto.
            command = "L"

        elif command == "Z":
            # Close path
            if current_pos != start_pos:
                segments.append(path.Line(current_pos.c, start_pos.c))

            segments.closed = True
            current_pos = start_pos
            start_pos = None
            command = None  # You can"t have implicit commands after closing.

        elif command == "L":
            x = elements.pop()
            y = elements.pop()

            pos = Point(float(x), float(y))

            if not absolute:
                pos += current_pos

            segments.append(path.Line(current_pos.c, pos.c))
            current_pos = pos

        elif command == "H":
            x = elements.pop()
            pos = Point(float(x), current_pos.y)

            if not absolute:
                pos += Point(current_pos.x, 0)

            segments.append(path.Line(current_pos.c, pos.c))
            current_pos = pos

        elif command == "V":
            y = elements.pop()
            pos = Point(current_pos.x, float(y))

            if not absolute:
                pos += Point(0, current_pos.y)

            segments.append(path.Line(current_pos.c, pos.c))
            current_pos = pos

        elif command == "C":
            control1 = Point(float(elements.pop()), float(elements.pop()))
            control2 = Point(float(elements.pop()), float(elements.pop()))
            end = Point(float(elements.pop()), float(elements.pop()))

            if not absolute:
                control1 += current_pos
                control2 += current_pos
                end += current_pos

            segments.append(path.CubicBezier(current_pos.c, control1.c, control2.c, end.c))
            current_pos = end

        elif command == "S":
            # Smooth curve. First control point is the "reflection" of
            # the second control point in the previous path.

            if last_command not in "CS":
                # If there is no previous command or if the previous command
                # was not an C, c, S or s, assume the first control point is
                # coincident with the current point.
                control1 = current_pos
            else:
                # The first control point is assumed to be the reflection of
                # the second control point on the previous command relative
                # to the current point.
                control1 = current_pos + current_pos - Point(segments[-1].control2.real, segments[-1].control2.imag)

            control2 = Point(float(elements.pop()), float(elements.pop()))
            end = Point(float(elements.pop()), float(elements.pop()))

            if not absolute:
                control2 += current_pos
                end += current_pos

            segments.append(path.CubicBezier(current_pos.c, control1.c, control2.c, end.c))
            current_pos = end

        elif command == "Q":
            control = Point(float(elements.pop()), float(elements.pop()))
            end = Point(float(elements.pop()), float(elements.pop()))

            if not absolute:
                control += current_pos
                end += current_pos

            segments.append(path.QuadraticBezier(current_pos.c, control.c, end.c))
            current_pos = end

        elif command == "T":
            # Smooth curve. Control point is the "reflection" of
            # the second control point in the previous path.

            if last_command not in "QT":
                # If there is no previous command or if the previous command
                # was not an Q, q, T or t, assume the first control point is
                # coincident with the current point.
                control = current_pos
            else:
                # The control point is assumed to be the reflection of
                # the control point on the previous command relative
                # to the current point.
                control = current_pos + current_pos - segments[-1].control

            end = Point(float(elements.pop()), float(elements.pop()))

            if not absolute:
                end += current_pos

            segments.append(path.QuadraticBezier(current_pos.c, control.c, end.c))
            current_pos = end

        elif command == "A":
            radius = Point(float(elements.pop()), float(elements.pop()))
            rotation = float(elements.pop())
            arc = float(elements.pop())
            sweep = float(elements.pop())
            end = Point(float(elements.pop()), float(elements.pop()))

            if not absolute:
                end += current_pos

            segments.append(path.Arc(current_pos.c, radius.c, rotation, arc, sweep, end.c))
            current_pos = end

    return segments
