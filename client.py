import socket
import threading
import sys

HOST = '127.0.0.1'  # Harus sama dengan HOST server
PORT = 65432        # Harus sama dengan PORT server

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(f"\n{data.decode('utf-8')}")
            sys.stdout.write("Anda: ") # Menampilkan prompt "Anda:" lagi setelah pesan diterima
            sys.stdout.flush()
        except OSError: # Koneksi terputus
            print("[CLIENT] Koneksi ke server terputus.")
            break
        except Exception as e:
            print(f"[CLIENT] Kesalahan saat menerima pesan: {e}")
            break

def start_client():
    client_name = input("Masukkan nama Anda: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"[CLIENT] Terhubung ke server di {HOST}:{PORT}")
            s.sendall(client_name.encode('utf-8')) # Mengirim nama klien ke server

            # Memulai thread terpisah untuk menerima pesan
            receive_thread = threading.Thread(target=receive_messages, args=(s,))
            receive_thread.daemon = True # Daemon thread akan berhenti ketika program utama berhenti
            receive_thread.start()

            while True:
                message = input("Anda: ")
                if message.lower() == 'keluar':
                    break
                s.sendall(message.encode('utf-8'))
        except ConnectionRefusedError:
            print("[CLIENT] Gagal terhubung ke server. Pastikan server sudah berjalan.")
        except Exception as e:
            print(f"[CLIENT] Terjadi kesalahan: {e}")
        finally:
            print("[CLIENT] Anda telah keluar dari chat.")
            s.close()
            # Pastikan receive_thread selesai sebelum keluar
            if receive_thread.is_alive():
                # Ini mungkin tidak selalu bekerja dengan baik karena receive_thread mungkin masih menunggu recv()
                # Cara terbaik adalah dengan membuat server menutup koneksi secara bersih.
                pass # Biarkan thread receive mati secara alami saat socket ditutup

if __name__ == '__main__':
    start_client()