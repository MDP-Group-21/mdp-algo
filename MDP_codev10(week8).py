import numpy as np
import sys
import webbrowser, os
import socket
from operator import attrgetter
from testsocket import Algo
import time

try: color = sys.stdout.shell
except AttributeError: raise RuntimeError("Use IDLE")

class Robot(object):
    def __init__(self, coord, face, wall_left=False, wall_right=False, wall_ahead=False):
        self.coord = coord
        self.face = face
        self.wall_left = wall_left
        self.wall_right = wall_right
        self.wall_ahead = wall_ahead
        self.left_decay = 0
        self.right_decay = 0
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


#2 parts to sending data
#1. 0 for unexplored, 1 for explored
#2. (only for explored cell) 0 for empty, 1 for obstacle

def initialize_map():
    if os.path.isfile("realtimemap.txt"):
        os.remove("realtimemap.txt")
##    if os.path.isfile("explore.txt"):
##        os.remove("explore.txt")
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
##    print('candidate: ' + str(candidate))
    return candidate

def update_map(xcoord, ycoord, text):
    mdp_map[ycoord][xcoord].text = text    
    
##def print_map():
##    for j in range(19,-1,-1):
##        for i in range(15):
##            if mdp_map[j][i].text == 'R':
##                color.write('[' + mdp_map[j][i].text + ']', 'STRING') #green
##            elif mdp_map[j][i].text == 'H':
##                color.write('[' + mdp_map[j][i].text + ']', 'KEYWORD') #orange
##            else:
##                print('[' + mdp_map[j][i].text + ']', end='')
##        print()
##    print()

def oob(x,y):
    return (x not in range(15) or y not in range(20))

##def print_explored():
##    for j in range(19,-1,-1):
##        for i in range(15):
##            if mdp_map[j][i].explored:
##                print('[1]', end='')
##            else:
##                print('[0]', end='')
##        print()
##    print()

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
    return hstr + ';' + hstr2

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
        
