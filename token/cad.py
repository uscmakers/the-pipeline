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

# GET THIS FROM THE 3D MODEL
STEP_DEPTH = 1.5 # Height of the USC logo from STEP file
STEP_SIZE = 60 # Size of USC logo from STEP file

COMP_STEP_DEPTH = 2
COMP_STEP_SIZE = 69.573


# SET DESIRED VALUES 
T_R = 45 # Radius of the token
T_H = 4 # Height of the flat token (excluding edge)
EDGE_W = 10 # Edge width of token
EDGE_H = 3 # Height of the token edge

LOGO_SIZE = 60
COMP_SIZE = (2*T_R - 2*EDGE_W) *0.95

FONT_DEPTH = 1 # depth of the engraved text
BACK_FONT_SIZE = 5
FONT_SIZE = 7
OUTER_MAX_CHAR = 64 # this determines the spacing of the characters
INNER_MAX_CHAR = 48

# Repeat for all token generation for all student entries
for key, val in student_dict.items():
    # BARE TOKEN (COLOR 1)
    token = cq.Workplane().circle(T_R).extrude(T_H)


    # edge (COLOR 1)
    edge = token.workplane(offset=T_H/2).circle(T_R).extrude(EDGE_H)
    edge = edge.cut(token.workplane(offset=T_H/2).circle(T_R-EDGE_W).extrude(EDGE_H))

    # Bare token + edge (COLOR 1)
    token = token.union(edge)

    # USC LOGO (COLOR 2)
    logo = (cq.importers.importStep("usclogo.step")
            .val().scale(LOGO_SIZE/STEP_SIZE)
            )
    color2 = cq.Workplane()
    color2 = color2.union(logo)

    # NAME (COLOR 2)
    name_str = "USC Makers"
    text = (cq.Compound
                .makeText(name_str, BACK_FONT_SIZE, FONT_DEPTH, font='Sans', fontPath=None, kind='bold', halign='center', valign='center', 
                        position=cq.Plane(origin=(0,0,0), xDir=(1,0,0), normal=(0, 0, 1))
                        )
                .mirror("XZ").rotate((0,0,-1), (0,0,1), 180)
                .translate((0, -LOGO_SIZE/2 - 5, 0))
            )
    color2 = color2.union(text)

    # COMPASS (COLOR 2)
    compass = (cq.importers.importStep("compass.step")
            .val().scale(COMP_SIZE/COMP_STEP_SIZE)
            .translate((0,0, T_H - COMP_STEP_DEPTH * COMP_SIZE/COMP_STEP_SIZE))
            )
    color2 = color2.union(compass)
    
    # CUSTOMIZABLE MORAL VALUES (COLOR 2)
    s = student_dict[key] + " "
    
    #---------- OUTER -----------
    outer_words = ["Integrity", "Honor", "Righteousness", "Loyalty"]

    # Radius
    outer_r = T_R - EDGE_W/2

    # For each word
    for i in range(0, 4):
        word = outer_words[i]
        # For each character
        for j in range(0, len(word)):
            # Calculate x and y origin position
            # deg = i/len(s) * 360
            deg = 90*i - len(word)/2*(360/OUTER_MAX_CHAR) + j*(360/OUTER_MAX_CHAR)
            rad = math.radians(deg)
            x_pos = outer_r*math.sin(rad)
            y_pos = outer_r*math.cos(rad)
            
            # COMPONENTS OF VECTOR FOR XDIR OF THE CHARACTER
            xDir_x = y_pos
            xDir_y = -x_pos
            
            # If character is not a space
            if (word[j] != " "):
                # Engrave character
                text = (cq.Compound
                    .makeText(word[j], FONT_SIZE, FONT_DEPTH, font='Consolas', fontPath=None, kind='bold', halign='center', valign='center', 
                            position=cq.Plane(origin=(x_pos, y_pos, T_H + EDGE_H - FONT_DEPTH), xDir=(xDir_x, xDir_y, 0.0), normal=(0.0, 0.0, 1.0))
                            )
                )
                color2 = color2.union(text)
                

    #---------- INNER -----------
    inner_words = ["Courage", "Accountability", "Honesty", "Commitment"]

    # Radius
    r = T_R - EDGE_W * 3/2

    # For each word
    for i in range(0, 4):
        word = inner_words[i]
        # For each character
        for j in range(0, len(word)):
            # Calculate x and y origin position
            # deg = i/len(s) * 360
            deg = 45 + 90*i - len(word)/2*(360/INNER_MAX_CHAR) + j*(360/INNER_MAX_CHAR)
            rad = math.radians(deg)
            x_pos = r*math.sin(rad)
            y_pos = r*math.cos(rad)
            
            # COMPONENTS OF VECTOR FOR XDIR OF THE CHARACTER
            xDir_x = y_pos
            xDir_y = -x_pos
            
            # If character is not a space
            if (word[j] != " "):
                # Engrave character
                text = (cq.Compound
                    .makeText(word[j], FONT_SIZE, FONT_DEPTH, font='Consolas', fontPath=None, kind='bold', halign='center', valign='center', 
                            position=cq.Plane(origin=(x_pos, y_pos, T_H - FONT_DEPTH), xDir=(xDir_x, xDir_y, 0.0), normal=(0.0, 0.0, 1.0))
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