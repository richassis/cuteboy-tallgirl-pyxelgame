# copilot: disable
import pyxel
import numpy as np
import time

class Jogo:
    def __init__(self) -> None:
        
        self.width = 256
        self.height = 256
        self.screenDim = (self.height, self.width)
        
        
        pyxel.init(self.width, self.height, title="Jogo", fps=60)

        self.obstacles_matrix = np.zeros(self.screenDim, np.int16)
        
        self.add_rect_to_matrix(0, 60, 236, 10, 2, self.obstacles_matrix)

        self.add_rect_to_matrix(20, 120, 236, 10, 2, self.obstacles_matrix)
        
        self.add_rect_to_matrix(0, 180, 236, 10, 2, self.obstacles_matrix)

        self.add_rect_to_matrix(0, 235, 256, 10, 2, self.obstacles_matrix)

        self.avatar1 = Avatar(1, 1, 10, 30, self.screenDim, self.obstacles_matrix, ['W', 'A', 'S', 'D'])

        self.avatar2 = Avatar(20, 1, 10, 25, self.screenDim, self.obstacles_matrix, ['UP', 'LEFT', 'DOWN', 'RIGHT'])

        self.screen_matrix = self.obstacles_matrix+self.avatar1.position_matrix+self.avatar2.position_matrix

        pyxel.run(self.update, self.draw)
    

    def update(self):

        self.avatar1.update()
        self.avatar2.update()


    def draw(self):
        pyxel.cls(0)

        self.screen_matrix = self.avatar1.position_matrix + self.avatar2.position_matrix + self.obstacles_matrix
        self.paint_screen(self.screen_matrix)

        self.matrix_to_txt(self.screen_matrix, 'screen_matrix')
    
        pass


    def add_rect_to_matrix(self, x, y, w, h, color, matrix):
        
        matrix[y:y+h, x:x+w] = color
        self.matrix_to_txt(matrix, 'teste.txt')
    

    def paint_screen(self, matrix):

        for y in range(self.height):
            for x in range(self.width):
                # if matrix[y,x]!=0:
                #print(x, y)
                pyxel.pset(x, y, matrix[y,x])

    
    def matrix_to_txt(self, matrix, filename):

        with open(filename+'.txt', 'w+') as f:
            for line in matrix:
                f.write(' '.join([str(int(h)) for h in line]) + '\n')        


class Avatar:
    def __init__(self, initial_x, initial_y, avatar_width, avatar_height, screendimension, obstacles_matrix, mov_keys) -> None:

        self.width = avatar_width
        self.height = avatar_height

        self.movement_keys = mov_keys

        self.x = initial_x
        self.y = initial_y

        self.screenDim = screendimension

        self.position_matrix = self.add_rect_to_matrix(self.x, self.y, 1)
        
        self.velocity = 1
        self.obstacles_matrix = obstacles_matrix

        self.jump_height = 40
        self.jumping_left = 0
  

    def update(self):
            
            self.keyboard_movement()

            if self.jumping_left > (-self.jump_height):
                self.jump()

    def add_rect_to_matrix(self, x, y, color):
        
        w = self.width
        h = self.height
        matrix = np.zeros(self.screenDim, np.int16)
        matrix[y:y+h, x:x+w] = color
        return matrix

    def keyboard_movement(self):


        if pyxel.btn(getattr(pyxel, 'KEY_' + self.movement_keys[3])): #D
            self.x, self.y = self.goto_position(self.x+self.velocity, self.y)

        if pyxel.btn(getattr(pyxel, 'KEY_'+self.movement_keys[1])): #A
            self.x, self.y = self.goto_position(self.x-self.velocity, self.y)
            
        if pyxel.btnp(getattr(pyxel, 'KEY_'+self.movement_keys[0])): #W
            self.jumping_left = self.jump_height
           # self.x, self.y = self.goto_position(self.x, self.y-self.velocity)
        
        if pyxel.btn(getattr(pyxel, 'KEY_'+self.movement_keys[2])): #S
            self.x, self.y = self.goto_position(self.x, self.y+self.velocity)

        if pyxel.btn(pyxel.KEY_SPACE):
            print(self.x, self.y)

        if pyxel.btn(pyxel.KEY_SHIFT):
            self.velocity = self.velocity*2

    def jump(self):
        
        if self.jumping_left > 0:
            i = 1
        else:
            i = -1
            
        self.x, self.y = self.goto_position(self.x, self.y - i)
        self.jumping_left -= 1

            #print(self.y)        

    
    def goto_position(self, target_x, target_y):

        if target_x+self.width>=self.screenDim[1] or target_x<0 or \
            target_y+self.height>=self.screenDim[0] or target_y<0:
            return [self.x, self.y]
        
        matrix_test = self.obstacles_matrix + self.add_rect_to_matrix(target_x, target_y, 1)

        # return [target_x, target_y]
        if np.count_nonzero(matrix_test==3)==0:
            self.position_matrix = self.add_rect_to_matrix(target_x, target_y, 1)
            return [target_x, target_y]
        else:
            return [self.x, self.y]


