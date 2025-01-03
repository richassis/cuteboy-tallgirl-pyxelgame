# copilot: disable
import pyxel
import numpy as np
import time
from Imagem import ImagemPPM as imgppg

class Jogo:
    def __init__(self) -> None:
        
        #DEFINIÇÕES DE DIMENSÕES DO JOGO
        self.width = 256
        self.height = 256
        self.screenDim = (self.height, self.width)
        
        #DEFINIÇÕES DOS NUMEROS DE CADA OBJETO NA MATRIZ
        self.background_number = 0
        self.floor_number = 3
        self.avatar_number = 1

        #CRIAR MATRIZ COM OS OBSTACULOS (CHÃO)
        self.obstacles_matrix = np.zeros(self.screenDim, np.int16)
        
        #INICIALIZA PYXEL
        pyxel.init(self.width, self.height, title="Jogo", fps=60)

        #CARREGA A SPRITE E DEFINE OS INTERVALOS DAS ANIMAÇÕES DOS AVATARES
        self.image_buffer = 0
        
        pyxel.images[self.image_buffer].load(0,0, "sprites.png")
        
        self.background_remove = 13

        self.avatar1 = Avatar('tallgirl', 1, 1, 10, 30, self, ['W', 'A', 'S', 'D'])

        self.avatar2 = Avatar('cuteboy', 20, 1, 10, 25, self, ['UP', 'LEFT', 'DOWN', 'RIGHT'])
        
        self.avatars_matrix = self.avatar1.position_matrix+self.avatar2.position_matrix

        self.construct_map_objects(1)

        #RODAR JOGO
        pyxel.run(self.update, self.draw)


    def construct_map_objects(self, level):
        
        match level:
            case 1:
                
                pgm = imgppg("obstacles.pgm")
                self.obstacles_matrix = np.where(pgm.matrix == 1, self.floor_number, pgm.matrix)

                self.gate1 = GateSystem('purple', self, buttons=[[1, 59], [110, 59]], gates=[[100, 32, 0, 'ver'], [230, 62, 1, 'hor']])

                self.gate2 = GateSystem('green', self, buttons=[[150, 59]], levers=[[210, 52]], gates=[[200, 32, 0, 'ver']])



    def update(self):
        
        self.screen_matrix = self.obstacles_matrix.copy()

        self.gate1.update()
        self.gate2.update()

        self.avatar1.update()
        self.avatar2.update()
        self.avatars_matrix = self.avatar1.position_matrix+self.avatar2.position_matrix

        # self.matrix_to_txt(self.avatars_matrix, 'testenew')




    def draw(self):
        pyxel.cls(0)

        self.avatar1.draw()
        self.avatar2.draw()
        
        self.paint_screen(self.obstacles_matrix)
        
        self.gate1.draw()
        self.gate2.draw()
        
    
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
                if not matrix[y,x] in [self.background_number, self.avatar_number]:
                    pyxel.pset(x, y, matrix[y,x])

    
    def matrix_to_txt(self, matrix, filename):
        
        with open(filename+'.txt', 'w+') as f:
           for line in matrix:
               f.write(' '.join([str(int(h)) for h in line]) + '\n')        



