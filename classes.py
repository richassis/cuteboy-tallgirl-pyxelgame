# copilot: disable
import pyxel
import numpy as np
import time

class Jogo:
    def __init__(self) -> None:
        
        self.width = 256
        self.height = 256
        self.screenDim = (self.height, self.width)
        
        self.floor_number = 2
        self.avatar_number = 1
        
        pyxel.init(self.width, self.height, title="Jogo", fps=60)

        self.obstacles_matrix = np.zeros(self.screenDim, np.int16)
        
        self.add_rect_to_matrix(0, 60, 236, 10, self.floor_number, self.obstacles_matrix)

        self.add_rect_to_matrix(20, 120, 236, 10, self.floor_number, self.obstacles_matrix)
        
        self.add_rect_to_matrix(0, 180, 236, 10, self.floor_number, self.obstacles_matrix)

        self.add_rect_to_matrix(0, 235, 256, 10, self.floor_number, self.obstacles_matrix)

        self.avatar1 = Avatar(1, 1, 10, 30, self, ['W', 'A', 'S', 'D'])

       # self.avatar2 = Avatar(20, 1, 10, 25, self, ['UP', 'LEFT', 'DOWN', 'RIGHT'])

        self.screen_matrix = self.obstacles_matrix+self.avatar1.position_matrix#+self.avatar2.position_matrix

        pyxel.run(self.update, self.draw)
    

    def update(self):

        self.avatar1.update()
       # self.avatar2.update()


    def draw(self):
        pyxel.cls(0)

        self.screen_matrix = self.obstacles_matrix + self.avatar1.position_matrix #+ self.avatar2.position_matrix
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
    def __init__(self, initial_x, initial_y, avatar_width, avatar_height, Jogo, mov_keys) -> None:

        self.Jogo = Jogo

        self.width = avatar_width
        self.height = avatar_height

        self.movement_keys = mov_keys

        self.x = initial_x
        self.y = initial_y

        self.screenDim = self.Jogo.screenDim

        self.position_matrix = self.add_rect_to_matrix(self.x, self.y, self.Jogo.avatar_number)
        
        self.velocity = 1
        self.obstacles_matrix = self.Jogo.obstacles_matrix

        self.jumping = False
        self.falling = False
        self.onFloor = False

        self.gravity_accel= 0.1
        self.jump_y0 = 0
        self.jump_vel = 3
        self.jump_t = 0
  

    def update(self):
            
            self.keyboard_movement()
            
            if not self.onFloor:
                self.gravity()

            self.check_on_floor()

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
            self.jumping = True
           # self.x, self.y = self.goto_position(self.x, self.y-self.velocity)
        
        if pyxel.btn(getattr(pyxel, 'KEY_'+self.movement_keys[2])): #S
            self.x, self.y = self.goto_position(self.x, self.y+self.velocity)

        if pyxel.btn(pyxel.KEY_SPACE):
            print(self.x, self.y)

        if pyxel.btn(pyxel.KEY_SHIFT):
            self.velocity = self.velocity*2      

    
    def goto_position(self, target_x, target_y):

        if target_x+self.width>=self.screenDim[1] or target_x<0 or \
            target_y+self.height>=self.screenDim[0] or target_y<0:
            return [self.x, self.y]
        
        matrix_test = self.obstacles_matrix + self.add_rect_to_matrix(target_x, target_y, self.Jogo.avatar_number)

        # return [target_x, target_y]
        if np.count_nonzero(matrix_test==self.Jogo.floor_number+self.Jogo.avatar_number)==0:
            self.position_matrix = self.add_rect_to_matrix(target_x, target_y, self.Jogo.avatar_number)
            return [target_x, target_y]
        else:

            return [self.x, self.y]

    def check_on_floor(self):

        #print(self.Jogo.screen_matrix[self.y + self.height + 1, self.x:self.x+self.width].tolist())
        if self.Jogo.screen_matrix[self.y + self.height + 1, self.x:self.x+self.width].tolist().count(self.Jogo.floor_number)==0:
            self.onFloor = False
        else:
            self.onFloor = True

        # print(self.onFloor)

    def gravity(self):
        
        if self.jump_t==0:
            self.jump_y0 = self.y  

        if self.falling: 
            self.real_jump_vel = 0
            new_y = (self.jump_y0 + (self.real_jump_vel*self.jump_t) -  ((1/2)*(self.gravity_accel)*(self.jump_t**2)))
        else:
            self.real_jump_vel = self.jump_vel
            new_y = (self.jump_y0 - (self.real_jump_vel*self.jump_t) +  ((1/2)*(self.gravity_accel)*(self.jump_t**2)))

        self.x, self.y = self.goto_position(self.x, int(new_y))   

        print(self.jump_y0, self.jump_t, self.y)

        self.jump_t += 1

        if self.onFloor:
            self.jump_t=0
            self.jump_y0 = 0
            self.jumping=False
            self.falling=False

        

             


Jogo()

class Teste:
    
    def __init__(self) -> None:
        print('Teste')