def robot_sense(robot):
    mail.write('ARD|.')
    sensedata = mail.read('ARD')
    if 'ACK' in sensedata:
        mail.write('ARD|.')
        sensedata = list(map(int, mail.read('ARD')))
    robot_coord = robot[0]
    x = robot_coord[0]
    y = robot_coord[1]
    print('left decay: ' + str(robot.left_decay))
    print('right decay: ' + str(robot.right_decay))
    if robot.left_decay > 0:
        robot.left_decay  -= 1
        robot.wall_left = True
    else:
        robot.wall_left = False
    if robot.right_decay > 0:
        robot.right_decay -= 1
        robot.wall_right = True
    else:
        robot.wall_right = False
    robot.wall_ahead = False
    
    #ARD sense data: 0 - immediate, 1 - 1 away, 2 - 2 away, 9 - no obstacles
    if robot.face == 'W':
        if y+2 in range(20):
            pt1 = mdp_map[y+2][x-1]
            pt4 = mdp_map[y+2][x]
            pt7 = mdp_map[y+2][x+1]
        else:
            pt1 = pt4 = pt7 = 'x'
        if y+3 in range(20):
            pt2 = mdp_map[y+3][x-1]
            pt5 = mdp_map[y+3][x]
            pt8 = mdp_map[y+3][x+1]
        else:
            pt2 = pt5 = pt8 = 'x'
        if y+4 in range(20):
            pt3 = mdp_map[y+4][x-1]
            pt6 = mdp_map[y+4][x]
            pt9 = mdp_map[y+4][x+1]
        else:
            pt3 = pt6 = pt9 = 'x'
        if x+2 in range(15):
            pt10 = mdp_map[y+1][x+2]
        else:
            pt10 = 'x'
        if x+3 in range(15):
            pt11 = mdp_map[y+1][x+3]
        else:
            pt11 = 'x'
        if x-2 in range(15):
            pt12 = mdp_map[y+1][x-2]
        else:
            pt12 = 'x'
        if x-3 in range(15):
            pt13 = mdp_map[y+1][x-3]
        else:
            pt13 = 'x'
    elif robot.face == 'A':
        if x-2 in range(15):
            pt1 = mdp_map[y-1][x-2]
            pt4 = mdp_map[y][x-2]
            pt7 = mdp_map[y+1][x-2]
        else:
            pt1 = pt4 = pt7 = 'x'
        if x-3 in range(15):
            pt2 = mdp_map[y-1][x-3]
            pt5 = mdp_map[y][x-3]
            pt8 = mdp_map[y+1][x-3]
        else:
            pt2 = pt5 = pt8 = 'x'
        if x-4 in range(15):
            pt3 = mdp_map[y-1][x-4]
            pt6 = mdp_map[y][x-4]
            pt9 = mdp_map[y+1][x-4]
        else:
            pt3 = pt6 = pt9 = 'x'
        if y+2 in range(20):
            pt10 = mdp_map[y+2][x-1]
        else:
            pt10 = 'x'
        if y+3 in range(20):
            pt11 = mdp_map[y+3][x-1]
        else:
            pt11 = 'x'
        if y-2 in range(20):
            pt12 = mdp_map[y-2][x-1]
        else:
            pt12 = 'x'
        if y-3 in range(20):
            pt13 = mdp_map[y-3][x-1]
        else:
            pt13 = 'x'
    elif robot.face == 'S':
        if y-2 in range(20):
            pt1 = mdp_map[y-2][x+1]
            pt4 = mdp_map[y-2][x]
            pt7 = mdp_map[y-2][x-1]
        else:
            pt1 = pt4 = pt7 = 'x'
        if y-3 in range(20):
            pt2 = mdp_map[y-3][x+1]
            pt5 = mdp_map[y-3][x]
            pt8 = mdp_map[y-3][x-1]
        else:
            pt2 = pt5 = pt8 = 'x'
        if y-4 in range(20):
            pt3 = mdp_map[y-4][x+1]
            pt6 = mdp_map[y-4][x]
            pt9 = mdp_map[y-4][x-1]
        else:
            pt3 = pt6 = pt9 = 'x'
        if x-2 in range(15):
            pt10 = mdp_map[y-1][x-2]
        else:
            pt10 = 'x'
        if x-3 in range(15):
            pt11 = mdp_map[y-1][x-3]
        else:
            pt11 = 'x'
        if x+2 in range(15):
            pt12 = mdp_map[y-1][x+2]
        else:
            pt12 = 'x'
        if x+3 in range(15):
            pt13 = mdp_map[y-1][x+3]
        else:
            pt13 = 'x'
    elif robot.face == 'D':
        if x+2 in range(15):
            pt1 = mdp_map[y+1][x+2]
            pt4 = mdp_map[y][x+2]
            pt7 = mdp_map[y-1][x+2]
        else:
            pt1 = pt4 = pt7 = 'x'
        if x+3 in range(15):
            pt2 = mdp_map[y+1][x+3]
            pt5 = mdp_map[y][x+3]
            pt8 = mdp_map[y-1][x+3]
        else:
            pt2 = pt5 = pt8 = 'x'
        if x+4 in range(15):
            pt3 = mdp_map[y+1][x+4]
            pt6 = mdp_map[y][x+4]
            pt9 = mdp_map[y-1][x+4]
        else:
            pt3 = pt6 = pt9 = 'x'
        if y-2 in range(20):
            pt10 = mdp_map[y-2][x+1]
        else:
            pt10 = 'x'
        if y-3 in range(20):
            pt11 = mdp_map[y-3][x+1]
        else:
            pt11 = 'x'
        if y+2 in range(20):
            pt12 = mdp_map[y+2][x+1]
        else:
            pt12 = 'x'
        if y+3 in range(20):
            pt13 = mdp_map[y+3][x+1]
        else:
            pt13 = 'x'

    try:
        if sensedata[0] == '9':
            pt1.explored = pt2.explored = pt3.explored = True
            pt1.text = pt2.text = pt3.text = ' '
        elif sensedata[0] == '2':
            pt1.explored = pt2.explored = True
            pt1.text = pt2.text = ' '
            if pt3 != 'x':
                pt3.explored = True
                pt3.text = 'W'
        elif sensedata[0] == '1':
            pt1.explored = True
            pt1.text = ' '
            if pt2 != 'x':
                pt2.explored = True
                pt2.text = 'W'
        elif sensedata[0] == '0':
            robot.wall_ahead = True
            if pt1 != 'x':
                pt1.explored = True
                pt1.text = 'W'
    except:
        print('Front sensor 1 input error')
            

    try:        
        if sensedata[1] == '9':
            pt4.explored = pt5.explored = pt6.explored = True
            pt4.text = pt5.text = pt6.text = ' '
        elif sensedata[1] == '2':
            pt4.explored = pt5.explored = True
            pt4.text = pt5.text = ' '
            if pt6 != 'x':
                pt6.explored = True
                pt6.text = 'W'
        elif sensedata[1] == '1':
            pt4.explored = True
            pt4.text = ' '
            if pt5 != 'x':
                pt5.explored = True
                pt5.text = 'W'
        elif sensedata[1] == '0':
            robot.wall_ahead = True
            if pt4 != 'x':
                pt4.explored = True
                pt4.text = 'W'
    except:
        print('Front sensor 2 input error')
            

    try:    
        if sensedata[2] == '9':
            pt7.explored = pt8.explored = pt9.explored = True
            pt7.text = pt8.text = pt9.text = ' '
        elif sensedata[2] == '2':
            pt7.explored = pt8.explored = True
            pt7.text = pt8.text = ' '
            if pt9 != 'x':
                pt9.explored = True
                pt9.text = 'W'
        elif sensedata[2] == '1':
            pt7.explored = True
            pt7.text = ' '
            if pt8 != 'x':
                pt8.explored = True
                pt8.text = 'W'
        elif sensedata[2] == '0':
            robot.wall_ahead = True
            if pt7 != 'x':
                pt7.explored = True
                pt7.text = 'W'
    except:
        print('Front sensor 3 input error')
        
    try:
        if sensedata[3] == '9':
            pt10.explored = pt11.explored = True
            pt10.text = pt11.text = ' '
        elif sensedata[3] == '1':
            pt10.explored = True
            pt10.text = ' '
            if pt11 != 'x':
                pt11.explored = True
                pt11.text = 'W'
        elif sensedata[3] == '0':
            robot.wall_right = True
            robot.right_decay = 2
            if pt10 != 'x':
                pt10.explored = True
                pt10.text = 'W'
    except:
        print('Right sensor input error')

    try:
        if sensedata[4] == '9':
            pt12.explored = pt13.explored = True
            pt12.text = pt13.text = ' '
        elif sensedata[4] == '1':
            pt12.explored = True
            pt12.text = ' '
            if pt13 != 'x':
                pt13.explored = True
                pt13.text = 'W'
        elif sensedata[4] == '0':
            robot.wall_left = True
            robot.left_decay = 2
            if pt12 != 'x':
                pt12.explored = True
                pt12.text = 'W'
    except:
        print('Left sensor input error')

        
    with open("realtimemap.txt","w") as text_file_sim:
        text_file_sim.write(print_alt_descriptor())
    mail.write('AND|'+ print_descriptor() + ';' + str(robot.coord[0]) + ';' + str(robot.coord[1]) + ';' + robot.face)

    if sensedata[5] == '7':
        return
    else:
        print('robot not ready')
        time.sleep(1)
        return