class Avatar:
    def __init__(self, avatar, initial_x, initial_y, avatar_width, avatar_height, Jogo, mov_keys) -> None:

        self.avatar = avatar

        self.Jogo:Jogo = Jogo

        self.width = avatar_width
        self.height = avatar_height

        if self.avatar == 'tallgirl':
            self.direcoes= [
                [0,0,10,30], #frente
                [10,0,8,30], #lado direito com perna fechada 
                [18,0,13,30], #lado direito com perna aberta
                [10,0,-8,30], #lado direito com perna fechada
                [18,0,-13,30] #lado direito com perna aberta
            ]
        else:
            self.direcoes= [
                [0,30,10,25], #frente
                [10,30,8,25], #lado direito com perna fechada 
                [18,30,13,25], #lado direito com perna aberta
                [10,30,-8,25], #lado direito com perna fechada 
                [18,30,-13,25] #lado direito com perna aberta
            ]

        self.direcao_sprite = 0
        self.animation_cap = 7
        self.animation_it = 0

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
        self.underCeiling = False
        self.rightWall = False
        self.leftWall = False

        self.gravity_accel= 0.35
        self.jump_y0 = 0
        self.jump_vel = 8
        self.jump_t = 0
        self.fall_speed = 0
  

    def update(self):
        self.keyboard_movement()

        if self.jumping or self.falling:
            self.gravity()

        if not self.onFloor and not self.jumping and not self.falling:
            self.falling = True
            self.gravity()

        self.position_matrix = self.Jogo.add_rect_to_matrix(self.x, self.y, self.Jogo.avatar_number, self.width, self.height)

    def draw(self):

        self.draw_avatar()


    def draw_avatar(self):

        posicao_atual = self.direcoes[self.direcao_sprite]

        pyxel.blt(self.x, self.y, self.Jogo.image_buffer,
                   posicao_atual[0], posicao_atual[1], posicao_atual[2], posicao_atual[3], self.Jogo.background_remove)

    def add_rect_to_matrix(self, x, y, color):
        
        w = self.width
        h = self.height
        matrix = np.zeros(self.screenDim, np.int16)
        matrix[y:y+h, x:x+w] = color
        return matrix

    def keyboard_movement(self):

        if pyxel.btnp(getattr(pyxel, 'KEY_'+self.movement_keys[0])): #W
            self.jump()

        if pyxel.btn(getattr(pyxel, 'KEY_'+self.movement_keys[1])): #A

            self.movement_animation('left')

            self.update_position(self.x-self.velocity, self.y)
        

        if pyxel.btn(getattr(pyxel, 'KEY_' + self.movement_keys[3])): #D

            self.movement_animation('right')

            self.update_position(self.x+self.velocity, self.y)

        if pyxel.btn(pyxel.KEY_SPACE):
            A=0
        #    print(self.x, self.y)

        if pyxel.btn(pyxel.KEY_SHIFT):
            self.running = 3
        else:
            self.running = 1


    def update_position(self, target_x, target_y):
        increment = 1  # Tamanho do incremento para verificar colisão
        steps_x = abs(target_x - self.x)  # Número de passos a serem dados no eixo x
        steps_y = abs(target_y - self.y)  # Número de passos a serem dados no eixo y
        direction_x = 1 if target_x > self.x else -1  # Direção do movimento no eixo x
        direction_y = 1 if target_y > self.y else -1  # Direção do movimento no eixo y

        for _ in range(max(steps_x, steps_y)):
            if steps_x > 0:
                next_x = self.x + direction_x * increment
            else:
                next_x = self.x

            if steps_y > 0:
                next_y = self.y + direction_y * increment
            else:
                next_y = self.y

            if next_x + self.width >= self.screenDim[1] or next_x < 0 or \
               next_y + self.height >= self.screenDim[0] or next_y < 0:
                break

            avatar_bottom_border = self.Jogo.screen_matrix[next_y + self.height, next_x:next_x + self.width].tolist()
            avatar_top_border = self.Jogo.screen_matrix[next_y, next_x:next_x + self.width].tolist()
            avatar_right_border = self.Jogo.screen_matrix[next_y:next_y + self.height, next_x + self.width].tolist()
            avatar_left_border = self.Jogo.screen_matrix[next_y:next_y + self.height, next_x].tolist()

            self.rightWall = False
            self.leftWall = False
            self.onFloor = False
            self.underCeiling = False

            if avatar_right_border.count(self.Jogo.floor_number) > 0:
                self.rightWall = True
            elif avatar_left_border.count(self.Jogo.floor_number) > 0:
                self.leftWall = True
            if avatar_bottom_border.count(self.Jogo.floor_number) > 0:
                self.onFloor = True
            elif avatar_top_border.count(self.Jogo.floor_number) > 0:
                self.underCeiling = True

            if not self.onFloor and not self.underCeiling and not self.rightWall and not self.leftWall:
                self.x, self.y = next_x, next_y
            else:
                break

        return [self.x, self.y]

        
    def movement_animation(self, dir):

        match dir:
            case 'right':
                perna_fechada = 1
                perna_aberta = 2
            
            case 'left':
                perna_fechada = 3
                perna_aberta = 4

        self.animation_it+=1
            
        if self.direcao_sprite != perna_fechada and self.direcao_sprite != perna_aberta:
            self.direcao_sprite = perna_aberta
        
        else:
            
            if self.animation_it > self.animation_cap:

                if self.direcao_sprite == perna_aberta:
                    if not self.jumping: self.direcao_sprite = perna_fechada

                else: 
                    self.direcao_sprite = perna_aberta

                self.animation_it = 0

    def gravity(self):
        gravity_force = 1 
        max_fall_speed = 5 

        self.fall_speed = min(self.fall_speed + gravity_force, max_fall_speed)

        target_y = self.y + self.fall_speed

        self.update_position(self.x, target_y)

        if self.onFloor:
            self.fall_speed = 0
            self.jumping = False
            self.falling = False


    def jump(self):
        if self.onFloor and not self.jumping:
            self.jumping = True
            self.fall_speed = -13
    


class GateSystem:

    def __init__(self, id, Jogo, gates, buttons=[], levers=[]):
        
        self.id = id
        self.Jogo = Jogo

        self.objects = []

        for params in buttons:
            self.objects.append(Button(params[0], params[1], self.Jogo, self))
            
        for params in levers:
            self.objects.append(Lever(params[0], params[1], self.Jogo, self))

        for params in gates:
            self.objects.append(Gate(params[0], params[1], params[2], params[3], self.Jogo, self))

        self.state = 0 #0- não pressionado, 1-pressionado

        pass

    def update(self):
        
        self.state = 0
        for obj in self.objects:
            obj.update()
            if self.state==0: self.state = obj.state

    def draw(self):

        for obj in self.objects:
            obj.draw()



