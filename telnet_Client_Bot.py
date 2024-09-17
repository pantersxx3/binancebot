import telnetlib
import sys

HOST = "localhost"
PORT = 9999

tn = telnetlib.Telnet(HOST, PORT)

while True:
    print("\nServer Telnet - MegatronMod[localhost:9999]\n")
    cmmd = input("Comando[funcion.variable]: ")
    if "exit" in cmmd:
        exit(0)

    tn.write(cmmd.encode('utf-8') + b"\n")
    print(tn.read_until(b"<END_COMMAND>").decode('utf-8').replace("<END_COMMAND>", ""))
    print("\n")