def step_eval(x, y, g):
    return (abs(g[0]-x) + abs(g[1]-y))

def h_eval(x, y, h):
    return (abs(x-h[0]) + abs(y-h[1]))

def explore(robot):
    path = []
    steps = 0
    right_wall_before = False
    goal_explored = False
    start_explored = False
    #right wall hug : ensure wall right is True as much as possible
    while robot.coord != start or (robot.coord == start and goal_explored == False) or (goal_explored == False and start_explored == False):
##        if steps == time_limit:
##            print('Time up!')
##            fastest_path(robot, robot.coord, start)
##            return
##        elif explore_percent() == explore_limit:
##            print('Explore limit reached!')
##            fastest_path(robot, robot.coord, start)
##            return
        if goal_explored == True and start_explored == True:
            print('Goal + Start explored; Proceeding back to start.')
            fastest_path(robot, robot.coord, start)
            return
##        print(steps)
        robot_sense(robot)
        steps += 1
        if robot.wall_right and not robot.wall_ahead:
            print('wr&~wa')
            robot_forward(robot)
            right_wall_before = True
            path.append(robot.face)
        elif robot.wall_right and robot.wall_ahead:
            print('wr&wa')
            robot_left(robot)
            right_wall_before = True
        elif robot.wall_ahead and not right_wall_before:
            print('wa&~rb')
            robot_left(robot)
            right_wall_before = False
        elif robot.wall_ahead and right_wall_before:
            print('wa&rb')
            robot_right(robot)
            right_wall_before = False
        elif not robot.wall_right and right_wall_before:
            print('~wr&rb')
            robot_right(robot)
            right_wall_before = False
        else:
            print('none')
            robot_forward(robot)
            right_wall_before = False
            path.append(robot.face)
        steps += 1
        if robot.coord == goal:
            goal_explored = True
        if robot.coord == start:
            start_explored = True
        #print_map()
