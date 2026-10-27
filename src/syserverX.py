if __name__ == "__main__":
    def main():
        print('Hello User')
        log(0, "starting :]")
        log(0, "geting the moduls") 
        # i dnt use the fuking garbagecolector thats for normies
        file = open(mainpath / "paths.json", "r")
        pathsall = json.load(file)
        file.close()
        
        log(0, "make the soket")
        socket_path = pathlib.Path("/tmp/syserver.sock")
        socket_path.unlink(missing_ok=True)  # Elimina un socket viejo si quedó

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(socket_path))
            server.listen()

            print(f"Escuchando en {socket_path}")
            conn, _ = server.accept()

            with conn:
                data = conn.recv(1024)
                print("Recibido:", data.decode())
                conn.sendall(b"Hola desde el servidor")
        log(0, "exit good :]")
        return 0

    # i dnt like from
    import json
    import pathlib
    import socket
    import sys

    mainpath = pathlib.Path(__file__).resolve().parent

    def log(codenum, msg):
        if codenum==0:
            print(f'[ OK ] {msg}')
        elif codenum==-1:
            print(f'[ ERR ] {msg}')
        elif codenum==1:
            print(f'[ warning ] {msg}')

    sys.exit(main())
else:
    print('No fuk u dnt import me or export my content')
