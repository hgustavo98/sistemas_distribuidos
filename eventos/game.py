# -*- coding: utf-8 -*-

import turtle
import time
import random
import paho.mqtt.client as mqtt
import threading
import queue
import json



broker_address = "localhost"  
client_id = f"player_{random.randint(0, 1000)}"
client = mqtt.Client(client_id)


client.connect(broker_address, keepalive=60)


wn = turtle.Screen()
wn.title("Multiplayer Move Game")
wn.bgcolor("green")
wn.setup(width=600, height=600)
wn.tracer(0) 


players = {}
colors = ["red", "blue", "yellow", "purple", "orange", "pink"]
message_queue = queue.Queue()




def move_player(player_id, direction):
    if player_id in players:
        player = players[player_id]

   
        if direction == "up":
            player['y'] += 10
        elif direction == "down":
            player['y'] -= 10
        elif direction == "left":
            player['x'] -= 10
        elif direction == "right":
            player['x'] += 10

        client.publish("game/positions", json.dumps({
            'player_id': player_id,
            'color': player['color'],
            'x': player['x'],
            'y': player['y']
        }))




def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    message_queue.put(payload)  


def listen_for_messages():
    client.loop_forever()



def update_display():
    while True:
        while not message_queue.empty():
            payload = message_queue.get()
            data = json.loads(payload)
            player_id, color, x, y = data['player_id'], data['color'], data['x'], data['y']

            
            if player_id not in players:
                players[player_id] = {'color': color, 'x': x,
                                      'y': y, 'turtle': create_turtle(color)}
            else:
                players[player_id]['x'] = x
                players[player_id]['y'] = y

           
            players[player_id]['turtle'].goto(x, y)

        time.sleep(0.1) 


def create_turtle(color):
    t = turtle.Turtle()
    t.penup()
    t.shape("circle")
    t.color(color)
    t.goto(0, 0)
    return t




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
    wn.onkeypress(wn.bye, "Escape")  


client.on_message = on_message
client.subscribe("game/positions")  


threading.Thread(target=listen_for_messages, daemon=True).start()

threading.Thread(target=update_display, daemon=True).start()
setup_keyboard_listener()  




def update_screen():
    while True:
        wn.update()
        time.sleep(0.05)  


threading.Thread(target=update_screen, daemon=True).start()

wn.mainloop() 