##        with open("explore.txt","a") as text_file_explore:
##            text_file_explore.write(print_descriptor())
        with open("realtimemap.txt","w") as text_file_sim:
            text_file_sim.write(print_alt_descriptor())
        mail.write('AND|'+ print_descriptor() + ';' + str(robot.coord[0]) + ';' + str(robot.coord[1]) + ';' + robot.face)
        #print('=================================================')

##    while not fully_explored():
##        #print('Begin relocation routine.')
##        #print(robot.coord)
##        fastest_path(robot, robot.coord, to_explore(robot.coord))
##        robot_sense(robot)

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
    pathstring = ''
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
                pathstring += 'W'
                robot_forward(robot)
                path.pop(0)
            elif robot.face == 'W':
                if next_path == 'A':
                    pathstring += 'A'
                    robot_left(robot)
                elif next_path == 'D':
                    pathstring += 'D'
                    robot_right(robot)
                elif next_path == 'S':
                    pathstring += 'DD'
                    robot_right(robot)
                    robot_right(robot)
            elif robot.face == 'A':
                if next_path == 'S':
                    pathstring += 'A'
                    robot_left(robot)
                elif next_path == 'W':
                    pathstring += 'D'
                    robot_right(robot)
                elif next_path == 'D':
                    pathstring += 'DD'
                    robot_right(robot)
                    robot_right(robot)
            elif robot.face == 'S':
                if next_path == 'D':
                    pathstring += 'A'
                    robot_left(robot)
                elif next_path == 'A':
                    pathstring += 'D'
                    robot_right(robot)
                elif next_path == 'W':
                    pathstring += 'DD'
                    robot_right(robot)
                    robot_right(robot)
            elif robot.face == 'D':
                if next_path == 'W':
                    pathstring += 'A'
                    robot_left(robot)
                elif next_path == 'S':
                    pathstring += 'D'
                    robot_right(robot)
                elif next_path == 'A':
                    pathstring += 'DD'
                    robot_right(robot)
                    robot_right(robot)
            with open("realtimemap.txt","w") as text_file_sim:
                text_file_sim.write(print_alt_descriptor())
            mail.write('AND|'+ print_descriptor() + ';' + str(robot.coord[0]) + ';' + str(robot.coord[1]) + ';' + robot.face)
            #print_map()
                
    
