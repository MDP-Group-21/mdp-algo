import numpy as np
import sys
import webbrowser, os
from operator import attrgetter

try: color = sys.stdout.shell
except AttributeError: raise RuntimeError("Use IDLE")

class Robot(object):
    def __init__(self, coord, face, wall_left=False, wall_right=False, wall_ahead=False):
        self.coord = coord
        self.face = face
        self.wall_left = wall_left
        self.wall_right = wall_right
        self.wall_ahead = wall_ahead
    def __getitem__(self,index):
        if index == 0:
            return self.coord
        elif index == 1:
            return self.face
    def __setitem__(self,index,value):
        self[index] = value
class Coordinates(object):
    def __init__(self, coord):
        self.x = coord[0]
        self.y = coord[1]
    def __getitem__(self,index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
class Cell(object):
    def __init__(self, text, explored = False, has_image = False, direction = '', fpath = '1'):
        self.text = text
        self.explored = explored
        self.has_image = has_image
        self.direction = direction
        self.fpath = fpath
class Frontier(object):
    def __init__(self, coord, step, hvalue):
        self.x = coord[0]
        self.y = coord[1]
        self.step = step
        self.hvalue = hvalue
        self.total = step + hvalue

start = [1,1]
goal = [13,18]
string = input('Time limit?(m:ss)')
time_input = string.split(':')
time_limit = int(time_input[0])*60 + int(time_input[1])
explore_limit = int(input('Explore limit?(%)'))
print(time_limit)
print(explore_limit)
robot = Robot([1,1],'D')
mdp_map = []
mdp_explore_map = []


#2 parts to sending data
#1. 0 for unexplored, 1 for explored
#2. (only for explored cell) 0 for empty, 1 for obstacle

def initialize_map():
    if os.path.isfile("sim.txt"):
        os.remove("sim.txt")
    if os.path.isfile("explore.txt"):
        os.remove("explore.txt")
    mdp_map_row = []
    mdp_explore_map_row = []
    for j in range(20):
        for i in range(15):
            if i in range(start[0]+2) and j in range(start[1]+2):
                mdp_map_row.append(Cell('S'))
            elif i in range(goal[0]-1, goal[0]+2) and j in range(goal[1]-1,goal[1]+2):
                mdp_map_row.append(Cell('G'))
            elif i == 0 or i == 14 or j == 0 or j == 19:
                mdp_map_row.append(Cell('V'))
            else:
                mdp_map_row.append(Cell(' '))
            mdp_explore_map_row.append(Cell(' '))
        mdp_explore_map.append(mdp_explore_map_row)
        mdp_map.append(mdp_map_row)
        mdp_map_row = []

def reset_fpath():
    for j in range(20):
        for i in range(15):
            mdp_map[j][i].fpath = '1'

def fully_explored():
    for j in range(20):
        for i in range(15):
            if not mdp_map[j][i].explored:
                return False
    return True

def valid_space(x, y):
    for j in range(3):
        for i in range(3):
            if mdp_map[y-1+j][x-1+i].text == 'W' or not mdp_map[y-1+j][x-1+i].explored:
                return False
    return True

def to_explore(fro):
    candidate = []
    distance = 999999
    evdistance = 0
    for j in range(19,-1,-1):
        for i in range(15):
            if not mdp_map[j][i].explored:
                if mdp_map[j][i-1].explored and mdp_map[j][i-2].explored and mdp_map[j][i-2].text != 'W' and mdp_map[j][i-1].text != 'W':
                    if valid_space(i-2, j):
                        evdistance = ((i-2) - fro[0]) + (j - fro[1])
                        if evdistance < distance:
                            candidate = [i-2, j]
                            distance = evdistance
                elif mdp_map[j][i+1].explored and mdp_map[j][i+2].explored and mdp_map[j][i+2].text != 'W' and mdp_map[j][i+1].text != 'W':
                    if valid_space(i+2, j):
                        evdistance = ((i+2) - fro[0]) + (j - fro[1])
                        if evdistance < distance:
                            candidate = [i+2, j]
                            distance = evdistance
                elif mdp_map[j+1][i].explored and mdp_map[j+2][i].explored and mdp_map[j+2][i].text != 'W' and mdp_map[j+1][i].text != 'W':
                    if valid_space(i, j+2):
                        evdistance = (i - fro[0]) + ((j+2) - fro[1])
                        if evdistance < distance:
                            candidate = [i, j+2]
                            distance = evdistance
                elif mdp_map[j-1][i].explored and mdp_map[j-2][i].explored and mdp_map[j-2][i].text != 'W' and mdp_map[j-1][i].text != 'W':
                    if valid_space(i, j-2):
                        evdistance = (i - fro[0]) + ((j-2) - fro[1])
                        if evdistance < distance:
                            candidate = [i, j-2]
    print('candidate: ' + str(candidate))
    return candidate

def update_map(xcoord, ycoord, text):
    mdp_map[ycoord][xcoord].text = text    
    
def print_map():
    for j in range(19,-1,-1):
        for i in range(15):
            if mdp_map[j][i].text == 'R':
                color.write('[' + mdp_map[j][i].text + ']', 'STRING') #green
            elif mdp_map[j][i].text == 'H':
                color.write('[' + mdp_map[j][i].text + ']', 'KEYWORD') #orange
            else:
                print('[' + mdp_map[j][i].text + ']', end='')
        print()
    print()

def oob(x,y):
    return (x not in range(15) or y not in range(20))

def print_explored():
    for j in range(19,-1,-1):
        for i in range(15):
            if mdp_map[j][i].explored:
                print('[1]', end='')
            else:
                print('[0]', end='')
        print()
    print()

def explore_percent():
    var1 = 0
    for j in range(20):
        for i in range(15):
            if mdp_map[j][i].explored:
                var1 += 1
    return int((var1/300)*100)

def print_descriptor():
    descriptor_1 = ['11']
    descriptor_2 = []
    for j in range(20):
        for i in range(15):
            if mdp_map[j][i].explored:
                descriptor_1.append('1')
                if mdp_map[j][i].text == 'W':
                    descriptor_2.append('1')
                else:
                    descriptor_2.append('0')
            else:
                descriptor_1.append('0')
    descriptor_1.append('11')

    des1 = ''.join(descriptor_1)
    hstr = '%0*X' % ((len(des1) + 3) // 4, int(des1, 2))
    #print(hstr)
    des2 = ''.join(descriptor_2)
    while len(des2) % 8 != 0:
        des2 += '0'
    hstr2 = '%0*X' % ((len(des2) + 3) // 4, int(des2, 2))
    #print(hstr2)
    return hstr + '\n' + hstr2 + '\n'

def print_alt_descriptor():
    descriptor = []
    for j in range(19,-1,-1):
        for i in range(15):
            if mdp_map[j][i].explored:
                if mdp_map[j][i].text == ' ' or mdp_map[j][i].text == 'V':
                    descriptor.append('S')
                else:
                    descriptor.append(mdp_map[j][i].text)
            else:
                descriptor.append('X')
    des = ''.join(descriptor)
    #print(des)
    return des + '\n'

def place_wall(x_coord, y_coord):
    if x_coord in range(15) and y_coord in range(20):
        mdp_map[y_coord][x_coord].text = 'W'
        place_vwall(x_coord+1, y_coord)
        place_vwall(x_coord, y_coord+1)
        place_vwall(x_coord-1, y_coord)
        place_vwall(x_coord, y_coord-1)
    else:
        print('Wall out of range')
        
def place_vwall(x_coord, y_coord):
    if x_coord in range(15) and y_coord in range(20) and mdp_map[y_coord][x_coord].text!='W':
        mdp_map[y_coord][x_coord].text = 'V'

def place_robot(robot_coord):
    x = robot_coord[0]
    y = robot_coord[1]
    place = True
    for i in range(3):
        for j in range(3):
            if mdp_map[y-1+j][x-1+i].text == 'W':
                #place = False
                place = True
    if place:
        for i in range(3):
            for j in range(3):
                update_map(x-1+i, y-1+j, 'R')
                mdp_map[y-1+j][x-1+i].explored = True
        if robot.face == 'W':
            update_map(x, y+1, 'H')
        elif robot.face == 'A':
            update_map(x-1, y, 'H')
        elif robot.face == 'S':
            update_map(x, y-1, 'H')
        elif robot.face == 'D':
            update_map(x+1, y, 'H')
        robot_sense(robot)
    else:
        print('Error in robot placement.')

def sense_diag(robot, c1_1, c1_2, c2, c3_1, c3_2, c4, c5_1, c5_2, c6):
    robot_coord = robot[0]
    x = robot_coord[0]
    y = robot_coord[1]
    #top left
    #[ ][5]
    #[5][4][3]
    #   [3][2][1]
    #      [1][X]
    if (not oob(c1_1[0], c1_1[1]) and mdp_map[c1_1[1]][c1_1[0]].text == 'W') and (not oob(c1_2[0], c1_2[1]) and mdp_map[c1_2[1]][c1_2[0]].text == 'W'): #1
        mdp_map[c1_1[1]][c1_1[0]].explored = True
        mdp_map[c1_2[1]][c1_2[0]].explored = True
        return
    else:
        if not oob(c1_1[0], c1_1[1]):
            mdp_map[c1_1[1]][c1_1[0]].explored = True
        if not oob(c1_2[0], c1_2[1]):
            mdp_map[c1_2[1]][c1_2[0]].explored = True
                    
    if not oob(c2[0], c2[1]) and mdp_map[c2[1]][c2[0]].text == 'W': #2
        mdp_map[c2[1]][c2[0]].explored = True
        return
    elif not oob(c2[0], c2[1]):
        mdp_map[c2[1]][c2[0]].explored = True
                    
    #3 is blocked by 1
    if (not oob(c3_1[0], c3_1[1]) and mdp_map[c3_1[1]][c3_1[0]].text == 'W') and (not oob(c3_2[0], c3_2[1]) and mdp_map[c3_2[1]][c3_2[0]].text == 'W'): #3
        if not oob(c3_1[0], c3_1[1]):
            mdp_map[c3_1[1]][c3_1[0]].explored = True
        if not oob(c3_2[0], c3_2[1]):
            mdp_map[c3_2[1]][c3_2[0]].explored = True
        return
    else:
        if not oob(c3_1[0], c3_1[1]) and mdp_map[c1_1[1]][c1_1[0]].text != 'W':
            mdp_map[c3_1[1]][c3_1[0]].explored = True
        if not oob(c3_2[0], c3_2[1]) and mdp_map[c1_2[1]][c1_2[0]].text != 'W':
            mdp_map[c3_2[1]][c3_2[0]].explored = True
                
    if not oob(c4[0], c4[1]) and mdp_map[c4[1]][c4[0]].text == 'W': #4
        mdp_map[c4[1]][c4[0]].explored = True
        return
    elif not oob(c4[0], c4[1]):
        mdp_map[c4[1]][c4[0]].explored = True

    #5 blocked by 3 or 1
    if (not oob(c5_1[0], c5_1[1]) and mdp_map[c5_1[1]][c5_1[0]].text == 'W') and (not oob(c5_2[0], c5_2[1]) and mdp_map[c5_2[1]][c5_2[0]].text == 'W'): #5
        if not oob(c5_1[0], c5_1[1]):
            mdp_map[y+2][x-3].explored = True
        if not oob(c5_2[0], c5_2[1]):
            mdp_map[c5_2[1]][c5_2[0]].explored = True
        return
    else:
        if not oob(c5_1[0], c5_1[1]) and mdp_map[c3_1[1]][c3_1[0]].text != 'W' and mdp_map[c1_1[1]][c1_1[0]].text != 'W':
            mdp_map[c5_1[1]][c5_1[0]].explored = True
        if not oob(c5_2[0], c5_2[1]) and mdp_map[c3_2[1]][c3_2[0]].text != 'W' and mdp_map[c1_2[1]][c1_2[0]].text != 'W':
            mdp_map[c5_2[1]][c5_2[0]].explored = True

    if not oob(c6[0], c6[1]):#6
        mdp_map[c6[1]][c6[0]].explored = True
    #print('loop')
    #mdp_map[y+3-1+j][x-3-1+i].explored = True
        
def robot_sense(robot):
    robot_coord = robot[0]
    x = robot_coord[0]
    y = robot_coord[1]
    robot.wall_left = False
    robot.wall_right = False
    robot.wall_ahead = False
    #set points to activate different detection algorithms for different directions
    if robot.face == 'W':
        #print('w function')
        #top left, top right, left, up, right
        sense_diag(robot, [x-1, y], [x, y+1], [x-1, y+1], [x-2, y+1], [x-1, y+2], [x-2, y+2], [x-3, y+2], [x-2, y+3], [x-3, y+3])
        sense_diag(robot, [x+1, y], [x, y+1], [x+1, y+1], [x+2, y+1], [x+1, y+2], [x+2, y+2], [x+3, y+2], [x+2, y+3], [x+3, y+3])
        #left
        for j in range(3):
            if y-1+j in range(20) and x-2 in range(15):
                if mdp_map[y-1+j][x-1].text == 'W':
                    robot.wall_left = True
                    continue
                if x-4 in range(15) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W' and mdp_map[y-1+j][x-3].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    mdp_map[y-1+j][x-3].explored = True
                    mdp_map[y-1+j][x-4].explored = True
                elif x-3 in range(15) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    mdp_map[y-1+j][x-3].explored = True
                elif x-2 in range(15) and mdp_map[y-1+j][x-1].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                else:
                    robot.wall_left = True
                if x-2 in range(15) and mdp_map[y-1+j][x-2].text == 'W':
                    robot.wall_left = True
            elif x-2 not in range(15):
                robot.wall_left = True
                break
        #up
        for i in range(3):
            if y+2 in range(20) and x-1+i in range(15):
                if mdp_map[y+1][x-1+i].text == 'W':
                    robot.wall_ahead = True
                    continue
                if y+4 in range(20) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W' and mdp_map[y+3][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    mdp_map[y+3][x-1+i].explored = True
                    mdp_map[y+4][x-1+i].explored = True
                elif y+3 in range(20) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    mdp_map[y+3][x-1+i].explored = True
                elif y+2 in range(20) and mdp_map[y+1][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                else:
                    robot.wall_ahead = True
                if y+2 in range(20) and mdp_map[y+2][x-1+i].text == 'W':
                    robot.wall_ahead = True
            elif y+2 not in range(20):
                robot.wall_ahead = True
                break
        #right
        for j in range(3):
            if y-1+j in range(20) and x+2 in range(15):
                if mdp_map[y-1+j][x+1].text == 'W':
                    robot.wall_right = True
                    continue
                if x+4 in range(15) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W' and mdp_map[y-1+j][x+3].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                    mdp_map[y-1+j][x+3].explored = True
                    mdp_map[y-1+j][x+4].explored = True
                elif x+3 in range(15) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                    mdp_map[y-1+j][x+3].explored = True
                elif x+2 in range(15) and mdp_map[y-1+j][x+1].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                else:
                    robot.wall_right = True
                if x+2 in range(15) and mdp_map[y-1+j][x+2].text == 'W':
                    robot.wall_right = True
            elif x+2 not in range(15):
                robot.wall_right = True
                break
        for i in range(3):
            if y-1 in range(20):
                mdp_map[y-1][x-1+i].explored = True
    elif robot.face == 'A':
        #print('a function')
        #top left, bottom left, up, left, down
        sense_diag(robot, [x-1, y], [x, y+1], [x-1, y+1], [x-2, y+1], [x-1, y+2], [x-2, y+2], [x-3, y+2], [x-2, y+3], [x-3, y+3])
        sense_diag(robot, [x-1, y], [x, y-1], [x-1, y-1], [x-2, y-1], [x-1, y-2], [x-2, y-2], [x-3, y-2], [x-2, y-3], [x-3, y-3])
        #left
        for j in range(3):
            if y-1+j in range(20) and x-2 in range(15):
                if mdp_map[y-1+j][x-1].text == 'W':
                    #print('X1')
                    robot.wall_ahead = True
                    continue
                if x-4 in range(15) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W' and mdp_map[y-1+j][x-3].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    mdp_map[y-1+j][x-3].explored = True
                    mdp_map[y-1+j][x-4].explored = True
                    #print('X2')
                elif x-3 in range(15) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    mdp_map[y-1+j][x-3].explored = True
                    #print('X3')
                elif x-2 in range(15) and mdp_map[y-1+j][x-1].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    #print('X4')
                else:
                    robot.wall_ahead = True
                    #print('X5')
                if x-2 in range(15) and mdp_map[y-1+j][x-2].text == 'W':
                    #print('X6')
                    robot.wall_ahead = True
            elif x-2 not in range(15):
                robot.wall_ahead = True
                #print('X7')
                break
        #up
        for i in range(3):
            #print(i)
            if y+2 in range(20) and x-1+i in range(15):
                if mdp_map[y+1][x-1+i].text == 'W':
                    robot.wall_right = True
                    #print('Y1')
                    continue
                if y+4 in range(20) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W' and mdp_map[y+3][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    mdp_map[y+3][x-1+i].explored = True
                    mdp_map[y+4][x-1+i].explored = True
                    #print('Y2')
                elif y+3 in range(20) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    mdp_map[y+3][x-1+i].explored = True
                    #print('Y3')
                elif y+2 in range(20) and mdp_map[y+1][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    #print('Y4')
                else:
                    robot.wall_right = True
                    #print('Y5')
                if y+2 in range(20) and mdp_map[y+2][x-1+i].text == 'W':
                    robot.wall_right = True
                    #print('Y6')
            elif y+2 not in range(20):
                robot.wall_right = True
                #print('Y7')
                break
        #down
        for i in range(3):
            if y-2 in range(20) and x-1+i in range(15):
                if mdp_map[y-1][x-1+i].text == 'W':
                    robot.wall_left = True
                    continue
                if y-4 in range(20) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W' and mdp_map[y-3][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                    mdp_map[y-3][x-1+i].explored = True
                    mdp_map[y-4][x-1+i].explored = True
                elif y-3 in range(20) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                    mdp_map[y-3][x-1+i].explored = True
                elif y-2 in range(20) and mdp_map[y-1][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                else:
                    robot.wall_left = True
                if y-2 in range(20) and mdp_map[y-2][x-1+i].text == 'W':
                    robot.wall_left = True
            elif y-2 not in range(20):
                robot.wall_left = True
                break
        for i in range(3):
            if x+1 in range(20):
                mdp_map[y-1+i][x+1].explored = True
    elif robot.face == 'S':
        #print('s function')
        #bottom left, bottom right, left, down, right
        sense_diag(robot, [x-1, y], [x, y-1], [x-1, y-1], [x-2, y-1], [x-1, y-2], [x-2, y-2], [x-3, y-2], [x-2, y-3], [x-3, y-3])
        sense_diag(robot, [x+1, y], [x, y-1], [x+1, y-1], [x+2, y-1], [x+1, y-2], [x+2, y-2], [x+3, y-2], [x+2, y-3], [x+3, y-3])
        #left
        for j in range(3):
            if y-1+j in range(20) and x-2 in range(15):
                if mdp_map[y-1+j][x-1].text == 'W':
                    robot.wall_right = True
                    continue
                if x-4 in range(15) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W' and mdp_map[y-1+j][x-3].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    mdp_map[y-1+j][x-3].explored = True
                    mdp_map[y-1+j][x-4].explored = True
                elif x-3 in range(15) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                    mdp_map[y-1+j][x-3].explored = True
                elif x-2 in range(15) and mdp_map[y-1+j][x-1].text != 'W':
                    mdp_map[y-1+j][x-2].explored = True
                else:
                    robot.wall_right = True
                if x-2 in range(15) and mdp_map[y-1+j][x-2].text == 'W':
                    robot.wall_right = True
            elif x-2 not in range(15):
                robot.wall_right = True
                break
        #right
        for j in range(3):
            if y-1+j in range(20) and x+2 in range(15):
                if mdp_map[y-1+j][x+1].text == 'W':
                    robot.wall_left = True
                    continue
                if x+4 in range(15) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W' and mdp_map[y-1+j][x+3].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                    mdp_map[y-1+j][x+3].explored = True
                    mdp_map[y-1+j][x+4].explored = True
                elif x+3 in range(15) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                    mdp_map[y-1+j][x+3].explored = True
                elif x+2 in range(15) and mdp_map[y-1+j][x+1].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                else:
                    robot.wall_left = True
                if x+2 in range(15) and mdp_map[y-1+j][x+2].text == 'W':
                    robot.wall_left = True
            elif x+2 not in range(15):
                robot.wall_left = True
                break
        #down
        for i in range(3):
            if y-2 in range(20) and x-1+i in range(15):
                if mdp_map[y-1][x-1+i].text == 'W':
                    robot.wall_ahead = True
                    continue
                if y-4 in range(20) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W' and mdp_map[y-3][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                    mdp_map[y-3][x-1+i].explored = True
                    mdp_map[y-4][x-1+i].explored = True
                elif y-3 in range(20) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                    mdp_map[y-3][x-1+i].explored = True
                elif y-2 in range(20) and mdp_map[y-1][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                else:
                    robot.wall_ahead = True
                if y-2 in range(20) and mdp_map[y-2][x-1+i].text == 'W':
                    robot.wall_ahead = True
            elif y-2 not in range(20):
                robot.wall_ahead = True
                break
        for i in range(3):
            if y+1 in range(20):
                mdp_map[y+1][x-1+i].explored = True
    elif robot.face == 'D':
        #print('d function')
        #top right, bottom right, up, right, down
        sense_diag(robot, [x+1, y], [x, y+1], [x+1, y+1], [x+2, y+1], [x+1, y+2], [x+2, y+2], [x+3, y+2], [x+2, y+3], [x+3, y+3])
        sense_diag(robot, [x+1, y], [x, y-1], [x+1, y-1], [x+2, y-1], [x+1, y-2], [x+2, y-2], [x+3, y-2], [x+2, y-3], [x+3, y-3])
        #up
        for i in range(3):
            if y+2 in range(20) and x-1+i in range(15):
                if mdp_map[y+1][x-1+i].text == 'W':
                    robot.wall_left = True
                    continue
                if y+4 in range(20) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W' and mdp_map[y+3][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    mdp_map[y+3][x-1+i].explored = True
                    mdp_map[y+4][x-1+i].explored = True
                elif y+3 in range(20) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                    mdp_map[y+3][x-1+i].explored = True
                elif y+2 in range(20) and mdp_map[y+1][x-1+i].text != 'W':
                    mdp_map[y+2][x-1+i].explored = True
                else:
                    robot.wall_left = True
                if y+2 in range(20) and mdp_map[y+2][x-1+i].text == 'W':
                    robot.wall_left = True
            elif y+2 not in range(20):
                robot.wall_left = True
                #print('broke1')
                break
        #right
        for j in range(3):
            if y-1+j in range(20) and x+2 in range(15):
                if mdp_map[y-1+j][x+1].text == 'W':
                    robot.wall_ahead = True
                    continue
                if x+4 in range(15) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W' and mdp_map[y-1+j][x+3].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                    mdp_map[y-1+j][x+3].explored = True
                    mdp_map[y-1+j][x+4].explored = True
                elif x+3 in range(15) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                    mdp_map[y-1+j][x+3].explored = True
                elif x+2 in range(15) and mdp_map[y-1+j][x+1].text != 'W':
                    mdp_map[y-1+j][x+2].explored = True
                else:
                    robot.wall_ahead = True
                if x+2 in range(15) and mdp_map[y-1+j][x+2].text == 'W':
                    robot.wall_ahead = True
            elif x+2 not in range(15):
                robot.wall_ahead = True
                break
        #down
        for i in range(3):
            if y-2 in range(20) and x-1+i in range(15):
                if mdp_map[y-1][x-1+i].text == 'W':
                    robot.wall_right = True
                    continue
                if y-4 in range(20) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W' and mdp_map[y-3][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                    mdp_map[y-3][x-1+i].explored = True
                    mdp_map[y-4][x-1+i].explored = True
                elif y-3 in range(20) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                    mdp_map[y-3][x-1+i].explored = True
                elif y-2 in range(20) and mdp_map[y-1][x-1+i].text != 'W':
                    mdp_map[y-2][x-1+i].explored = True
                else:
                    robot.wall_right = True
                if y-2 in range(20) and mdp_map[y-2][x-1+i].text == 'W':
                    robot.wall_right = True
            elif y-2 not in range(20):
                robot.wall_right = True
                #print('broke3')
                break
        for i in range(3):
            if x-1 in range(20):
                mdp_map[y-1+i][x-1].explored = True
    with open("explore.txt","a") as text_file_explore:
        text_file_explore.write(print_descriptor())
    with open("sim.txt","a") as text_file_sim:
        text_file_sim.write(print_alt_descriptor())
    #print('=================================================')
    #top left
    #[ ][5]
    #[5][4][3]
    #   [3][2][1]
    #      [1][X]
    #sense_diag(robot, [x-1, y], [x, y+1], [x-1, y+1], [x-2, y+1], [x-1, y+2], [x-2, y+2], [x-3, y+2], [x-2, y+3], [x-3, y+3])
    #top right
    #      [5][6]
    #   [3][4][5]
    #[1][2][3]
    #[X][1]
    #sense_diag(robot, [x+1, y], [x, y+1], [x+1, y+1], [x+2, y+1], [x+1, y+2], [x+2, y+2], [x+3, y+2], [x+2, y+3], [x+3, y+3])
    #bottom left
    #      [1][X]
    #   [3][2][1]
    #[5][4][3]
    #[6][5]
    #sense_diag(robot, [x-1, y], [x, y-1], [x-1, y-1], [x-2, y-1], [x-1, y-2], [x-2, y-2], [x-3, y-2], [x-2, y-3], [x-3, y-3])
    #bottom right
    #[X][1]
    #[1][2][3]
    #   [3][4][5]
    #      [5][6]
    #sense_diag(robot, [x+1, y], [x, y-1], [x+1, y-1], [x+2, y-1], [x+1, y-2], [x+2, y-2], [x+3, y-2], [x+2, y-3], [x+3, y-3])
    #left
    #for j in range(3):
    #    if y-1+j in range(15) and x-2-j in range(20):
    #       if mdp_map[y-1+j][x-1].text == 'W':
    #            continue
    #        if x-4 in range(20) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W' and mdp_map[y-1+j][x-3].text != 'W':
    #            mdp_map[y-1+j][x-2].explored = True
    #            mdp_map[y-1+j][x-3].explored = True
    #            mdp_map[y-1+j][x-4].explored = True
    #            robot.wall_left = False
    #        elif x-3 in range(20) and mdp_map[y-1+j][x-1].text != 'W' and mdp_map[y-1+j][x-2].text != 'W':
    #            mdp_map[y-1+j][x-2].explored = True
    #            mdp_map[y-1+j][x-3].explored = True
    #            robot.wall_left = False
    #        elif x-2 in range(20) and mdp_map[y-1+j][x-1].text != 'W':
    #            mdp_map[y-1+j][x-2].explored = True
    #            robot.wall_left = True
    #        else:
    #            robot.wall_left = True
    #up
    #for i in range(3):
    #    if y+2+i in range(15) and x-1+i in range(20):
    #        if mdp_map[y+1][x-1+i].text == 'W':
    #            continue
    #        if y+4 in range(15) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W' and mdp_map[y+3][x-1+i].text != 'W':
    #            mdp_map[y+2][x-1+i].explored = True
    #            mdp_map[y+3][x-1+i].explored = True
    #            mdp_map[y+4][x-1+i].explored = True
    #            robot.wall_ahead = False
    #        elif y+3 in range(15) and mdp_map[y+1][x-1+i].text != 'W' and mdp_map[y+2][x-1+i].text != 'W':
    #            mdp_map[y+2][x-1+i].explored = True
    #            mdp_map[y+3][x-1+i].explored = True
    #            robot.wall_ahead = False
    #        elif y+2 in range(15) and mdp_map[y+1][x-1+i].text != 'W':
    #            mdp_map[y+2][x-1+i].explored = True
    #            robot.wall_ahead = True
    #        else:
    #            robot.wall_ahead = True
    #right
    #for j in range(3):
    #    if y-1+j in range(15) and x+2+i in range(20):
    #        if mdp_map[y-1+j][x+1].text == 'W':
    #            continue
    #        if x+4 in range(20) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W' and mdp_map[y-1+j][x+3].text != 'W':
    #            mdp_map[y-1+j][x+2].explored = True
    #            mdp_map[y-1+j][x+3].explored = True
    #            mdp_map[y-1+j][x+4].explored = True
    #            robot.wall_right = False
    #        elif x+3 in range(20) and mdp_map[y-1+j][x+1].text != 'W' and mdp_map[y-1+j][x+2].text != 'W':
    #            mdp_map[y-1+j][x+2].explored = True
    #            mdp_map[y-1+j][x+3].explored = True
    #            robot.wall_right = False
    #        elif x+2 in range(20) and mdp_map[y-1+j][x+1].text != 'W':
    #            mdp_map[y-1+j][x+2].explored = True
    #            robot.wall_right = True
    #        else:
    #            robot.wall_right = True
    #down
    #for i in range(3):
    #    if y-2+i in range(15) and x-1+i in range(20):
    #        if mdp_map[y-1][x-1+i].text == 'W':
    #            continue
    #        if y+4 in range(15) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W' and mdp_map[y-3][x-1+i].text != 'W':
    #            mdp_map[y-2][x-1+i].explored = True
    #            mdp_map[y-3][x-1+i].explored = True
    #            mdp_map[y-4][x-1+i].explored = True
    #            robot.wall_ahead = False
    #        elif y+3 in range(15) and mdp_map[y-1][x-1+i].text != 'W' and mdp_map[y-2][x-1+i].text != 'W':
    #            mdp_map[y+2][x-1+i].explored = True
    #            mdp_map[y+3][x-1+i].explored = True
    #            robot.wall_ahead = False
    #        elif y+2 in range(15) and mdp_map[y-1][x-1+i].text != 'W':
    #            mdp_map[y+2][x-1+i].explored = True
    #            robot.wall_ahead = True
    #        else:
    #            robot.wall_ahead = True
    #first check for walls
    #then determine explored/unexplored based on whether a block is blocked by a wall
    #Check using 3x3 grids for left, up, right; 2x2 for top left, top right

def step_eval(x, y, g):
    return (abs(g[0]-x) + abs(g[1]-y))

def h_eval(x, y, h):
    return (abs(x-h[0]) + abs(y-h[1]))

def explore(robot):
    path = []
    steps = 0
    right_wall_before = False
    goal_explored = False
    #right wall hug : ensure wall right is True as much as possible
    while robot.coord != start or (robot.coord == start and goal_explored == False):
        if steps == time_limit:
            print('Time up!')
            fastest_path(robot, robot.coord, start)
            return
        elif explore_percent() == explore_limit:
            print('Explore limit reached!')
            fastest_path(robot, robot.coord, start)
            return
        print(steps)
        robot_sense(robot)
        steps += 1
        if robot.wall_right and not robot.wall_ahead:
            robot_forward(robot)
            right_wall_before = True
            path.append(robot.face)
        elif robot.wall_right and robot.wall_ahead:
            robot_left(robot)
            right_wall_before = True
        elif robot.wall_ahead and not right_wall_before:
            robot_left(robot)
            right_wall_before = False
        elif robot.wall_ahead and right_wall_before:
            robot_right(robot)
            right_wall_before = False
        elif not robot.wall_right and right_wall_before:
            robot_right(robot)
            right_wall_before = False
        else:
            robot_forward(robot)
            right_wall_before = False
            path.append(robot.face)
        steps += 1
        if robot.coord == goal:
            goal_explored = True
        #print_map()
        with open("explore.txt","a") as text_file_explore:
            text_file_explore.write(print_descriptor())
        with open("sim.txt","a") as text_file_sim:
            text_file_sim.write(print_alt_descriptor())
        #print('=================================================')

    while not fully_explored():
        #print('Begin relocation routine.')
        #print(robot.coord)
        fastest_path(robot, robot.coord, to_explore(robot.coord))
        robot_sense(robot)

    fastest_path(robot, robot.coord, start)
    
    #print(path)
    #print_explored()
    #print_map()

def fastest_path(robot, begin, end):
    reset_fpath()
    #start from goal
    #formulate a path backwards towards goal
    #reverse the solution
    #!frontier -> coord, step, hvalue
    eye = [end[0], end[1]]
    frontier = []
    path = []
    wflag = False
    while eye != begin:
        #print(eye)
        #right
        if eye[0]+2 in range(15) and mdp_map[eye[1]][eye[0]].fpath != 'D':
            for i in range(3):
                if (mdp_map[eye[1]-1+i][eye[0]+2].text == 'W' or not mdp_map[eye[1]-1+i][eye[0]+2].explored) and not wflag:
                    wflag = True
                    #print('D, wall')
            if not wflag and mdp_map[eye[1]][eye[0]+2].explored:
                if mdp_map[eye[1]][eye[0]+1].fpath == '1':
                    frontier.append(Frontier([eye[0]+1,eye[1]], step_eval(eye[0]+1,eye[1],end), h_eval(eye[0]+1,eye[1],begin)))
                    mdp_map[eye[1]][eye[0]+1].fpath = 'A'
                    #print('D, frontier')
            wflag = False
            
        #left    
        if eye[0]-2 in range(15) and mdp_map[eye[1]][eye[0]].fpath != 'A':
            for i in range(3):
                if (mdp_map[eye[1]-1+i][eye[0]-2].text == 'W' or not mdp_map[eye[1]-1+i][eye[0]-2].explored) and not wflag:
                    wflag = True
                    #print('A, wall')
            if not wflag and mdp_map[eye[1]][eye[0]-2].explored:
                if mdp_map[eye[1]][eye[0]-1].fpath == '1':
                    frontier.append(Frontier([eye[0]-1,eye[1]], step_eval(eye[0]-1,eye[1],end), h_eval(eye[0]-1,eye[1],begin)))
                    mdp_map[eye[1]][eye[0]-1].fpath = 'D'
                    #print('A, frontier')
            wflag = False

        #up
        if eye[1]+2 in range(20) and mdp_map[eye[1]][eye[0]].fpath != 'W':
            for i in range(3):
                if (mdp_map[eye[1]+2][eye[0]-1+i].text == 'W' or not mdp_map[eye[1]+2][eye[0]-1+i].explored) and not wflag:
                    wflag = True
                    #print('W, wall')
            if not wflag and mdp_map[eye[1]+2][eye[0]].explored:
                if mdp_map[eye[1]+1][eye[0]].fpath == '1':
                    frontier.append(Frontier([eye[0],eye[1]+1], step_eval(eye[0],eye[1]+1,end), h_eval(eye[0]-1,eye[1],begin)))
                    mdp_map[eye[1]+1][eye[0]].fpath = 'S'
                    #print('W, frontier')
            wflag = False

        #down
        if eye[1]-2 in range(20) and mdp_map[eye[1]][eye[0]].fpath != 'S':
            for i in range(3):
                if (mdp_map[eye[1]-2][eye[0]-1+i].text == 'W' or not mdp_map[eye[1]-2][eye[0]-1+i].explored) and not wflag:
                    wflag = True
                    #print('S, wall')
            if not wflag and mdp_map[eye[1]-2][eye[0]].explored:
                if mdp_map[eye[1]-1][eye[0]].fpath == '1':
                    frontier.append(Frontier([eye[0],eye[1]-1], step_eval(eye[0],eye[1]-1,end), h_eval(eye[0]-1,eye[1],begin)))
                    mdp_map[eye[1]-1][eye[0]].fpath = 'W'
                    #print('S, frontier')
            wflag = False
        #for j in range(19,-1,-1):
        #    for i in range(15):
        #        if mdp_map[j][i].fpath != '':
        #            print('[' + mdp_map[j][i].fpath + ']', end='')
        #        else:
        #            print('[ ]',end='')
        #    print()
        #print()
        #for item in frontier:
            #print(item.x + item.y)
        minima = min(frontier, key=attrgetter('total'))
        eye = [minima.x, minima.y]
        for i in range(len(frontier)):
            if frontier[i].x == eye[0] and frontier[i].y == eye[1]:
                del frontier[i]
                break
            
    #for j in range(19,-1,-1):
    #    for i in range(15):
    #        if mdp_map[j][i].fpath != '':
    #            print('[' + mdp_map[j][i].fpath + ']', end='')
    #        else:
    #            print('[ ]',end='')
    #    print()
    #print()
    #print_explored()

    while eye != end:
        path.append(mdp_map[eye[1]][eye[0]].fpath)
        if mdp_map[eye[1]][eye[0]].fpath == 'W':
            eye[1] += 1
        elif mdp_map[eye[1]][eye[0]].fpath == 'A':
            eye[0] -= 1
        elif mdp_map[eye[1]][eye[0]].fpath == 'S':
            eye[1] -= 1
        elif mdp_map[eye[1]][eye[0]].fpath == 'D':
            eye[0] += 1
    #print(robot.coord)
    if robot.coord != begin:
        print("Where's my robot?")
    else:
        while robot.coord != end:
            next_path = path[0]
            if robot.face == next_path:
                robot_forward(robot)
                path.pop(0)
            elif robot.face == 'W':
                if next_path == 'A':
                    robot_left(robot)
                elif next_path == 'D':
                    robot_right(robot)
                elif next_path == 'S':
                    robot_right(robot)
                    robot_right(robot)
            elif robot.face == 'A':
                if next_path == 'S':
                    robot_left(robot)
                elif next_path == 'W':
                    robot_right(robot)
                elif next_path == 'D':
                    robot_right(robot)
                    robot_right(robot)
            elif robot.face == 'S':
                if next_path == 'D':
                    robot_left(robot)
                elif next_path == 'A':
                    robot_right(robot)
                elif next_path == 'W':
                    robot_right(robot)
                    robot_right(robot)
            elif robot.face == 'D':
                if next_path == 'W':
                    robot_left(robot)
                elif next_path == 'S':
                    robot_right(robot)
                elif next_path == 'A':
                    robot_right(robot)
                    robot_right(robot)
            with open("sim.txt","a") as text_file_sim:
                text_file_sim.write(print_alt_descriptor())
            #print_map()
                
    
def robot_forward(robot):
    robotcoord = robot[0]
    origincoord = Coordinates(robotcoord)
    #print(robot[0])
    robotface = robot.face
    if robotface == 'W':
        if robotcoord[1]+1 in range(20):
            robotcoord[1] += 1
    elif robotface == 'A':
        if robotcoord[0]-1 in range(15):
            robotcoord[0] -= 1
    elif robotface == 'S':
        if robotcoord[1]-1 in range(20):
            robotcoord[1] -= 1
    elif robotface == 'D':
        if robotcoord[0]+1 in range(15):
            robotcoord[0] += 1
    else:
        print('?')
    #update map
    for i in range(3):
        for j in range(3):
            coord1 = origincoord[0]-1+i
            coord2 = origincoord[1]-1+j
            if coord1 in range(start[0]+2) and coord2 in range(start[1]+2):
                update_map(coord1, coord2, 'S')
            elif origincoord[0]-1+i in range(goal[0]-1, goal[0]+2) and origincoord[1]-1+j in range(goal[1]-1,goal[1]+2):
                update_map(coord1, coord2, 'G')
            else:
                update_map(coord1, coord2, ' ')
    #robot
    for i in range(3):
        for j in range(3):
            update_map(robotcoord[0]-1+i, robotcoord[1]-1+j, 'R')
    if robot.face == 'W':
        update_map(robotcoord[0], robotcoord[1]+1, 'H')
    elif robot.face == 'A':
        update_map(robotcoord[0]-1, robotcoord[1], 'H')
    elif robot.face == 'S':
        update_map(robotcoord[0], robotcoord[1]-1, 'H')
    elif robot.face == 'D':
        update_map(robotcoord[0]+1, robotcoord[1], 'H')

def robot_left(robot):
    robotcoord = robot[0]
    if robot.face == 'W':
        robot.face = 'A'
    elif robot.face == 'A':
        robot.face = 'S'
    elif robot.face == 'S':
        robot.face = 'D'
    elif robot.face == 'D':
        robot.face = 'W'
    else:
        print('?')
    for i in range(3):
        for j in range(3):
            update_map(robotcoord[0]-1+i, robotcoord[1]-1+j, 'R')
    if robot.face == 'W':
        update_map(robotcoord[0], robotcoord[1]+1, 'H')
    elif robot.face == 'A':
        update_map(robotcoord[0]-1, robotcoord[1], 'H')
    elif robot.face == 'S':
        update_map(robotcoord[0], robotcoord[1]-1, 'H')
    elif robot.face == 'D':
        update_map(robotcoord[0]+1, robotcoord[1], 'H')

def robot_right(robot):
    robotcoord = robot[0]
    if robot.face == 'W':
        robot.face = 'D'
    elif robot.face == 'A':
        robot.face = 'W'
    elif robot.face == 'S':
        robot.face = 'A'
    elif robot.face == 'D':
        robot.face = 'S'
    else:
        print('?')
    for i in range(3):
        for j in range(3):
            update_map(robotcoord[0]-1+i, robotcoord[1]-1+j, 'R')
    if robot.face == 'W':
        update_map(robotcoord[0], robotcoord[1]+1, 'H')
    elif robot.face == 'A':
        update_map(robotcoord[0]-1, robotcoord[1], 'H')
    elif robot.face == 'S':
        update_map(robotcoord[0], robotcoord[1]-1, 'H')
    elif robot.face == 'D':
        update_map(robotcoord[0]+1, robotcoord[1], 'H')

def place_obstacles():
    #accepts arena input, 0 for empty, 1 for wall
    #places walls in arena, and prints a hexstr of the arena
    lines = []
    for i in range(20):
        line = input('Simulation arena data, please')
        lines.append(line)
    string = '\n'.join(lines)
    string = ''.join(string.split())
    obstacles = string.split()
    for j in range(20):
        for i in range(15):
            if string[i+(j*15)] == '1':
                place_wall(i,j)
    hexstr = '%0*X' % ((len(string)+3) // 4, int(string, 2))
    print(hexstr)

#main
initialize_map()

#top left
    #[ ][5]
    #[5][4][3]
    #   [3][2][1]
    #      [1][X]
#top left testing walls
#place_wall(8,9) #1
#place_wall(7,8) #1
#place_wall(7,9) #2
#place_wall(6,9) #3
#place_wall(7,10) #3
#place_wall(6,10) #4
#place_wall(5,10) #5
#place_wall(6,11) #5
#place_wall(5,11) #6
#top right testing walls
#place_wall(10,9)
#place_wall(9,10)
#place_wall(10,11)
#place_wall(11,10)
#left testing walls
#place_wall(4,9)
#place_wall(5,8)
#place_wall(6,7)

#obstacles
filename = 'D:\Python(3.6.4)\Practice\MDP21\MapSimulator\MapSimulator\PlayMapSimulator.html'
place_obstacles()
place_robot(robot.coord)
explore(robot)
print_explored()
print_map()
print_descriptor()
fastest_path(robot, start, goal)
webbrowser.open('http://localhost/Projects/MapSimulator/PlayMapSimulator.html')


            
