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

        #TEMPORIZADOR
        self.fps= 60
        self.time = 0
        self.timer= self.fps*self.time
        self.pause = False

        self.ignore_timer = False

        #INTERFACE
        self.estado= 'menu'
        self.menu = Menu()
        self.escolhaLevel= EscolhaLevel()
        self.pauseMenu = PauseMenu()
        self.level = 1
        
        #DEFINIÇÕES DOS NUMEROS DE CADA OBJETO NA MATRIZ
        self.background_number = 0
        self.floor_number = 1
        self.avatars_matrix_number = [2,3]
        
        #INICIALIZA PYXEL
        pyxel.init(self.width, self.height, title="Jogo", fps=self.fps)

        #CARREGA A SPRITE E DEFINE OS INTERVALOS DAS ANIMAÇÕES DOS AVATARES
        self.image_buffer = 0
        
        pyxel.images[self.image_buffer].load(0,0, "sprites.png")
        
        self.background_remove = 13

        #CRIAR MATRIZ COM OS OBSTACULOS (CHÃO)
        self.obstacles_matrix = None
        self.obstacles_matrix_reduced = None


        #AVATARES
        self.avatars = []
        self.doors = []

        #MAP OBJECTS
        self.objects = []

        #RODAR JOGO
        pyxel.run(self.update, self.draw)

    def restart(self): #resetar e voltar pra posição inicial
        self.timer = self.fps*self.time
        
        for avatar in self.avatars:
            avatar.restart()

        for obj in self.objects:
            obj.reset()
        

    def create_avatars(self):

        avatar1 = Avatar('tallgirl', 10, 30, self, ['W', 'A', 'S', 'D'], self.avatars_matrix_number[0])

        avatar2 = Avatar('cuteboy', 10, 25, self, ['UP', 'LEFT', 'DOWN', 'RIGHT'], self.avatars_matrix_number[1])

        self.avatars = [avatar1, avatar2]
        
        self.avatars_matrix = sum(avatar.position_matrix for avatar in self.avatars)


    def load_map(self):
        
        self.objects = []
        self.doors = []


        match self.level:
            case 0:
                
                #avatares
                self.avatars[0].set_initial_position(1, 8)
                self.avatars[1].set_initial_position(20, 8)


                #objetos

                pgm = imgppg("obstacles2.pgm")
                
                self.obstacles_matrix_reduced = pgm.matrix
                replication_matrix = np.ones((8, 8), dtype=np.int16)

                self.obstacles_matrix = np.kron(self.obstacles_matrix_reduced, replication_matrix)

                gate1 = GateSystem('purple', self, buttons=[[1, 59], [110, 59]], gates=[[100, 32, 0, 'ver', False], [230, 62, 1, 'hor', False]])
                gate2 = GateSystem('green', self, buttons=[[150, 59]], levers=[[210, 52]], gates=[[200, 32, 0, 'ver', False]])

                portal1 = PortalSystem(self.avatars[0], [[35, 1, 'right'], [65, 140, 'left']], self, buttons=[[85, 59]])

                spike1 = Spike(125, 178, self)

                self.objects.append(gate1)
                self.objects.append(gate2)
                self.objects.append(portal1)
                self.objects.append(spike1)

                door1 = FinalDoor(3, 218, self.avatars[0], self)
                door2 = FinalDoor(20, 223, self.avatars[1], self)

                self.doors.append(door1)
                self.doors.append(door2)
            
            case 1:
                #avatares
                self.avatars[0].set_initial_position(14, 175)
                self.avatars[1].set_initial_position(14, 219)
                
                # self.avatars[0].set_initial_position(14, 9)
                # self.avatars[1].set_initial_position(14, 9)

                self.time = 35

                pgm = imgppg("level1.pgm")
                
                self.obstacles_matrix_reduced = pgm.matrix
                replication_matrix = np.ones((8, 8), dtype=np.int16)

                self.obstacles_matrix = np.kron(self.obstacles_matrix_reduced, replication_matrix)


                self.objects.append(Spike(125, 244, self))
                self.objects.append(Spike(165, 244, self))
                self.objects.append(Spike(175, 189, self))

                self.objects.append(GateSystem('green', self, levers=[[72, 157]], gates=[[9, 132, 0, 'hor', False]]))
                self.objects.append(GateSystem('purple', self, buttons=[[80, 124], [178, 76]], gates=[[225, 82, 0, 'hor', False]]))

                door1 = FinalDoor(200, 9, self.avatars[0], self)
                door2 = FinalDoor(227, 14, self.avatars[1], self)
                self.doors.append(door1)
                self.doors.append(door2)

            case 2:
                #avatares
                self.avatars[0].set_initial_position(18, 175)
                self.avatars[1].set_initial_position(30, 219)

                self.time = 60

                pgm = imgppg("level2.pgm")
                
                self.obstacles_matrix_reduced = pgm.matrix
                replication_matrix = np.ones((8, 8), dtype=np.int16)

                self.obstacles_matrix = np.kron(self.obstacles_matrix_reduced, replication_matrix)

                self.objects.append(Spike(200, 204, self))
                self.objects.append(Spike(210, 93, self))

                self.objects.append(GateSystem('green', self, buttons=[[232, 205], [232, 85]], gates=[[80, 217, 0, 'ver', False], [9, 46, 0, 'hor', False]]))
                self.objects.append(GateSystem('purple', self, levers=[[171, 238]], gates=[[110, 137, 0, 'ver', True]]))

                self.objects.append(PortalSystem(self.avatars[1], [[8, 120, 'right'], [243, 8, 'left']], self, buttons=[[70, 37]]))

                door1 = FinalDoor(195, 9, self.avatars[0], self)
                door2 = FinalDoor(170, 14, self.avatars[1], self)
                self.doors.append(door1)
                self.doors.append(door2)

            
        self.timer = self.fps*self.time
    
    def update(self):

        #aqui é pra funcionar o temporizador certinho e reiniciar
        if self.estado == "menu":
            self.menu.update()
        
            if pyxel.btnp(pyxel.KEY_RETURN):

                if self.menu.options_initial[self.menu.option] == 'START':
                    self.estado = 'level'

                elif self.menu.options_initial[self.menu.option] == "QUIT GAME":
                    pyxel.quit()  # sai do jogo

        elif self.estado== 'level':

            self.escolhaLevel.update()

            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.escolhaLevel.options_initial[self.escolhaLevel.option] == 'Level 1':
                    self.level = 1
                    self.estado = 'playing'
                elif self.escolhaLevel.options_initial[self.escolhaLevel.option] == "Level 2":
                    self.level = 2
                    self.estado = 'playing' 
                
                self.create_avatars()
                self.load_map()

        # se o estado for 'playing', inicia o jogo
        elif self.estado == "playing":


            if not self.pause:
                if self.timer > 0:
                    self.timer -= 1
                    
                else:
                    if not self.ignore_timer: self.restart()
            
                self.screen_matrix = self.obstacles_matrix.copy()

                for obj in self.objects:
                    obj.update()

                for avatar in self.avatars:
                    avatar.update()

                self.avatars_matrix = sum(avatar.position_matrix for avatar in self.avatars)

                if self.doors == []:
                    return
                
                for door in self.doors:
                    door.update()


                if sum(door.state for door in self.doors)==len(self.doors):
                    self.pause=True
                    self.finish_level()
            
            else:
                self.pauseMenu.update()

                if pyxel.btnp(pyxel.KEY_RETURN):

                    if self.pauseMenu.options_initial[self.pauseMenu.option] == 'Resume':
                        pass

                    elif self.pauseMenu.options_initial[self.pauseMenu.option] == "Restart":
                        self.restart()
                        
                    elif self.pauseMenu.options_initial[self.pauseMenu.option] == "Exit":
                        self.estado = "menu"
                    
                    self.pause=False



    def draw(self):
        if self.estado == "menu":
            self.menu.draw()
        elif self.estado=='level':
            self.escolhaLevel.draw()
        elif self.estado == "playing":

            pyxel.cls(0)
            pyxel.text(10, 10, "remaining time: " + str(self.timer // self.fps), 7)
            pyxel.text(10, 19, "level: " + str(self.level), 7)

            # pyxel.text(10, 10, "tempo restante: " + str(self.timer // self.fps), 7) #quadros por segundoss

            for door in self.doors:
                door.draw()

            for avatar in self.avatars:
                avatar.draw()
            
            for obj in self.objects:
                obj.draw()

            self.paint_screen()

            if self.pause: self.pauseMenu.draw()

    
    def finish_level(self):
        #ESCREVER AQUI O QUE ACONTECE QUANDO TERMINA A FASE
        self.level += 1
        self.load_map()
        self.restart()
        self.pause = False

    def pause_level(self):
        self.pause = True

    def add_rect_to_matrix(self, x, y, color, w=0, h=0):
        
        w = w if w else self.width
        h = h if h else self.width

        matrix = np.zeros(self.screenDim, np.int16)
        matrix[y:y+h, x:x+w] = color
        return matrix

    

    def paint_screen(self):
        
        width = self.obstacles_matrix_reduced.shape[0]
        height = self.obstacles_matrix_reduced.shape[1]
        for y in range(height):
            for x in range(width):
                if not self.obstacles_matrix_reduced[y,x] in [self.background_number]:
                    
                    # pyxel.pset(x, y, matrix[y,x])

                    pyxel.blt(x*8, y*8, self.image_buffer,
                        79, 0, 8, 8, self.background_remove)

    
    def matrix_to_txt(self, matrix, filename):
        
        with open(filename+'.txt', 'w+') as f:
           for line in matrix:
               f.write(' '.join([str(int(h)) for h in line]) + '\n')        



class Avatar:
    def __init__(self, avatar, avatar_width, avatar_height, Jogo, mov_keys, matrix_number) -> None:

        self.avatar = avatar
        self.avatar_number = matrix_number

        self.Jogo:Jogo = Jogo

        self.width = avatar_width
        self.height = avatar_height

        if self.avatar == 'tallgirl':
            self.direcoes= [
                [0,0,10,30], #frente
                [10,0,8,30], #lado direito com perna fechada 
                [18,0,13,30], #lado direito com perna aberta
                [10,0,-8,30], #lado esquerdo com perna fechada
                [18,0,-13,30] #lado esquerdo com perna aberta
            ]
        else:
            self.direcoes= [
                [0,30,10,25], #frente
                [10,30,8,25], #lado direito com perna fechada 
                [18,30,13,25], #lado direito com perna aberta
                [10,30,-8,25], #lado esquerdo com perna fechada 
                [18,30,-13,25] #lado esquerdo com perna aberta
            ]

        self.direcao_sprite = 0
        self.animation_cap = 7
        self.animation_it = 0

        self.movement_keys = mov_keys

        self.start_x = 0
        self.start_y = 0

        self.x = 0
        self.y = 0

        self.screenDim = self.Jogo.screenDim

        self.position_matrix = self.Jogo.add_rect_to_matrix(self.x, self.y, self.avatar_number, self.width, self.height)
        
        self.velocity = 1

        self.running = False

        self.jumping = False
        self.falling = False

        self.onFloor = False
        self.underCeiling = False
        self.rightWall = False
        self.leftWall = False

        self.gravity_accel= 0.35
        self.max_fallspeed = 4
        self.fall_speed = 0
  

    def update(self):
        self.keyboard_movement()

        if self.jumping or self.falling:
            self.gravity()

        if not self.onFloor and not self.jumping and not self.falling:
            self.falling = True
            self.gravity()

        self.position_matrix = self.Jogo.add_rect_to_matrix(self.x, self.y, self.avatar_number, self.width, self.height)

    def draw(self):

        self.draw_avatar()


    def draw_avatar(self):

        posicao_atual = self.direcoes[self.direcao_sprite]

        pyxel.blt(self.x, self.y, self.Jogo.image_buffer,
                   posicao_atual[0], posicao_atual[1], posicao_atual[2], posicao_atual[3], self.Jogo.background_remove)

    def set_initial_position(self, x, y):
        self.start_x = x
        self.x = x
        self.start_y = y
        self.y = y

    def restart(self):
        self.teletransport(self.start_x, self.start_y)

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
            self.Jogo.pause_level()

    def teletransport(self, x, y):
        self.x = x
        self.y = y
        self.check_borders(self.x, self.y)


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

            self.check_borders(next_x, next_y)


            if not self.onFloor and not self.underCeiling and not self.rightWall and not self.leftWall:
                self.x, self.y = next_x, next_y
            else:
                break

        return [self.x, self.y]

    def check_borders(self, x, y):

        avatar_bottom_border = self.Jogo.screen_matrix[y + self.height, x:x + self.width].tolist()
        avatar_top_border = self.Jogo.screen_matrix[y, x:x + self.width].tolist()
        avatar_right_border = self.Jogo.screen_matrix[y:y + self.height, x + self.width].tolist()
        avatar_left_border = self.Jogo.screen_matrix[y:y + self.height, x].tolist()

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
        self.max_fallspeed = 5 

        self.fall_speed = min(self.fall_speed + self.gravity_accel, self.max_fallspeed)

        target_y = int(np.ceil(self.y + self.fall_speed))

        self.update_position(self.x, target_y)

        if self.onFloor:
            self.fall_speed = 0
            self.jumping = False
            self.falling = False


    def jump(self):
        if self.onFloor and not self.jumping:
            self.jumping = True
            self.fall_speed = -7

class FinalDoor:

    def __init__(self, x, y, Avatar, Jogo):

        self.x = x
        self.y = y
        self.avatar = Avatar
        self.Jogo = Jogo

        self.width = 14

        self.state = 0

        
        match self.avatar.avatar:
            case 'tallgirl':
                self.height = 30

                self.animation = [
                    [51, 0],
                    [65, 0]
                    ]
            case 'cuteboy':
                self.height = 25

                self.animation = [
                    [51, 30],
                    [65, 30]
                ]

        pass

    def update(self):

        door_matrix_area = self.Jogo.avatars_matrix[self.y:self.y+self.height, self.x:self.x+self.width]

        count = 0
        for line in door_matrix_area:
            for elem in line:

                if elem==self.avatar.avatar_number:  
                    count+=1

        if count>self.width*self.height/3:
            self.state = 1
        
        else:
            self.state = 0
            
    
    def draw(self):

        posicao_atual = self.animation[self.state]

        pyxel.blt(self.x, self.y, self.Jogo.image_buffer,
                   posicao_atual[0], posicao_atual[1], self.width, self.height, self.Jogo.background_remove)
        pass


class Button:
    
    def __init__(self, id, x, y, Jogo, gateSystem):
        
        self.Jogo = Jogo
        self.gateSystem = gateSystem
        self.id = id


        self.x = x
        self.y = y

        self.width = 10
        self.height = 3

        self.state = 0

        match self.id:
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
            case 'cuteboy':
                self.animation = [
                    [94, 46],
                    [94, 49]
                ]
            case 'tallgirl':
                self.animation = [
                    [94, 40],
                    [94, 43]
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

    def __init__(self, id, x, y, Jogo, gateSystem):
        
        self.Jogo = Jogo
        self.gateSystem = gateSystem
        self.id = id

        self.x = x
        self.y = y

        self.width = 10
        self.height = 10

        self.onTop = True
        self.state = 0

        match self.id:
            case 'green':
                self.animation = [
                    [41, 19],
                    [41, 29]
                    ]
            case 'purple':
                self.animation = [
                    [41, 39],
                    [31, 39]
                ]
            case 'cuteboy':
                self.animation = [
                    [94, 20],
                    [94, 30]
                ]
            case 'tallgirl':
                self.animation = [
                    [94, 0],
                    [94, 10]
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
    
    def __init__(self, x, y, type, direction, dual, Jogo, gateSystem):
        
        self.Jogo = Jogo
        self.gateSystem = gateSystem

        self.x = x
        self.y = y
        self.type = type #type==0 -> normalmente fechado// type==1 -> normalmente aberto 
        self.direction = direction
        self.dual = dual

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
        
        self.opennig_size = self.height - 4 if self.gateSystem.id == 'green' else (self.height+10 if self.dual else self.height)
        pass


    def update(self):  

        self.state = not self.gateSystem.state if self.type else self.gateSystem.state

        match self.direction:
            case 'ver':
                new_x = self.x
                new_y = self.y if self.state == 0 else self.y - self.opennig_size

                self.Jogo.screen_matrix[new_y:new_y+self.height, new_x:new_x+self.width] = self.Jogo.floor_number

            case 'hor':
                new_x = self.x if self.state == 0 else self.x-self.opennig_size
                new_y = self.y

                # Ajustar as coordenadas de origem para rotação de 90 graus
                
                self.Jogo.screen_matrix[new_y:new_y+self.width, new_x:new_x+self.height] = self.Jogo.floor_number

        
        
        pass

    def draw(self):
        posicao_atual = self.animation[0]
        u = posicao_atual[0]
        v = posicao_atual[1]
        
        match self.direction:
            case 'ver':
                new_x = self.x
                new_y = self.y if self.state == 0 else self.y - self.opennig_size

                pyxel.blt(new_x, new_y, self.Jogo.image_buffer, u, v, self.width, self.height, self.Jogo.background_remove)

            case 'hor':
                new_x = self.x if self.state == 0 else self.x-self.opennig_size
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


class GateSystem:

    def __init__(self, id, Jogo, gates, buttons=[], levers=[]):
        
        self.id = id
        self.Jogo = Jogo

        self.objects = []
        self.gates = []

        for params in buttons:
            self.objects.append(Button(self.id, params[0], params[1], self.Jogo, self))
            
        for params in levers:
            self.objects.append(Lever(self.id, params[0], params[1], self.Jogo, self))

        for params in gates:
            self.gates.append(Gate(params[0], params[1], params[2], params[3], params[4], self.Jogo, self))

        self.state = 0 #0- não pressionado, 1-pressionado

        pass

    def update(self):
        
        # self.state = 0
        for obj in self.objects:
            obj.update()
            # if self.state==0: self.state = obj.state

        
        self.state = 1 if sum(obj.state for obj in self.objects)>0 else 0

        for gate in self.gates:
            gate.update()

    def draw(self):

        for obj in self.objects:
            obj.draw()

        for gate in self.gates:
            gate.draw()

    def reset(self):

        self.state = 0
        for obj in self.objects:
            obj.state = 0

class PortalSystem:

    def __init__(self, avatar, portals_list, Jogo, levers=[], buttons=[]):
        
        self.Jogo = Jogo
        self.avatar = avatar

        self.portal1 = Portal(portals_list[0][0], portals_list[0][1], portals_list[0][2], self.Jogo, self)
        self.portal2 = Portal(portals_list[1][0], portals_list[1][1], portals_list[1][2], self.Jogo, self)

        self.objects = []

        # self.id = self.avatar.avatar
        self.id = self.avatar.avatar

        for params in buttons:
            self.objects.append(Button(self.id, params[0], params[1], self.Jogo, self))
            
        for params in levers:
            self.objects.append(Lever(self.id, params[0], params[1], self.Jogo, self))
        
        pass


    def update(self):  

        if len(self.objects)>0:
            self.state = 0
        else:
            self.state = 1
        
        for obj in self.objects:
            obj.update()
            if self.state==0: self.state = obj.state

        self.portal1.update()
        self.portal2.update()

        if self.state==0:
            return

        portal1_area_matrix = self.Jogo.avatars_matrix[self.portal1.y:self.portal1.y+self.portal1.height, self.portal1.x:self.portal1.x+self.portal1.width]

        portal2_area_matrix = self.Jogo.avatars_matrix[self.portal2.y:self.portal2.y+self.portal2.height, self.portal2.x:self.portal2.x+self.portal2.width]
        
        for line in portal1_area_matrix:
            for elem in line:

                if elem==self.avatar.avatar_number:  
                    add_to_position = -self.avatar.width-1 if self.portal2.side=='left' else self.portal2.width+1
                    self.avatar.teletransport(self.portal2.x+add_to_position, self.portal2.y)

        for line in portal2_area_matrix:
            for elem in line:

                if elem==self.avatar.avatar_number:  
                    add_to_position = -self.avatar.width-1 if self.portal1.side=='left' else self.portal1.width+1
                    self.avatar.teletransport(self.portal1.x+add_to_position, self.portal1.y)
            

        pass

    def draw(self):

        self.portal1.draw()
        self.portal2.draw()
        for obj in self.objects:
            obj.draw()

    def reset(self):

        self.state = 0
        for obj in self.objects:
            obj.state = 0

class Portal:
    
    def __init__(self, x, y, side, Jogo, portalSystem):

        self.Jogo = Jogo
        self.portalSystem = portalSystem

        self.x = x
        self.y = y
        self.side = side

        self.width = 5
        self.height = 32

        self.matrix = np.zeros(self.Jogo.screenDim, np.int16)
        self.state = 0 #0 - liberado; 1-travado

        match self.portalSystem.avatar.avatar:
            case 'tallgirl':
                self.animation = [
                    [79, 23],
                    [84, 23]
                ]
            case 'cuteboy':
                self.animation = [
                    [79, 23],
                    [89, 23]
                ]


    def update(self):
        
        self.state = self.portalSystem.state

    def draw(self):
        posicao_atual = self.animation[self.state]
        u = posicao_atual[0]
        v = posicao_atual[1]

        new_x = self.x
        new_y = self.y
        new_w = self.width
        new_h = self.height 

        pyxel.blt(new_x, new_y, self.Jogo.image_buffer, u, v, new_w, new_h, self.Jogo.background_remove)

class Spike:
    def __init__(self, x, y, Jogo):
        
        self.Jogo = Jogo

        self.x = x
        self.y = y

        self.width = 14
        self.height = 3

        # self.state = 0

        self.animation = [37, 8]

        pass


    def update(self):

        area_matrix = self.Jogo.avatars_matrix[self.y:self.y+self.height, self.x:self.x+self.width]
        
        if np.count_nonzero(area_matrix)>0:

            self.Jogo.restart()

    def draw(self):

        posicao_atual = self.animation

        pyxel.blt(self.x, self.y, self.Jogo.image_buffer,
                   posicao_atual[0], posicao_atual[1], self.width, self.height, self.Jogo.background_remove)
        pass

    def reset(self):

        pass

class Menu:
    def __init__(self):
        self.options_initial = ['START', 'QUIT GAME']
        self.option = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.option = (self.option - 1) % len(self.options_initial)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.option = (self.option + 1) % len(self.options_initial)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(75,75,'CUTEBOY AND TALLGIRL', 11)
        for i, option in enumerate(self.options_initial):
            if i == self.option:     
                color= 7
            else: 
                color= 8
            pyxel.text(100, 110 + i * 10, option, color)

class EscolhaLevel:
    def __init__(self):
        self.options_initial = ['Level 1', 'Level 2']
        self.option = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.option = (self.option - 1) % len(self.options_initial)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.option = (self.option + 1) % len(self.options_initial)

    def draw(self):
        pyxel.cls(0)
        for i, option in enumerate(self.options_initial):
            if i == self.option:     
                color= 7
            else: 
                color= 8
            pyxel.text(100, 110 + i * 10, option, color)

class PauseMenu:

    def __init__(self):
        self.options_initial = ['Resume', 'Restart', 'Exit']
        self.option = 0

    def update(self):

        if pyxel.btnp(pyxel.KEY_UP):
            self.option = (self.option - 1) % len(self.options_initial)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.option = (self.option + 1) % len(self.options_initial)

    def draw(self):
        # pyxel.cls(0)

        pyxel.rect(90, 90, 70, 16+ (len(self.options_initial) * 10), 0)

        for i, option in enumerate(self.options_initial):
            if i == self.option:     
                color= 7
            else: 
                color= 8

            pyxel.text(110, 110 + i * 10, option, color)
        


Jogo()