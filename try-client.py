import socket
import threading
import sys

HOST = '127.0.0.1'  
PORT = 212        

class ChatClient:
    def __init__(self):
        self.socket = None
        self.current_chat_user = None
        self.username = None
        self.in_chat_mode = False
        self.online_users = []

    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                
                # Handle pesan khusus dari server
                if message.startswith('SERVER:'):
                    server_msg = message[7:]  
                    print(f"\n{server_msg}")
                
                elif message.startswith('USERLIST:'):
                    # Update daftar user online
                    users = message[9:].split(',') if message[9:] else []
                    self.online_users = [u for u in users if u != self.username]
                
                elif message.startswith('CHATMODE:'):
                    # Masuk ke mode chat dengan user tertentu
                    target_user = message[9:]
                    self.current_chat_user = target_user
                    self.in_chat_mode = True
                    print(f"\n=== Chat dengan {target_user} dimulai ===")
                    print("Ketik pesan Anda (ketik '/back' untuk kembali ke menu utama):")
                
                else:
                    # Pesan biasa dari user lain
                    print(f"\n{message}")
                
                if not self.in_chat_mode:
                    self.show_prompt()
                else:
                    sys.stdout.write(f"[Chat dengan {self.current_chat_user}] ")
                    sys.stdout.flush()
                
            except OSError:
                print("\n[CLIENT] Koneksi ke server terputus.")
                break
            except Exception as e:
                print(f"\n[CLIENT] Kesalahan saat menerima pesan: {e}")
                break

    def show_prompt(self):
        sys.stdout.write(f"\n[{self.username}] Commands:\n")
        sys.stdout.write("/list               - lihat semua user\n")
        sys.stdout.write("/chat <user>        - private chat\n")
        sys.stdout.write("/all <pesan>        - broadcast\n")
        sys.stdout.write("/quit               - keluar\n")
        sys.stdout.write(f"\n[{self.username}]> ")
        sys.stdout.flush()

    def start_client(self):
        self.username = input("Masukkan username: ")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.socket = s
            try:
                s.connect((HOST, PORT))
                print(f"[CLIENT] Terhubung ke server di {HOST}:{PORT}")
                s.sendall(self.username.encode('utf-8'))

                # Memulai thread terpisah untuk menerima pesan
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()

                # Tunggu sebentar untuk menerima pesan selamat datang
                threading.Event().wait(0.5)
                
                while True:
                    if not self.in_chat_mode:
                        self.show_prompt()
                        message = input()
                        
                        if message.lower() == '/quit':
                            s.sendall('/quit'.encode('utf-8'))
                            break
                        elif message.startswith('/chat '):
                            parts = message.split(' ', 1)
                            if len(parts) >= 2:
                                target_user = parts[1]
                                s.sendall(f'/chat {target_user}'.encode('utf-8'))
                            else:
                                print("Format: /chat <username>")
                        else:
                            s.sendall(message.encode('utf-8'))
                    
                    else:
                        # Mode chat pribadi
                        sys.stdout.write(f"[Chat dengan {self.current_chat_user}] ")
                        sys.stdout.flush()
                        message = input()
                        
                        if message.lower() == '/back':
                            self.in_chat_mode = False
                            self.current_chat_user = None
                            print("=== Kembali ke menu utama ===")
                        else:
                            # Kirim pesan pribadi
                            private_msg = f"PRIVATE:{self.current_chat_user}:{message}"
                            s.sendall(private_msg.encode('utf-8'))

            except ConnectionRefusedError:
                print("[CLIENT] Gagal terhubung ke server. Pastikan server sudah berjalan.")
            except Exception as e:
                print(f"[CLIENT] Terjadi kesalahan: {e}")
            finally:
                print("[CLIENT] Anda telah keluar dari chat.")

if __name__ == '__main__':
    client = ChatClient()
    client.start_client()