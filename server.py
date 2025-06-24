import socket
import threading
import sys

HOST = '127.0.0.1'  # Alamat IP localhost
PORT = 65432        # Port yang digunakan (bisa diubah)

clients = []
client_names = {}

def handle_client(conn, addr):
    print(f"[SERVER] Terhubung dengan {addr}")
    try:
        # Menerima nama klien pertama kali
        client_name = conn.recv(1024).decode('utf-8')
        client_names[conn] = client_name
        print(f"[SERVER] Klien '{client_name}' ({addr}) telah terhubung.")

        # Beri tahu klien lain bahwa ada yang bergabung
        if len(clients) == 2:
            other_client_conn = [c for c in clients if c != conn][0]
            other_client_name = client_names[other_client_conn]
            conn.sendall(f"Anda terhubung dengan {other_client_name}".encode('utf-8'))
            other_client_conn.sendall(f"{client_name} telah bergabung!".encode('utf-8'))


        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"[SERVER] Menerima dari {client_names[conn]}: {message}")

            # Teruskan pesan ke klien lain
            for client_socket in clients:
                if client_socket != conn:
                    try:
                        client_socket.sendall(f"[{client_names[conn]}] {message}".encode('utf-8'))
                    except:
                        # Klien terputus saat mencoba mengirim
                        clients.remove(client_socket)
                        if client_socket in client_names:
                            del client_names[client_socket]
                        print(f"[SERVER] Klien {client_socket.getpeername()} terputus saat meneruskan pesan.")
                        break # Keluar dari loop for, akan menyebabkan break dari loop while
    except Exception as e:
        print(f"[SERVER] Kesalahan dengan klien {addr}: {e}")
    finally:
        # Hapus klien dari daftar saat terputus
        if conn in clients:
            clients.remove(conn)
        if conn in client_names:
            disconnected_client_name = client_names[conn]
            del client_names[conn]
            print(f"[SERVER] Klien '{disconnected_client_name}' ({addr}) terputus.")
            # Beri tahu klien lain jika ada yang terputus
            if clients:
                clients[0].sendall(f"[{disconnected_client_name}] telah meninggalkan chat.".encode('utf-8'))
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Memungkinkan penggunaan ulang alamat/port
        s.bind((HOST, PORT))
        s.listen(2) # Hanya mendengarkan untuk 2 koneksi klien
        print(f"[SERVER] Server mendengarkan di {HOST}:{PORT}")

        while len(clients) < 2:
            conn, addr = s.accept()
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr)).start()

        print("[SERVER] Dua klien terhubung. Chat bisa dimulai.")
        # Opsional: Loop untuk menjaga server tetap hidup jika Anda ingin menangani putus/sambung kembali
        # Untuk kasus sederhana ini, server akan tetap berjalan sampai dihentikan manual.
        # Bisa ditambahkan logika untuk menerima klien baru jika ada yang terputus.
        while True:
            # Server utama hanya menunggu thread klien bekerja
            pass

if __name__ == '__main__':
    start_server()