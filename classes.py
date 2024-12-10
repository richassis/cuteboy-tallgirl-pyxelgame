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

        pyxel.image(0).load(0,0, "sprites.png")

        self.obstacles_matrix = np.zeros(self.screenDim, np.int16)
        
        self.obstacles_matrix = self.obstacles_matrix + self.add_rect_to_matrix(0, 60, self.floor_number, 236, 10)

        self.obstacles_matrix = self.obstacles_matrix + self.add_rect_to_matrix(20, 120, self.floor_number, 236, 10)
        
        self.obstacles_matrix = self.obstacles_matrix + self.add_rect_to_matrix(0, 180, self.floor_number, 236, 10)

        self.obstacles_matrix = self.obstacles_matrix + self.add_rect_to_matrix(0, 235, self.floor_number, 256, 10)

        list_sprites= [
            [0,0,10,30],
            [10,0,8,30],
            [18,0,13,30]
        ]
        self.avatar1 = Avatar(1, 1, 10, 30, self, ['W', 'A', 'S', 'D'], list_sprites)

       # self.avatar2 = Avatar(20, 1, 10, 25, self, ['UP', 'LEFT', 'DOWN', 'RIGHT'])

        self.screen_matrix = self.obstacles_matrix+self.avatar1.position_matrix#+self.avatar2.position_matrix

        pyxel.run(self.update, self.draw)
    

    def update(self):

        self.avatar1.update()
       # self.avatar2.update()


    def draw(self):
        pyxel.cls(0)
        pyxel.blt(20, 1, 0, 0, 0, 10, 30, 13)
        self.screen_matrix = self.obstacles_matrix + self.avatar1.position_matrix #+ self.avatar2.position_matrix
        # self.paint_screen(self.screen_matrix)

        self.matrix_to_txt(self.screen_matrix, 'screen_matrix')
    
        pass


    def add_rect_to_matrix(self, x, y, color, w=0, h=0):
        
        w = w if w else self.width
        h = h if h else self.width

        matrix = np.zeros(self.screenDim, np.int16)
        matrix[y:y+h, x:x+w] = color
        return matrix

    

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
    def __init__(self, initial_x, initial_y, avatar_width, avatar_height, Jogo, mov_keys, list_sprite) -> None:

        self.Jogo:Jogo = Jogo

        self.width = avatar_width
        self.height = avatar_height

        self.direcoes = list_sprite

        self.movement_keys = mov_keys

        self.x = initial_x
        self.y = initial_y

        self.screenDim = self.Jogo.screenDim

        self.position_matrix = self.Jogo.add_rect_to_matrix(self.x, self.y, self.Jogo.avatar_number, self.width, self.height)
        
        self.velocity = 1
        self.obstacles_matrix = self.Jogo.obstacles_matrix

        self.running = False

        self.jumping = False
        self.falling = False
        self.onFloor = False

        self.gravity_accel= 0.4
        self.jump_y0 = 0
        self.jump_vel = 5
        self.jump_t = 0
  

    def update(self):
            
            self.keyboard_movement()

            self.check_on_floor()

            if self.jumping:
               self.gravity()

            if not self.onFloor and not self.jumping:
                self.falling = True
                self.gravity()


            

    def add_rect_to_matrix(self, x, y, color):
        
        w = self.width
        h = self.height
        matrix = np.zeros(self.screenDim, np.int16)
        matrix[y:y+h, x:x+w] = color
        return matrix

    def keyboard_movement(self):

        if pyxel.btnp(getattr(pyxel, 'KEY_'+self.movement_keys[0])): #W
            self.jumping = True
           # self.gravity()
            # self.x, self.y = 
            #self.goto_position('y', -1)

        if pyxel.btn(getattr(pyxel, 'KEY_'+self.movement_keys[1])): #A
            # self.x, self.y = 
            self.goto_position('x', -self.velocity)
        
        
        if pyxel.btn(getattr(pyxel, 'KEY_'+self.movement_keys[2])): #S
            # self.x, self.y = 
            self.goto_position('y', self.velocity)

        if pyxel.btn(getattr(pyxel, 'KEY_' + self.movement_keys[3])): #D
            #self.x, self.y = 
            self.goto_position('x', self.velocity)

        if pyxel.btn(pyxel.KEY_SPACE):
            print(self.x, self.y)

        if pyxel.btn(pyxel.KEY_SHIFT):
            self.running = 3
        else:
            self.running = 1

    
    def goto_position(self, axis, distance):
        
        if axis=='x':
            target_y = self.y
            target_x = pyxel.ceil(self.x+(distance*self.running))
        else:
            target_y = pyxel.ceil(self.y+(distance*self.running))
            target_x = self.x

        if target_x+self.width>=self.screenDim[1] or target_x<0 or \
            target_y+self.height>=self.screenDim[0] or target_y<0:
            print(target_x<0,  target_y+self.height>=self.screenDim[0] or target_y<0)
            return [self.x, self.y]

        print(target_x, target_y)

        matrix_test = self.obstacles_matrix + self.Jogo.add_rect_to_matrix(target_x, target_y, self.Jogo.avatar_number, self.width, self.height)
        self.Jogo.matrix_to_txt(matrix_test, 'teste')

        # return [target_x, target_y]

        while np.count_nonzero(matrix_test==self.Jogo.floor_number+self.Jogo.avatar_number)!=0:
            
            fade = 1 if distance>0 else -1
            if axis=='x':
                target_x -= fade
            else:
                if fade==-1:
                    target_y = self.y
                else:
                    target_y -= fade

            matrix_test = self.obstacles_matrix + self.Jogo.add_rect_to_matrix(target_x, target_y, self.Jogo.avatar_number, self.width, self.height)
            self.Jogo.matrix_to_txt(matrix_test, 'teste')


        self.position_matrix = self.Jogo.add_rect_to_matrix(target_x, target_y, self.Jogo.avatar_number, self.width, self.height)

        self.x, self.y = target_x, target_y
        return [target_x, target_y]

        
            

    def check_on_floor(self):

        #print(self.Jogo.screen_matrix[self.y + self.height + 1, self.x:self.x+self.width].tolist())
        if self.Jogo.screen_matrix[self.y + self.height, self.x:self.x+self.width].tolist().count(self.Jogo.floor_number)==0:
            self.onFloor = False
        else:
            self.onFloor = True

    def gravity(self):

       
        
        if self.jump_t==0:
            self.jump_y0 = self.y
            self.jump_t+=1

        if self.falling: 
            self.real_jump_vel = 0
        else:
            self.real_jump_vel = self.jump_vel
        

        new_y = (self.jump_y0 - (self.real_jump_vel*self.jump_t) +  ((1/2)*(self.gravity_accel)*(self.jump_t**2)))

        print(self.jump_y0, self.jump_t, new_y, new_y-self.y, self.y)

        self.goto_position('y', new_y-self.y)   

        print(self.jump_y0, self.jump_t, new_y, new_y-self.y, self.y)

        self.jump_t += 1

        self.check_on_floor()

        if self.onFloor:
            self.jump_t=0
            self.jump_y0 = 0
            self.jumping=False
            self.falling=False
            return None


class Portal:

    def __init__(self, x1, y1, x2, y2, Jogo) -> None:

        self.Jogo:Jogo = Jogo

        self.width = 4
        self.height = 11

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.screenDim = self.Jogo.screenDim

        self.position_matrix = self.Jogo.add_rect_to_matrix(self.x, self.y, self.Jogo.avatar_number)
        
        self.velocity = 1
        self.obstacles_matrix = self.Jogo.obstacles_matrix



Jogo()

class Teste:
    
    def __init__(self) -> None:
        print('Teste')