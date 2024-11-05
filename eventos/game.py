# -*- coding: utf-8 -*-

import turtle
import time
import random
import paho.mqtt.client as mqtt
import threading
import queue
import json


# Configurações do MQTT
broker_address = "localhost"  
client_id = f"player_{random.randint(0, 1000)}"
client = mqtt.Client(client_id)

# Conectar ao broker MQTT
client.connect(broker_address, keepalive=60)

# Configuração da tela
wn = turtle.Screen()
wn.title("Multiplayer Move Game")
wn.bgcolor("green")
wn.setup(width=600, height=600)
wn.tracer(0)  # Desativa as atualizações da tela

# Dicionário para armazenar jogadores
players = {}
colors = ["red", "blue", "yellow", "purple", "orange", "pink"]
message_queue = queue.Queue()

# Função para mover o jogador e publicar sua nova posição


def move_player(player_id, direction):
    if player_id in players:
        player = players[player_id]

        # Atualiza a posição local
        if direction == "up":
            player['y'] += 10
        elif direction == "down":
            player['y'] -= 10
        elif direction == "left":
            player['x'] -= 10
        elif direction == "right":
            player['x'] += 10

        # Publica a nova posição
        client.publish("game/positions", json.dumps({
            'player_id': player_id,
            'color': player['color'],
            'x': player['x'],
            'y': player['y']
        }))

# Função para receber mensagens do broker


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    message_queue.put(payload)  # Adiciona a mensagem à fila


def listen_for_messages():
    client.loop_forever()

# Função para atualizar a tela com as posições dos jogadores


def update_display():
    while True:
        while not message_queue.empty():
            payload = message_queue.get()
            data = json.loads(payload)
            player_id, color, x, y = data['player_id'], data['color'], data['x'], data['y']

            # Adiciona ou atualiza o jogador
            if player_id not in players:
                players[player_id] = {'color': color, 'x': x,
                                      'y': y, 'turtle': create_turtle(color)}
            else:
                players[player_id]['x'] = x
                players[player_id]['y'] = y

            # Move a tartaruga para a nova posição
            players[player_id]['turtle'].goto(x, y)

        time.sleep(0.1)  # Reduz a frequência de atualização da tela


def create_turtle(color):
    t = turtle.Turtle()
    t.penup()
    t.shape("circle")
    t.color(color)
    t.goto(0, 0)
    return t

# Adiciona um jogador


def add_player(color):
    player_id = client_id
    players[player_id] = {'color': color, 'x': 0,
                          'y': 0, 'turtle': create_turtle(color)}
    return player_id


player_id = add_player(random.choice(colors))


def setup_keyboard_listener():
    wn.listen()
    wn.onkeypress(lambda: move_player(player_id, "up"), "w")
    wn.onkeypress(lambda: move_player(player_id, "down"), "s")
    wn.onkeypress(lambda: move_player(player_id, "left"), "a")
    wn.onkeypress(lambda: move_player(player_id, "right"), "d")
    wn.onkeypress(wn.bye, "Escape")  # Fecha o jogo com a tecla Escape


# Configurar o cliente MQTT
client.on_message = on_message
client.subscribe("game/positions")  # Subscreve a mensagens de posições

# Inicia as threads
# Thread para ouvir mensagens
threading.Thread(target=listen_for_messages, daemon=True).start()
# Thread para atualizar a tela
threading.Thread(target=update_display, daemon=True).start()
setup_keyboard_listener()  # Configura a escuta do teclado

# Atualiza a tela continuamente


def update_screen():
    while True:
        wn.update()
        time.sleep(0.05)  # Ajusta a frequência de atualização da tela


# Iniciar a atualização da tela
threading.Thread(target=update_screen, daemon=True).start()

wn.mainloop()  # Inicia o loop principal do turtle


