# -*- coding: utf-8 -*-

import numpy as np

class Imagem: 
    def __init__(self,arqEntrada):

        self.working = True
        self.arqEntrada = arqEntrada #Não alterar essa linha
        
        self.matrix = None
        self.dimension = None
        self.maxPixelValue = 0
        self.type = ''
        self.width = 0
        self.height = 0

        self.extract_image_data()

        

    def extract_image_data(self):
        
        try:
            arq = open(self.arqEntrada, 'r')

        except:
            print('O caminho do arquivo inserido não existe.')
            self.working = False
            return None

        imgString = arq.read().replace('\n', ' ')
        
        imgList = imgString.split(' ')

        popped = 0
        
        for i in range(len(imgList)):
        
            realIndex = i-popped

            if imgList[realIndex]=='':
                imgList.pop(realIndex)
                popped += 1
            
            elif imgList[realIndex].isnumeric():
                imgList[realIndex]=int(imgList[realIndex])
        
        
        self.type = imgList[0]
        self.width = int(imgList[1])
        self.height = int(imgList[2])
        
        self.maxPixelValue = int(imgList[3])

        imgList = imgList[4:]

        index = 0
        if self.type == 'P2':
            
            self.dimension = (self.height, self.width)
            self.matrix = np.zeros(self.dimension, np.int64)

            for i in range(self.height):
                for j in range(self.width):
                    self.matrix[i, j] = imgList[index]
                    index += 1

        elif self.type == 'P3':
            
            self.dimension = (self.height, self.width*3)
            self.matrix = np.zeros(self.dimension, np.int64)

            print(self.matrix)

            for i in range(self.height):
                for j in range(self.width):
                    print(i, (j*3),':',(j*3)+3)
                    print(self.matrix[i, (j*3):(j*3)+3])
                    print(imgList[index*3:index*3+3])
                    self.matrix[i, (j*3):(j*3)+3] = imgList[index*3:index*3+3]
                    index += 1

        print(self.matrix)

        arq.close()
    
    def matrix_to_image_data(self, matrix, arqSaida):

        matrixList = matrix.tolist()

        with open(arqSaida, 'w+') as arq:
            
            arq.write(str(self.type)+'\n')
            arq.write(str(self.dimension[1])+' '+str(self.dimension[0])+'\n')
            arq.write(str(self.maxPixelValue)+'\n')

            #print(matrixList)

            for line in matrixList:
                for element in line:
                    arq.write(str(element)+' ')
                arq.write('\n')
                
            
            
# Classe ImagemPGM herda a classe Imagem
class ImagemPGM(Imagem):

    def __init__(self,arqEntrada):

        super().__init__(arqEntrada) #Não alterar essa linha
        
        if self.type != 'P2': 
            print('A estrutura do arquivo não corresponde à classe invocada.')
            self.working=False
        

    def brilho(self,arqSaida,valor):
        
        if not self.working:
            return False
    
        result_matrix = np.zeros(self.dimension, np.int64)

        for i in range(self.height):
            for j in range(self.width):
                newPixelValue = self.matrix[i,j]+valor if self.matrix[i,j]+valor<self.maxPixelValue else self.maxPixelValue
                result_matrix[i, j]= newPixelValue

        print(result_matrix)

        self.matrix_to_image_data(result_matrix, arqSaida)

        return True

 
    def espelha(self,arqSaida):

        if not self.working:
            return False
    
        result_matrix = np.zeros(self.dimension, np.int64)

        for i in range(self.height):
            for j in range(self.width):

                result_matrix[i, j]= self.matrix[i,self.width-j-1]

        print(result_matrix)

        self.matrix_to_image_data(result_matrix, arqSaida)
        print(self.matrix.shape)

        return True

    

    ## Podem ser criados outros métodos


# Classe ImagemPGM herda a classe Imagem
class ImagemPPM(Imagem):

    def __init__(self,arqEntrada):
        # Recebe o nome do arquivo de entrada
        # e cria o atributo arqEntrada chamando o construtora
        # da classe imagem.
        super().__init__(arqEntrada) #Não alterar essa linha
        # Pode editar a partira daqui para criar outros atributos, se desejar.

    ################################################
    ####### ----  EDITAR A PARTIR DAQUI  ---- ######
    ################################################

    # Método que espelha uma imagem PPM
    # Seu método deve abrir o arquivo de entrada
    # e criar o arquivo de saída.
    # Caso o arquivo de entrada não exista ou seja inválido,
    # retornar False.
    def espelha(self,arqSaida):
        ok=True
        ## Escreva seu código aqui.
    
        return ok

    # Método que rotaciona 90o uma imagem PPM
    # Seu método deve abrir o arquivo de entrada
    # e criar o arquivo de saída.
    # Caso o arquivo de entrada não exista ou seja inválido,
    # retornar False.
    def rotaciona90(self,arqSaida):
        ok=True
        ## Escreva seu código aqui.
    
        return ok

    ## Podem ser criados outros métodos