import socket
import threading
import time
import random
from SegmentoConfiavel import SegmentoConfiavel

TIMEOUT = 3.0
JANELA = 4

class Sender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lock = threading.Lock()

        self.buffer_enviados = {}

      
        self.proximo_seq = 0

        
        self.acks_recebidos = {}

        
        self.receiver_addr = None

    def iniciar(self):
        ip_sender = input("IP do sender [127.0.0.1]: ").strip() or "127.0.0.1"
        porta_sender = input("Porta do sender [5001]: ").strip()
        porta_sender = int(porta_sender) if porta_sender else 5001

        ip_receiver = input("IP do receiver [127.0.0.1]: ").strip() or "127.0.0.1"
        porta_receiver = input("Porta do receiver [5000]: ").strip()
        porta_receiver = int(porta_receiver) if porta_receiver else 5000

        self.receiver_addr = (ip_receiver, porta_receiver)
        self.sock.bind((ip_sender, porta_sender))

        
        t_ack = threading.Thread(target=self._receber_acks, daemon=True)
        t_ack.start()

        self._loop_envio()

    def _receber_acks(self):
        while True:
            try:
                dados, _ = self.sock.recvfrom(65535)
                seg = SegmentoConfiavel.desserializar(dados)
                if seg.is_ack:
                    seq = seg.ack_num
                    with self.lock:
                        if seq in self.buffer_enviados:
                            _, _, msg_texto = self.buffer_enviados[seq]
                            del self.buffer_enviados[seq]
                            self.acks_recebidos[seq] = True
                    print(f"Mensagem id {seq} recebida pelo receiver.")
            except Exception:
                pass

    def _temporizador_pacote(self, seq_num):
        
        time.sleep(TIMEOUT)
        with self.lock:
            if seq_num in self.buffer_enviados:
                seg, _, msg_texto = self.buffer_enviados[seq_num]
                print(f"Mensagem id {seq_num} deu timeout, reenviando.")
                self.sock.sendto(seg.serializar(), self.receiver_addr)
                
                novo_timer = threading.Thread(
                    target=self._temporizador_pacote, args=(seq_num,), daemon=True
                )
                self.buffer_enviados[seq_num] = (seg, novo_timer, msg_texto)
                novo_timer.start()

    def _enviar_segmento(self, seg, msg_texto, seq_num):
        self.sock.sendto(seg.serializar(), self.receiver_addr)
        timer = threading.Thread(
            target=self._temporizador_pacote, args=(seq_num,), daemon=True
        )
        with self.lock:
            self.buffer_enviados[seq_num] = (seg, timer, msg_texto)
        timer.start()

    def _loop_envio(self):
        while True:
            msg = input("\nDigite a mensagem a ser enviada: ").strip()
            if not msg:
                continue

            seq = self.proximo_seq
            self.proximo_seq += 1

            print("\nOpções de envio:")
            print("1. Normal")
            print("2. Lenta")
            print("3. Perda")
            print("4. Fora de ordem")
            print("5. Duplicada")
            opcao = input("Escolha a opção: ").strip()

            opcoes = {"1": "normal", "2": "lenta", "3": "perda", "4": "fora de ordem", "5": "duplicada"}
            opcao_texto = opcoes.get(opcao, "normal")

            seg = SegmentoConfiavel(seq_num=seq, ack_num=0, dados=msg.encode())

            print(f"Mensagem \"{msg}\" enviada como {opcao_texto} com id {seq}")

            if opcao_texto == "normal":
                self._enviar_segmento(seg, msg, seq)

            elif opcao_texto == "lenta":
                
                def envio_lento(s, m, sn):
                    time.sleep(TIMEOUT + 1.5)
                    self.sock.sendto(s.serializar(), self.receiver_addr)
                    timer = threading.Thread(
                        target=self._temporizador_pacote, args=(sn,), daemon=True
                    )
                    with self.lock:
                        self.buffer_enviados[sn] = (s, timer, m)
                    timer.start()
                
                timer = threading.Thread(
                    target=self._temporizador_pacote, args=(seq,), daemon=True
                )
                with self.lock:
                    self.buffer_enviados[seq] = (seg, timer, msg)
                timer.start()
                t = threading.Thread(target=envio_lento, args=(seg, msg, seq), daemon=True)
                t.start()

            elif opcao_texto == "perda":
                
                timer = threading.Thread(
                    target=self._temporizador_pacote, args=(seq,), daemon=True
                )
                with self.lock:
                    self.buffer_enviados[seq] = (seg, timer, msg)
                timer.start()

            elif opcao_texto == "fora de ordem":
               
                seq2 = self.proximo_seq
                self.proximo_seq += 1
                msg2 = input(f"Digite a segunda mensagem (será enviada antes, id {seq2} antes de {seq}): ").strip()
                seg2 = SegmentoConfiavel(seq_num=seq2, ack_num=0, dados=msg2.encode())
                print(f"Mensagem \"{msg2}\" enviada como fora de ordem com id {seq2}")
                
                self._enviar_segmento(seg2, msg2, seq2)
                time.sleep(0.1)
                
                self._enviar_segmento(seg, msg, seq)

            elif opcao_texto == "duplicada":
                self._enviar_segmento(seg, msg, seq)
                time.sleep(0.1)
                
                self.sock.sendto(seg.serializar(), self.receiver_addr)


if __name__ == "__main__":
    s = Sender()
    s.iniciar()
