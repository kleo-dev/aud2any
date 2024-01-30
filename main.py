import socket
import sys
import os
import pyaudio
import sounddevice as sd
import numpy as np
from threading import Thread

TYPE = 'server';
HOST = '127.0.0.1';
PORT = 6658;
p = pyaudio.PyAudio();
FORMAT = pyaudio.paInt16;
CHANNELS = 1;
RATE = 44100;
CHUNK = 1024;

def client(conn: socket.socket, addr, stream):
    connected = True;
    while connected:
        try:
            data = conn.recv(1024);
            if data:
                stream.write(data);
        except:
            print(f'[-] client {addr} disconnected');
            conn.close();
            connected = False;
            break;


if (len(sys.argv) > 1):
    TYPE = 'client';
    HOST = sys.argv[1];


if (TYPE == 'server'):
    os.system(f'lsof -nti:{PORT} | xargs kill -9');
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK);
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    s.bind((HOST, PORT));
    print(f'[*] lst as {HOST}:{PORT}');
    s.listen(4);
    while True:
        conn, addr = s.accept();
        print(f'[+] client has connected with address of {addr}');
        Thread(target=client, args=(conn, addr, stream), daemon=True).start();
    
else:
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK);
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    print(f'[*] connecting to {HOST}:{PORT}');
    s.connect((HOST, PORT));
    print(f'[+] connected!');
    try:
        with sd.InputStream(samplerate=RATE, channels=CHANNELS) as stream:
            while True:
                # data = stream.read(CHUNK);
                data, overflowed = stream.read(RATE);
                data_bytes = np.array(data).tobytes();
                s.sendall(data_bytes);
    finally:
        p.terminate();
        s.close();