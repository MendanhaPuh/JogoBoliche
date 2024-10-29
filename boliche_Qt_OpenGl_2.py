import sys
import math
import pygame
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,QHBoxLayout, QWidget, QLabel,
                            QProgressBar, QPushButton, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget, QStatusBar
from PyQt5.QtGui import QFont
from OpenGL.GL import *
from OpenGL.GLU import *

# ============= 
#   Definição do dialogo que lida com o reinicio da partida
# =============
class EndGameDialog(QDialog):
    def __init__(self, winner_message, table_widget):
        super().__init__()

        self.setWindowTitle("Fim do Jogo")

        # Guardar a referência da tabela
        self.table_widget = table_widget

        # Layout principal
        layout = QVBoxLayout()

        # Label com a mensagem do vencedor
        self.message_label = QLabel(winner_message)
        layout.addWidget(self.message_label)

        # Botão para fechar o diálogo
        self.close_button = QPushButton("Jogar Novamente? ")
        self.close_button.clicked.connect(self.close_and_reset)  # Chama o método que fecha o diálogo e reseta a tabela
        layout.addWidget(self.close_button)

        # Configura o layout no diálogo
        self.setLayout(layout)

    def close_and_reset(self):
        """Fecha o diálogo e reseta a tabela."""
        self.table_widget.clearContents()  # Reseta a tabela, removendo todas as linhas
        self.accept()  # Fecha o diálogo
