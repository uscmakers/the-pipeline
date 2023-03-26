import cadquery as cq
import math

# Get these from the 3D Model
T_R = 45 # Radius of the token
T_H = 9 # Height of the token
T_EDGE = 8.875 # Edge width of token

# SET DESIRED VALUES 
FONT_DEPTH = 5 # depth of the engraved text
FONT_SIZE = 5


token = cq.importers.importStep("usc.step")


s = "Integrity  Honor  Courage  Loyalty  Perseverance  "


# Radius
r = T_R - T_EDGE/2

# For each character
for i in range(0, len(s)):
    # Calculate x and y origin position
    deg = i/len(s) * 360
    rad = math.radians(deg)
    x_pos = r * math.sin(rad)
    y_pos = r * math.cos(rad)
    
    # COMPONENTS OF VECTOR FOR XDIR OF THE CHARACTER
    xDir_x = y_pos
    xDir_y = -x_pos
    
    # If character is not a space
    if (s[i] != " "):
        # Engrave character
        text = (cq.Compound
            .makeText(s[i], FONT_SIZE, FONT_DEPTH, font='Sans', fontPath=None, kind='bold', halign='center', valign='center', 
                    position=cq.Plane(origin=(x_pos, y_pos, T_H - FONT_DEPTH), xDir=(xDir_x, xDir_y, 0.0), normal=(0.0, 0.0, 1.0))
                    )
        )
        token = token.cut(text)

# Export
cq.exporters.export(token, 'token.step')