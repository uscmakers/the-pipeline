import cadquery as cq
import math
import csv
import os

def convert(lst):
    # Clean up empty array entries
    lst = list(filter(None, lst))
    return ' '.join(lst)

student_dict = {}
with open("Token_Dummies.csv") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader: # each row is a list, skip title
        student_dict[row[0]] = convert(row[1:])

# GET THIS FROM THE 3D MODELS
LOGO_DEPTH = 2 # Height of the USC logo

# SET DESIRED VALUES 
T_R = 45 # Radius of the token
T_H = 6 # Height of the flat token (excluding edge)
EDGE_W= 8 # Edge width of token
EDGE_H = 3 # Height of the token edge

FONT_DEPTH = 2 # depth of the engraved text
FONT_SIZE = 5

# Repeat for all token generation for all student entries
for key, val in student_dict.items():
    # BARE TOKEN
    token = cq.Workplane().circle(T_R).extrude(T_H)
    
    # edge
    edge = token.workplane(offset=T_H/2).circle(T_R).extrude(EDGE_H)
    edge = edge.cut(token.workplane(offset=T_H/2).circle(T_R-EDGE_W).extrude(EDGE_H))
    
    # Bare token + edge
    token = token.union(edge)
    # USC LOGO
    color2 = (cq.importers.importStep("usclogo.step")
            .translate((0,0,T_H-LOGO_DEPTH+0.0001))
            )
    
    s = student_dict[key] + " "
    
    # Radius
    r = T_R - EDGE_W/2
    
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
                        position=cq.Plane(origin=(x_pos, y_pos, T_H + EDGE_H - FONT_DEPTH), xDir=(xDir_x, xDir_y, 0.0), normal=(0.0, 0.0, 1.0))
                        )
            )
            color2 = color2.union(text)
            
            
    # CUT OUT color2 FROM TOKEN
    token = token.cut(color2)
    
    # Export
    newpath = r'custom_tokens/' + key
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    cq.exporters.export(token, 'custom_tokens/' + key + '/color1.step')
    cq.exporters.export(color2, 'custom_tokens/' + key + '/color2.step')