class Button:
    
    def __init__(self, x, y, Jogo, gateSystem):
        
        self.Jogo = Jogo
        self.gateSystem = gateSystem

        self.x = x
        self.y = y

        self.width = 10
        self.height = 3

        self.state = 0

        match self.gateSystem.id:
            case 'green':
                self.animation = [
                    [31, 49],
                    [41, 49]
                    ]
            case 'purple':
                self.animation = [
                    [31, 52],
                    [41, 52]
                ]
        
        pass


    def update(self):

        button_area_matrix = self.Jogo.avatars_matrix[self.y:self.y+self.height, self.x:self.x+self.width]
        
        if np.count_nonzero(button_area_matrix)>self.width*self.height/3:

            self.state = 1

        else:

            self.state = 0

        pass

    def draw(self):

        posicao_atual = self.animation[self.state]

        pyxel.blt(self.x, self.y, self.Jogo.image_buffer,
                   posicao_atual[0], posicao_atual[1], self.width, self.height, self.Jogo.background_remove)
        pass

class Lever:

    def __init__(self, x, y, Jogo, gateSystem):
        
        self.Jogo = Jogo
        self.gateSystem = gateSystem

        self.x = x
        self.y = y

        self.width = 10
        self.height = 10

        self.onTop = True
        self.state = 0

        match self.gateSystem.id:
            case 'green':
                self.animation = [
                    [41, 19],
                    [41, 29]
                    ]
            case 'purple':
                self.animation = [
                    [31, 39],
                    [41, 39]
                ]
        
        pass


    def update(self):
        
        button_area_matrix = self.Jogo.avatars_matrix[self.y:self.y+self.height, self.x:self.x+self.width]     

        if np.count_nonzero(button_area_matrix)>self.width*self.height/3:
            
            if self.onTop==False:

                self.state = not self.state
                self.onTop = True
        else:

            self.onTop = False
        

    def draw(self):

        posicao_atual = self.animation[self.state]

        pyxel.blt(self.x, self.y, self.Jogo.image_buffer,
                   posicao_atual[0], posicao_atual[1], self.width, self.height, self.Jogo.background_remove)
        pass


class Gate:
    
    def __init__(self, x, y, type, direction, Jogo, gateSystem):
        
        self.Jogo = Jogo
        self.gateSystem = gateSystem

        self.x = x
        self.y = y
        self.type = type #type==0 -> normalmente fechado// type==1 -> normalmente aberto 
        self.direction = direction

        self.width = 3
        self.height = 30

        self.matrix = np.zeros(self.Jogo.screenDim, np.int16)
        self.state = 0

        match self.gateSystem.id:
            case 'green':
                self.animation = [
                    [34, 0],
                    
                    ]
            case 'purple':
                self.animation = [
                    [31, 0]
                ]
        
        pass


    def update(self):  

        self.state = not self.gateSystem.state if self.type else self.gateSystem.state

        match self.direction:
            case 'ver':
                new_x = self.x
                new_y = self.y if self.state == 0 else self.y - self.height - 5

                self.Jogo.screen_matrix[new_y:new_y+self.height, new_x:new_x+self.width] = self.Jogo.floor_number

            case 'hor':
                new_x = self.x if self.state == 0 else self.x-self.height-5
                new_y = self.y

                # Ajustar as coordenadas de origem para rotação de 90 graus
                
                self.Jogo.screen_matrix[new_y:new_y+self.width, new_x:new_x+self.height] = self.Jogo.floor_number

        

        # self.Jogo.screen_matrix = self.Jogo.screen_matrix + self.matrix
        
        
        pass

    def draw(self):
        posicao_atual = self.animation[0]
        u = posicao_atual[0]
        v = posicao_atual[1]
        
        match self.direction:
            case 'ver':
                new_x = self.x
                new_y = self.y if self.state == 0 else self.y - self.height - 5

                pyxel.blt(new_x, new_y, self.Jogo.image_buffer, u, v, self.width, self.height, self.Jogo.background_remove)

            case 'hor':
                new_x = self.x if self.state == 0 else self.x-self.height-5
                new_y = self.y

                # Ajustar as coordenadas de origem para rotação de 90 graus
                
                self.draw_rotated_90(new_x, new_y, self.Jogo.image_buffer, u, v, self.width, self.height, self.Jogo.background_remove)

        
            
    def draw_rotated_90(self, x, y, img, u, v, w, h, colkey):
        for i in range(w):
            for j in range(h):
                color = pyxel.image(img).pget(u + i, v + j)
                pyxel.pset(x + j, y + (w - 1 - i), color)                

        # self.Jogo.matrix_to_txt(self.Jogo.screen_matrix, 'newmatrix')
        
        pass



class Portal:

    def __init__(self, id, x, y, Jogo) -> None:

        self.Jogo:Jogo = Jogo

        self.width = 4
        self.height = 11

        self.id = id

        self.x = x
        self.y = y

        self.screenDim = self.Jogo.screenDim


Jogo()

class Teste:
    
    def __init__(self) -> None:

        print('Teste')