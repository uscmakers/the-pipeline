import cadquery as cq
import math
import csv
import os

# def convert(lst):
#     # Clean up empty array entries
#     lst = list(filter(None, lst))
#     return ' '.join(lst)

student_dict = {}
with open("WRIT340_COMPASS.csv") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader: # each row is a list, skip title
        student_dict[row[0]] = row[1:]

# A function that returns the length of the value:
def word_len(e):
  return len(e)

# GET THIS FROM THE 3D MODEL
LOGO_STEP_DEPTH = 0.6 # Exact height of the USC logo from STEP file
LOGO_STEP_SIZE = 60 # Size of USC logo from STEP file (may be approximate)

COMP_STEP_DEPTH = 0.6 # This must be exact
COMP_STEP_SIZE = 67 # This might not be exact


# SET DESIRED VALUES 
T_R = 45 # Radius of the token
T_H = 3.2 # Height of the flat token (excluding edge)
EDGE_W = 10 # Edge width of token
EDGE_H = 2.4 # Height of the token edge

LOGO_SIZE = 60
COMP_SIZE = 67

FONT_DEPTH = 0.6 # depth of the engraved text
BACK_FONT_SIZE = 5
FONT_SIZE = 7
OUTER_MAX_CHAR = 64 # this determines the spacing of the characters
INNER_MAX_CHAR = 48

# ----------- Calculations -----------

final_logo_depth = (LOGO_SIZE/LOGO_STEP_SIZE)*LOGO_STEP_DEPTH
final_comp_depth = (COMP_SIZE/COMP_STEP_SIZE)*COMP_STEP_DEPTH

print("SCALING LOGO BY", LOGO_SIZE/LOGO_STEP_SIZE)
print("SCALING COMPASS ROSE BY", COMP_SIZE/COMP_STEP_SIZE)


# CHECK THAT NUMBER OF BLACK LAYERS IS EVEN
combined_logo_compass_height = final_logo_depth + final_comp_depth

if combined_logo_compass_height > T_H:
    print("Logo and compass layers overlap. Height of black layers is equal to flat token height")
    print("MAKE SURE # of LAYERS IS EVEN (height is a multiple of 0.4mm):", T_H, "mm")
else: 
    print("Logo and compass layers do not overlap")
    print("\tMAKE SURE # of LOGO LAYERS IS ODD:", final_logo_depth, "mm")
    print("\tMAKE SURE # of COMPASS LAYERS IS ODD:", final_comp_depth, "mm")
    print("Flat token height:", T_H, "mm")

print("Black font depth:", FONT_DEPTH, "mm")

# ---------------------------- TOKEN GENERATION ------------------------------- 

# Repeat for all token generation for all student entries
for key, val in student_dict.items():
    val = val[1:]
    val.sort(reverse=True, key=word_len)
    outer_words = []
    outer_words.append(val[0])
    outer_words.append(val[2])
    outer_words.append(val[1])
    outer_words.append(val[3])
    inner_words = []
    inner_words.append(val[4])
    inner_words.append(val[6])
    inner_words.append(val[5])
    inner_words.append(val[7])
    # BARE TOKEN (COLOR 1)
    token = cq.Workplane().circle(T_R).extrude(T_H)


    # edge (COLOR 1)
    edge = token.workplane(offset=T_H/2).circle(T_R).extrude(EDGE_H)
    edge = edge.cut(token.workplane(offset=T_H/2).circle(T_R-EDGE_W).extrude(EDGE_H))

    # Bare token + edge (COLOR 1)
    token = token.union(edge)

    # USC LOGO (COLOR 2)
    logo = (cq.importers.importStep("usclogo.step")
            .val().scale(LOGO_SIZE/LOGO_STEP_SIZE)
            )
    color2 = cq.Workplane()
    color2 = color2.union(logo)

    # NAME (COLOR 2)
    name_str = key
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
    
    
    # #---------- OUTER -----------
    # outer_words = ["Integrity", "Honor", "Righteousness", "Loyalty"]

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
                

    # #---------- INNER -----------
    # inner_words = ["Courage", "Accountability", "Honesty", "Commitment"]

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
    cq.exporters.export(token, 'custom_tokens/' + key + '/color1.stl')
    cq.exporters.export(color2, 'custom_tokens/' + key + '/color2.stl')