def robot_forward(robot, text='W'):
    mail.write('ARD|' + text)
    ack = mail.read('ARD')
    while 'ACK' not in ack:
        mail.write('ARD|' + text)
        ack = mail.read('ARD')    
    robotcoord = robot[0]
    origincoord = Coordinates(robotcoord)
    #print(robot[0])
    robotface = robot.face
    if robotface == 'W':
        if robotcoord[1]+1 in range(20) and robotcoord[1]+2 in range(20):
            robotcoord[1] += 1
    elif robotface == 'A':
        if robotcoord[0]-1 in range(15) and robotcoord[0]-1 in range(15):
            robotcoord[0] -= 1
    elif robotface == 'S':
        if robotcoord[1]-1 in range(20) and robotcoord[1]-1 in range(20):
            robotcoord[1] -= 1
    elif robotface == 'D':
        if robotcoord[0]+1 in range(15) and robotcoord[0]+1 in range(15):
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
    mail.write('ARD|A')
    ack = mail.read('ARD')
    while 'ACK' not in ack:
        mail.write('ARD|A')
        ack = mail.read('ARD')
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
    robot.left_decay = 0
    robot.right_decay = 0

def robot_right(robot):
    mail.write('ARD|D')
    ack = mail.read('ARD')
    while 'ACK' not in ack:
        mail.write('ARD|D')
        ack = mail.read('ARD')
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
    robot.left_decay = 0
    robot.right_decay = 0

def place_obstacles():
    #accepts arena input, 0 for empty, 1 for wall
    #places walls in arena, and prints a hexstr of the arena
    #lines = []
    #for i in range(20):
    #    line = input('Simulation arena data, please')
    #    lines.append(line)
    string1 = bin(int(input('Map hexstring, please'), 16))[2:]
    string2 = string1[2:len(string1)-2]
    for j in range(20):
        for i in range(15):
            if string2[i+(j*15)] == '1':
                place_wall(i,j)
        
    
    #string = '\n'.join(lines)
    #string = ''.join(string.split())
    #obstacles = string.split()
    #for j in range(20):
    #    for i in range(15):
    #        if string[i+(j*15)] == '1':
    #            place_wall(i,j)
    hexstr = '%0*X' % ((len(string2)+3) // 4, int(string2, 2))
    print(hexstr)

if __name__ == "__main__":
    #main
    start = [1,1]
    goal = [13,18]
    mail = Algo()
    #string = input('Time limit?(m:ss)')
    #time_input = string.split(':')
    #time_limit = int(time_input[0])*60 + int(time_input[1])
    #explore_limit = int(input('Explore limit?(%)'))
    #print(time_limit)
    #print(explore_limit)
    
    
    mdp_map = []
    mdp_explore_map = []
    initialize_map()
    try:
        print('Robot data, please')
        rdata = mail.read('AND')
        print(rdata)
        robot = Robot([int(rdata[0]), int(rdata[1])],rdata[2])
        print(robot.coord)
        print(robot.face)
    except:
        print("robot initialization failed")
        exit()
    #obstacles
    #filename = 'D:\Python(3.6.4)\Practice\MDP21\MapSimulator\MapSimulator\PlayMapSimulator.html'
    #place_obstacles()
    place_robot(robot.coord)
    explore(robot)
    print_explored()
    print_map()
    print_descriptor()
    try:
        print('Waypoints, please.')
        rdata = mail.read('AND')
        waypoint = [int(rdata[0]), int(rdata[1])]
    except:
        print("Waypoint initialization failed, defaulting to start")
        waypoint = start
    if waypoint != start or waypoint != goal:
        fastest_path(robot, start, waypoint)
        fastest_path(robot, waypoint, end)
    else:
        fastest_path(robot, start, goal)
    #webbrowser.open('http://localhost/Projects/MapSimulator/PlayMapSimulator.html')


            