class CircleAvatar:
    def __init__(self, initial_x, initial_y, radius, screendimension, obstacles_matrix) -> None:

        self.radius = radius
        self.x = initial_x
        self.y = initial_y
        self.screenDim = screendimension
        self.position_matrix = self.add_circle_to_matrix(self.x, self.y)
        self.velocity = 1
        self.obstacles_matrix = obstacles_matrix

        self.jump_height = 20
        self.jumping_left = 0
  

    def update(self):
            
            self.keyboard_movement()

            if self.jumping_left > (-self.jump_height):
                self.jump()

    def add_circle_to_matrix(self, h, k):

        matrix = np.zeros(self.screenDim, np.int16)
        for y in range(k-self.radius, k+self.radius+1):
            for x in range(h-self.radius, h+self.radius+1):
                coord = ((x-h)**2) + ((y-k)**2)
                if coord <= (self.radius**2)+1:
                    matrix[y, x]+=1

        return matrix

    def keyboard_movement(self):

        if pyxel.btn(pyxel.KEY_D):
            self.x, self.y = self.goto_position(self.x+self.velocity, self.y)

        if pyxel.btn(pyxel.KEY_A):
            self.x, self.y = self.goto_position(self.x-self.velocity, self.y)
            
        if pyxel.btnp(pyxel.KEY_W):
            self.jumping_left = self.jump_height
           # self.x, self.y = self.goto_position(self.x, self.y-self.velocity)
        
        if pyxel.btn(pyxel.KEY_S): 
            self.x, self.y = self.goto_position(self.x, self.y+self.velocity)

        if pyxel.btn(pyxel.KEY_SPACE):
            print(self.x, self.y)

        if pyxel.btn(pyxel.KEY_SHIFT):
            self.velocity = self.velocity*2

    def jump(self):
        
        if self.jumping_left > 0:
            i = 1
        else:
            i = -1
            
        self.x, self.y = self.goto_position(self.x, self.y - i)
        self.jumping_left -= 1

            #print(self.y)        

    
    def goto_position(self, target_x, target_y):

        if target_x+self.radius>=self.screenDim[1] or target_x-self.radius<0 or \
            target_y+self.radius>=self.screenDim[0] or target_y-self.radius<0:
            return [self.x, self.y]
        
        matrix_test = self.obstacles_matrix + self.add_circle_to_matrix(target_x, target_y)

        # return [target_x, target_y]
        if np.count_nonzero(matrix_test==2)==0:
            self.position_matrix = self.add_circle_to_matrix(target_x, target_y)
            return [target_x, target_y]
        else:
            return [self.x, self.y]

Jogo()

class Teste:
    
    def __init__(self) -> None:
        print('Teste')