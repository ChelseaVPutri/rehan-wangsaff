import socket
import threading
import sys
import time

HOST = '127.0.0.1'  
PORT = 212       

clients = {}  
client_lock = threading.Lock()

def broadcast_user_list():
    """Mengirim daftar user yang online ke semua klien"""
    with client_lock:
        user_list = list(clients.values())
    
    if user_list:
        message = "USERLIST:" + ",".join([user['name'] for user in user_list])
        with client_lock:
            for conn in clients.keys():
                try:
                    conn.sendall(message.encode('utf-8'))
                except:
                    pass

def handle_client(conn, addr):
    print(f"[SERVER] Terhubung dengan {addr}")
    try:
        # Menerima nama klien pertama kali
        client_name = conn.recv(1024).decode('utf-8')
        
        with client_lock:
            clients[conn] = {'name': client_name, 'addr': addr}
        
        print(f"[SERVER] Klien '{client_name}' ({addr}) telah terhubung.")
        
        # Kirim pesan selamat datang
        welcome_msg = f"*** {client_name} bergabung ***"
        conn.sendall(f"SERVER:{welcome_msg}".encode('utf-8'))
        
        # Broadcast ke semua klien bahwa ada user baru
        with client_lock:
            for other_conn in clients.keys():
                if other_conn != conn:
                    try:
                        other_conn.sendall(f"SERVER:{welcome_msg}".encode('utf-8'))
                    except:
                        pass
        
        broadcast_user_list()
        
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"[SERVER] Menerima dari {client_name}: {message}")
            
            # Handle berbagai perintah
            if message.startswith('/'):
                parts = message.split(' ', 2)
                command = parts[0]
                
                if command == '/list':
                    # Kirim daftar user yang online
                    with client_lock:
                        user_names = [user['name'] for user in clients.values()]
                    user_list = "Users online: " + ", ".join(user_names)
                    conn.sendall(f"SERVER:{user_list}".encode('utf-8'))
                
                elif command == '/chat' and len(parts) >= 2:
                    target_user = parts[1]
                    # Cek apakah target user ada
                    target_conn = None
                    with client_lock:
                        for c, info in clients.items():
                            if info['name'] == target_user and c != conn:
                                target_conn = c
                                break
                    
                    if target_conn:
                        conn.sendall(f"CHATMODE:{target_user}".encode('utf-8'))
                    else:
                        conn.sendall(f"SERVER:User '{target_user}' tidak ditemukan atau itu adalah Anda sendiri.".encode('utf-8'))
                
                elif command == '/all' and len(parts) >= 2:
                    broadcast_message = " ".join(parts[1:])
                    # Broadcast ke semua user kecuali pengirim
                    with client_lock:
                        for other_conn, info in clients.items():
                            if other_conn != conn:
                                try:
                                    other_conn.sendall(f"[BROADCAST dari {client_name}] {broadcast_message}".encode('utf-8'))
                                except:
                                    pass
                    conn.sendall(f"SERVER:Broadcast terkirim ke semua user.".encode('utf-8'))
                
                elif command == '/quit':
                    break
                
                else:
                    help_msg = """Commands:
/list <user> - lihat semua user
/chat <user> - private chat
/all <pesan> - broadcast
/quit - keluar"""
                    conn.sendall(f"SERVER:{help_msg}".encode('utf-8'))
            
            else:
                # Jika bukan command, kirim sebagai pesan biasa atau dalam mode chat
                # Untuk implementasi sederhana, kita asumsikan ini adalah pesan broadcast
                with client_lock:
                    for other_conn, info in clients.items():
                        if other_conn != conn:
                            try:
                                other_conn.sendall(f"[{client_name}] {message}".encode('utf-8'))
                            except:
                                pass
    
    except Exception as e:
        print(f"[SERVER] Kesalahan dengan klien {addr}: {e}")
    finally:
        # Hapus klien dari daftar saat terputus
        with client_lock:
            if conn in clients:
                disconnected_client_name = clients[conn]['name']
                del clients[conn]
                print(f"[SERVER] Klien '{disconnected_client_name}' ({addr}) terputus.")
                
                # Beri tahu klien lain jika ada yang terputus
                disconnect_msg = f"*** {disconnected_client_name} meninggalkan chat ***"
                for other_conn in clients.keys():
                    try:
                        other_conn.sendall(f"SERVER:{disconnect_msg}".encode('utf-8'))
                    except:
                        pass
        
        # Update user list untuk semua klien
        broadcast_user_list()
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(10)  # Mendukung lebih banyak koneksi
        print(f"[SERVER] Server mendengarkan di {HOST}:{PORT}")
        
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[SERVER] Server dihentikan.")
        sys.exit(0)