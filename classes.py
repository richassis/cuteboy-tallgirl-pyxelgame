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
        self.floor_number = 2
        self.avatar_number = 1

        #CRIAR MATRIZ COM OS OBSTACULOS (CHÃO)
        self.obstacles_matrix = np.zeros(self.screenDim, np.int16)
        self.obstacles_matrix = imgppg("obstacles.pgm").matrix
        
        #INICIALIZA PYXEL
        pyxel.init(self.width, self.height, title="Jogo", fps=60)

        #CARREGA A SPRITE E DEFINE OS INTERVALOS DAS ANIMAÇÕES DOS AVATARES
        self.image_buffer = 0
        
        pyxel.image(self.image_buffer).load(0,0, "sprites.png")
        
        self.background_remove = 13

        avatar1_animations= [
            [0,0,10,30], #frente
            [10,0,8,30], #lado direito com perna fechada 
            [18,0,13,30], #lado direito com perna aberta
            [10,0,-8,30], #lado direito com perna fechada
            [18,0,-13,30] #lado direito com perna aberta
        ]

        avatar2_animations= [
            [0,30,10,25], #frente
            [10,30,8,25], #lado direito com perna fechada 
            [18,30,13,25], #lado direito com perna aberta
            [10,30,-8,25], #lado direito com perna fechada 
            [18,30,-13,25] #lado direito com perna aberta
        ]


        self.avatar1 = Avatar('tallgirl', 1, 1, 10, 30, self, ['W', 'A', 'S', 'D'], avatar1_animations)

        self.avatar2 = Avatar('cuteboy', 20, 1, 10, 25, self, ['UP', 'LEFT', 'DOWN', 'RIGHT'], avatar2_animations)

        self.screen_matrix = self.obstacles_matrix #+self.avatar1.position_matrix+self.avatar2.position_matrix


        #RODAR JOGO
        pyxel.run(self.update, self.draw)


    def update(self):

        self.avatar1.update()
        self.avatar2.update()


    def draw(self):
        pyxel.cls(0)

        self.avatar1.draw()
        self.avatar2.draw()

        #self.screen_matrix = self.obstacles_matrix #+ self.avatar1.position_matrix + self.avatar2.position_matrix
        
        self.paint_screen(self.obstacles_matrix)

        # self.matrix_to_txt(self.screen_matrix, 'screen_matrix')
    
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
    def __init__(self, avatar, initial_x, initial_y, avatar_width, avatar_height, Jogo, mov_keys, list_sprite) -> None:

        self.avatar = avatar

        self.Jogo:Jogo = Jogo

        self.width = avatar_width
        self.height = avatar_height

        self.direcoes = list_sprite
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

    
    def goto_position(self, axis, distance):
        increment = 1  # Tamanho do incremento para verificar colisão
        steps = int(abs(distance))  # Número de passos a serem dados
        direction = 1 if distance > 0 else -1  # Direção do movimento

        for _ in range(steps):
            if axis == 'x':
                target_x = self.x + direction * increment
                target_y = self.y
            elif axis == 'y':
                target_x = self.x
                target_y = self.y + direction * increment

            if target_x + self.width >= self.screenDim[1] or target_x < 0 or \
            target_y + self.height >= self.screenDim[0] or target_y < 0:
                break

            avatar_bottom_border = self.Jogo.screen_matrix[target_y + self.height, target_x:target_x + self.width].tolist()
            avatar_top_border = self.Jogo.screen_matrix[target_y, target_x:target_x + self.width].tolist()
            avatar_right_border = self.Jogo.screen_matrix[target_y:target_y + self.height, target_x + self.width].tolist()
            avatar_left_border = self.Jogo.screen_matrix[target_y:target_y + self.height, target_x].tolist()

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
                self.x, self.y = target_x, target_y
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
        gravity_force = 1  # Força da gravidade por incremento
        max_fall_speed = 5  # Velocidade máxima de queda

        # Incrementar a velocidade de queda até o máximo permitido
        self.fall_speed = min(self.fall_speed + gravity_force, max_fall_speed)

        # Calcular a nova posição y
        target_y = self.y + self.fall_speed

        # Atualizar a posição usando a nova função
        self.update_position(self.x, target_y)

        if self.onFloor:
            self.fall_speed = 0
            self.jumping = False
            self.falling = False


    def jump(self):
        if self.onFloor and not self.jumping:
            self.jumping = True
            self.fall_speed = -13  # Velocidade inicial do salto

    

    




class Portal:

    def __init__(self, id, x, y, Jogo) -> None:

        self.Jogo:Jogo = Jogo

        self.width = 4
        self.height = 11

        self.id = id

        self.x = x
        self.y = y

        self.screenDim = self.Jogo.screenDim

        self.position_matrix = self.Jogo.add_rect_to_matrix(self.x, self.y, self.Jogo.avatar_number)
        

class Button:
    
    def __init__(self, id, x, y, Jogo):

        self.id = id

        self.x = x
        self.y = y

        self.Jogo = Jogo
        pass

class Lever:

    def __init__(self, id, x, y, Jogo):

        self.id = id

        self.x = x
        self.y = y

        self.Jogo = Jogo
        pass

class Gate:
    
    def __init__(self, id, x, y, Jogo):

        self.id = id

        self.x = x
        self.y = y

        self.Jogo = Jogo
        pass



Jogo()

class Teste:
    
    def __init__(self) -> None:

        print('Teste')