# ============= 
#   Definição do core do jogo e
#   Instanciamento do contexto OpenGL
# =============
class BowlingGame(QOpenGLWidget):    
    
    # ============== Construtor
    def __init__(self, round_label_, progress_bar, players, score_board_):
        super().__init__()

        #Variáveis para os players
        self.current_player_index = 0  # Indica qual jogador está jogando
        self.current_round = 1  # Indica qual rodada (jogada) está em andamento
        self.total_rounds = 4  # Total de rodadas (cada jogador joga 2 vezes por turno)
        self.tries = 2
        self.players = players
        self.score = 0
        self.score_table = score_board_

        # Variáveis globais: bola e pinos
        self.ball_position = [-0.43, -1.0, 0.0]  # Inicialmente no centro, perto da base da pista
        self.ball_speed = 0.0  # Inicialmente a bola não se move
        self.rotation_angle = 180.0
        self.rotation_speed = 10.0        
        self.ball_direction = [0.0, 0.0]  # Direção inicial (x, y) para controle da direção da bola
        self.force = 0.0  # Força de lançamento da bola
        self.first_pin_height = 2.3 # Altura do primeiro pino, usada para calcular a altura dos demais
        self.ball_radius = 0.05 # Raio da bola e dos pinos
        self.pin_radius = 0.04
        self.round_label = round_label_
        self.progress_bar = progress_bar
        self.progress_bar.setValue(int(self.force * 100))

        # Inicialização dos pinos com rotação, estado de queda e cor
        self.pin_positions = [
            {"position": [-0.2, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.0, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.2, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [-0.1, self.first_pin_height+0.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.1, self.first_pin_height+0.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.0, self.first_pin_height, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#1ª
            {"position": [-0.3, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [-0.15, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.0, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.15, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.3, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)}#4ª
        ]
        
        

        
        self.setFocusPolicy(Qt.StrongFocus)  # Garante que o widget receberá o foco
        self.setFocus()  # Dá o foco para o widget

    def load_texture(self, path):
            texture_surface = pygame.image.load(path)
            texture_surface = pygame.transform.flip(texture_surface, False, True)  # Flip the texture vertically
            texture_data = pygame.image.tostring(texture_surface, "RGBA", True)

            # Generate texture ID
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)

            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # Upload the texture to OpenGL
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_surface.get_width(), texture_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            
            return texture_id

    # =============== OpenGL
    def initializeGL(self):
        #glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800 / 600, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0.0, -2.0, 1.0,  # Posição da câmera
                  0.0, 0.1, 0.0,  # Ponto de visão
                  0.0, 1.0, 0.0)  # Vetor "para cima"
        #Texture area
        self.floor_texture = self.load_texture('textures/piso4.png')
        self.ball_texture = self.load_texture('textures/dark_gray.png')
        self.pin_texture = self.load_texture('textures/pinofinal.png')

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        # Se a bola não estiver se movendo no eixo Y, mova lateralmente
        if self.ball_position[1] == -1.0:
            self.loopBall()  # Mover lateralmente apenas se ainda não começou a se mover no Y
        # Atualizar a posição da bola com base na velocidade e direção
        if self.ball_speed > 0:
            self.ball_position[1] += self.ball_speed * self.ball_direction[1]
            
            # Impedir que a bola saia da tela ou ultrapasse os pinos
            if self.ball_position[1] > 6.5:
                #self.ball_position[1] = 3.0
                #self.ball_speed = 0.0  # Parar a bola quando atingir o final da pista
                self.reset_ball_position()
                
                self.tries -= 1
                #print("Tries", self.tries, sep="|")
                if self.tries == 0 and self.current_round < 11:
                    
                    if (self.current_player_index == len(self.players)-1):
                        #self.players[self.current_player_index]["score"] = 0 # reseta os pontos obtidos na rodada
                        #print(f"{self.current_player_index} {self.players[self.current_player_index]['score']}")
                        print(f"Fim ROdada {self.current_round} | Começo {self.current_round+1}")
                        self.current_round += 1
                        self.current_player_index = 0
                        self.tries = 2
                        self.score_table.selectRow(self.current_player_index)
                        self.reset_game()
                        self.end_game()
                    else:
                        #self.players[self.current_player_index]["score"] = 0 # reseta os pontos obtidos na rodada
                        print(f"{self.current_player_index} {self.players[self.current_player_index]['score']}")
                        self.current_player_index += 1
                        self.tries = 2
                        self.score_table.selectRow(self.current_player_index)
                        self.reset_game()
                        

        
        self.draw_pist()
        self.draw_ball()
        self.draw_pins()
        self.move_ball()
        self.remove_pins()
        #self.end_game()
        self.update()
        glFlush()

    # ================= Gerenciamento do Jogo
    def atualizarTotais(self):
        # Iterar sobre as linhas da tabela
        for row in range(self.score_table.rowCount()):
            total = 0
            # Somar os valores das primeiras 10 colunas
            for col in range(4):
                item = self.score_table.item(row, col)
                if item and item.text().isdigit():
                    total += int(item.text())
            # Exibir o total na 11ª coluna (coluna do total)
            self.score_table.setItem(row, 4, QTableWidgetItem(str(total)))
            self.players[row]["score"] = total

    def loopBall(self):
        # Verifica se a bola está indo para a direita ou para a esquerda
        if self.ball_direction[0] >= 0:  # Movendo para a direita
            if self.ball_position[0] < 0.73:
                self.ball_position[0] += 0.01  # Move para a direita
            else:
                self.ball_direction[0] = -1  # Inverte a direção para a esquerda
        elif self.ball_direction[0] <= 0:  # Movendo para a esquerda
            if self.ball_position[0] > -0.73:
                self.ball_position[0] -= 0.01  # Move para a esquerda
            else:
                self.ball_direction[0] = 1  # Inverte a direção para a direita

        # Chame a renderização da bola aqui após atualizar a posição
        self.draw_ball()

    def keyPressEvent(self, event):
        key = event.key()
        #print(f"Evento capturado {key} ASCII_Value")
        
        if key == Qt.Key_W:
            self.force = min(self.force + 0.005, 0.05)
            self.update_progress_bar() 
            #print(f"Força aumentada para {self.force}")
        elif key == Qt.Key_S:
            self.force = max(self.force - 0.005, 0.001)
            self.update_progress_bar() 
            #print(f"Força diminuída para {self.force}")
        elif key == Qt.Key_Space:
            self.ball_direction = [0.0, 3.0] # Direção para frente
            self.ball_speed = self.force / 5.0
            #print(f"Lançando com força {self.force}")
        elif key == Qt.Key_Q:
            #print(f"Jogo reiniciado, força redefinida: {self.force}")
            self.reset_game()
        elif key == Qt.Key_R:
            #print(f"Bola reposicionada, força redefinida: {self.force}")
            self.reset_ball_position()
    
    def update_progress_bar(self):
        max_force = 0.05
        percentage = (self.force / max_force) * 100
        self.progress_bar.setValue(int(percentage))
    
    def reset_ball_position(self):
        self.ball_position = [0.0, -1.0, 0.0]
        self.ball_speed = 0.0
        self.ball_direction = [0.0, 0.0]
        self.force = 0.00
        self.update_progress_bar()
        self.loopBall()

    def remove_pins(self):
        # Filtra os pinos que não caíram
        self.pin_positions = [pin for pin in self.pin_positions if pin["rotation"] > -90.0]
   
    def move_ball(self):
        # Atualizar a posição da bola com base na velocidade e direção        
        if self.ball_position[1] <= 5.5 and self.ball_position[1] != 1.0:
            
            if(self.ball_speed > 0):
                self.rotation_angle +=self.rotation_speed
            
            self.ball_position[1] += self.ball_speed * self.ball_direction[1]
            self.ball_position[0] += self.ball_speed * self.ball_direction[0]
            self.check_collision()
            #print(self.ball_position, self.ball_direction, sep="|")

        else:
            # Atualize a rotação com base na velocidade da bola
            self.ball_position[1] += self.ball_speed * self.ball_direction[1]
            self.ball_position[0] += self.ball_speed * self.ball_direction[0]
        
    def check_collision(self):
        for pin in self.pin_positions:
            position = pin["position"]
            distance = math.sqrt(
                (self.ball_position[0] - position[0]) ** 2 + 
                (self.ball_position[1] - position[1]) ** 2
            )
            
            # Se a bola atingir o pino
            if distance < (self.ball_radius + self.pin_radius) and not pin["falling"]:
                #print(f"Colisão detectada com o pino em {position}!")
                pin["falling"] = True
          
                # Direção da queda baseada na posição relativa da bola
                direction_x = position[0] - self.ball_position[0]
                direction_y = position[1] - self.ball_position[1]
                
                # Atribuímos a direção de queda ao pino
                pin["fall_direction"] = [direction_x * 0.05, direction_y * 0.05]
                pin["fall_speed"] = 0.02  # Definir a velocidade inicial da queda
                self.update_scoreboard()

    def update_scoreboard(self):
        """Atualiza a pontuação do jogador atual."""
        self.score_table.selectRow(self.current_player_index)
        print("Updade_scoreboard",self.players[self.current_player_index]['score'],self.current_round, sep="|")
        #self.players[self.current_player_index]['score'] += 1
        self.score += 1
        self.update_placar()

    def change_cell_value(self, row, column, new_value):
        """Altera o valor de uma célula específica."""
        new_item = QTableWidgetItem(new_value)
        self.score_table.setItem(row, column, new_item)

    def update_placar(self):
        """Atualiza o placar na tela."""
        #player_score = self.players[self.current_player_index]["score"]
        self.change_cell_value(self.current_player_index,self.current_round-1,str(self.score))

    def end_game(self):
        """Exibe os resultados finais usando um QMessageBox."""
        if self.current_round > self.total_rounds:
            self.current_round = 1
            max_score = max(player["score"] for player in self.players)

            # Lista todos os jogadores que têm a pontuação máxima
            winners = [player for player in self.players if player["score"] == max_score]

            if len(winners) > 1:
                # Caso haja empate
                winner_names = ", ".join([winner['name'] for winner in winners])
                winner_message = f"Fim do jogo! Temos um empate entre {winner_names}, todos com {max_score} pontos!"
            else:
                # Apenas um vencedor
                winner = winners[0]
                winner_message = f"Fim do jogo! O vencedor é {winner['name']} com {winner['score']} pontos!"
            
            dialog = EndGameDialog(winner_message, self.score_table)
            dialog.exec_()
            # Cria uma caixa de mensagem
            #msg_box = QMessageBox()
            #msg_box.setWindowTitle("Fim do Jogo")
            #msg_box.setText(winner_message)
            #msg_box.setIcon(QMessageBox.Information)

            # Exibe a caixa de mensagem
            #msg_box.exec_()
    
    def reset_All(self,result):
        if result == QDialog.Accepted or result == QDialog.rejected:
            self.ball_position = [0.1, -1.0, 0.0]
            self.ball_speed = 0.0
            self.ball_direction = [0.0, 0.0]
            self.force = 0.0
            self.score = 0
            self.current_player_index = 0  
            self.players = [
                {"name": "Jogador 1", "score": 0},
                {"name": "Jogador 2", "score": 0}
                ]


            self.pin_positions = [
                {"position": [-0.2, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
                {"position": [0.0, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
                {"position": [0.2, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
                {"position": [-0.1, self.first_pin_height+0.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
                {"position": [0.1, self.first_pin_height+0.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
                {"position": [0.0, self.first_pin_height, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#1ª
                {"position": [-0.3, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
                {"position": [-0.15, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
                {"position": [0.0, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
                {"position": [0.15, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
                {"position": [0.3, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)}#4ª
            ]

    def reset_game(self):
        self.ball_position = [0.1, -1.0, 0.0]
        self.ball_speed = 0.0
        self.ball_direction = [0.0, 0.0]
        self.force = 0.0
        self.score = 0
        self.players[self.current_player_index]["score"] = 0
        self.atualizarTotais()

        self.pin_positions = [
            {"position": [-0.2, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.0, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [0.2, self.first_pin_height+1.0, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#3ª
            {"position": [-0.1, self.first_pin_height+0.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.1, self.first_pin_height+0.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#2ª
            {"position": [0.0, self.first_pin_height, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#1ª
            {"position": [-0.3, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [-0.15, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.0, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.15, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)},#4ª
            {"position": [0.3, self.first_pin_height+1.5, 0.0], "rotation": 0.0, "falling": False, "color": (1.0, 1.0, 1.0)}#4ª
        ]
    # =================== Gerenciamento dos objetos na cena
    def draw_pist(self):
        # Desenhar a pista
        glEnable(GL_TEXTURE_2D)  # Enable textures
        glBindTexture(GL_TEXTURE_2D, self.floor_texture)  # Bind the floor texture

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, -1.1, -0.5)  # Bottom left vertex
        
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1.0, -1.1, -0.5)  # Bottom right vertex
        
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1.0, 3.0, 0.5)  # Top right vertex
        
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0, 3.0, 0.5)  # Top left vertex
        glEnd()

        glDisable(GL_TEXTURE_2D)  # Disable textures

    def draw_sphere(self, radius, slices, stacks):
        glEnable(GL_TEXTURE_2D)  # Enable textures
        glBindTexture(GL_TEXTURE_2D, self.ball_texture)  # Bind the ball texture
        
        for i in range(slices):
            lat0 = math.pi * (-0.5 + float(i) / slices)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            lat1 = math.pi * (-0.5 + float(i + 1) / slices)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(stacks + 1):
                lng = 2 * math.pi * float(j) / stacks
                x = math.cos(lng)
                y = math.sin(lng)
                
                # Apply texture coordinates
                glTexCoord2f(float(j) / stacks, float(i) / slices)
                glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)
                
                glTexCoord2f(float(j) / stacks, float(i + 1) / slices)
                glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
            glEnd()
        
        glDisable(GL_TEXTURE_2D)  # Disable textures

    def draw_ball(self):
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(self.ball_position[0], self.ball_position[1], self.ball_position[2])
        
        # Aplique a rotação
        glRotatef(self.rotation_angle, -1.0, 1.0, 0.0)
        self.draw_sphere(self.ball_radius, 20, 20)
        glPopMatrix()

    def draw_cylinder(self, radius, height, slices):
        glEnable(GL_TEXTURE_2D)  # Enable textures
        glBindTexture(GL_TEXTURE_2D, self.pin_texture)  # Bind the pin texture

        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle)
            y = math.sin(angle)

            # Apply texture coordinates
            glTexCoord2f(float(i) / slices, 0)  # Bottom texture coordinate
            glVertex3f(x * radius, y * radius, 0.0)

            glTexCoord2f(float(i) / slices, 1)  # Top texture coordinate
            glVertex3f(x * radius, y * radius, height)
        glEnd()

        # Draw the bottom base of the cylinder
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle)
            y = math.sin(angle)
            glTexCoord2f(x * 0.5 + 0.5, y * 0.5 + 0.5)  # Texture coordinates for bottom
            glVertex3f(x * radius, y * radius, 0.0)
        glEnd()

        # Draw the top base of the cylinder
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            x = math.cos(angle)
            y = math.sin(angle)
            glTexCoord2f(x * 0.5 + 0.5, y * 0.5 + 0.5)  # Texture coordinates for top
            glVertex3f(x * radius, y * radius, height)
        glEnd()

        glDisable(GL_TEXTURE_2D)  # Disable textures

    def draw_pins(self):
        for pin in self.pin_positions:
            position = pin["position"]
            rotation = pin["rotation"]
            falling = pin["falling"]
            color = pin["color"]

            glColor3f(*color)
            glPushMatrix()
            glTranslatef(position[0], position[1], position[2])

            if falling:
                # Simular rotação e queda dos pinos
                pin["rotation"] -= 5.0  # Aumentar rotação
                pin["fall_speed"] += 0.001  # Aumentar a velocidade de queda

                # Aplicar a direção da queda ao pino
                position[0] += pin["fall_direction"][0] * pin["fall_speed"]
                position[1] += pin["fall_direction"][1] * pin["fall_speed"]

                # Limitar a rotação para 90 graus
                if pin["rotation"] <= -90.0:
                    pin["falling"] = False

                glRotatef(pin["rotation"], 1.0, 0.0, 0.0)  # Rotacionar o pino caindo

            # Desenhar o pino (em pé ou caindo)
            self.draw_cylinder(self.pin_radius, 0.2, 10)

            glPopMatrix()
# ============= 
#   Definição dos componentes da UI e
#   Instanciamento do core do jogo.
# =============
def main():

    app = QApplication(sys.argv)
    window = QMainWindow() # Janela principal da aplicação
    window.setWindowTitle("Boliche com PyQt")
    central_widget = QWidget() # Widget central para: Boloche_Core e placar
    layout_vertical = QVBoxLayout() # Vertical Layout para segurar o BolicheCore e placar
    layout_horizontal = QHBoxLayout()
    layout_horizontal2 = QHBoxLayout()
    force_layout = QHBoxLayout()
    score_board = QTableWidget()

    force_progress_bar = QProgressBar()
    force_progress_bar.setMinimum(0)
    force_progress_bar.setMaximum(100)
    force_progress_bar.setTextVisible(False)
    #score_board.setMaximumWidth(200)
    score_board.setMaximumHeight(100)
    score_board.setFocusPolicy(Qt.NoFocus)

    str_instructions = """[W] Aumenta a força [S] Diminui a força do lançamento [ESPAÇO] Lança a bola"""
    placar = QLabel("Rodada: 1")
    ball_force = QLabel("Força da bola")
    instrucoes_jogo = QLabel(str_instructions)
    font_placar = QFont()

    font_placar.setPointSize(15)
    placar.setFont(font_placar)
    placar.setAlignment(Qt.AlignCenter)
    placar.setMaximumHeight(30)
    #placar.setMaximumWidth(100)

    font_placar.setPointSize(12)
    ball_force.setFont(font_placar)
    instrucoes_jogo.setFont(font_placar)
    instrucoes_jogo.setAlignment(Qt.AlignCenter)
    instrucoes_jogo.setMaximumHeight(30)
    
    # Lista de jogadores
    players = [
        {"name": "Jogador 1", "score": 0},
        {"name": "Jogador 2", "score": 0}
    ]
    score_labels = [str(x) for x in range(1,5)]
    score_labels.append("Total")
    score_labels2 = [players[0]['name'], players[1]['name']]
    game = BowlingGame(placar, force_progress_bar, players, score_board)
    score_board.setRowCount(len(players))
    score_board.setColumnCount(len(score_labels))
    score_board.setColumnWidth(0,20)
    score_board.setHorizontalHeaderLabels(score_labels)
    score_board.setVerticalHeaderLabels(score_labels2)
    score_board.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    score_board.setEditTriggers(QTableWidget.NoEditTriggers)

    
    #layout_horizontal2.addWidget(placar)
    layout_horizontal2.addWidget(score_board)
    layout_vertical.addLayout(layout_horizontal2)
    layout_vertical.addWidget(game)
    force_layout.addWidget(ball_force)
    force_layout.addWidget(force_progress_bar)
    layout_vertical.addLayout(force_layout)
    layout_vertical.addWidget(instrucoes_jogo)
    layout_horizontal.addLayout(layout_vertical)
    #layout_vertical.addWidget(next_turn_button)  # Adiciona o botão ao layout

    central_widget.setLayout(layout_horizontal)
    window.setCentralWidget(central_widget)
    status_bar = QStatusBar()
    status_bar.showMessage("<===================== Ernesto, Ernesto, Rafael, Henrique ===================== >")
    window.setStatusBar(status_bar)
    window.show() 
    window.setMinimumHeight(600)
    window.setMinimumWidth(600)
    game.update()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
