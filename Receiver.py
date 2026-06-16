import socket
import threading
from SegmentoConfiavel import SegmentoConfiavel

JANELA = 4

class Receiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lock = threading.Lock()

        # Próximo seq esperado (base da janela)
        self.esperado = 0

        # Buffer de pacotes fora de ordem recebidos: {seq_num: segmento}
        self.buffer_fora_ordem = {}

        # Conjunto de seq_nums já recebidos (para detectar duplicatas)
        self.recebidos = set()

    def iniciar(self):
        ip = input("IP do receiver [127.0.0.1]: ").strip() or "127.0.0.1"
        porta = input("Porta do receiver [5000]: ").strip()
        porta = int(porta) if porta else 5000

        self.sock.bind((ip, porta))
        print(f"Receiver escutando em {ip}:{porta}")
        self._loop_recepcao()

    def _enviar_ack(self, seq_num, sender_addr):
        ack = SegmentoConfiavel(seq_num=0, ack_num=seq_num, dados=b"", is_ack=True)
        self.sock.sendto(ack.serializar(), sender_addr)

    def _entregar_em_ordem(self):
        while self.esperado in self.buffer_fora_ordem:
            seg = self.buffer_fora_ordem.pop(self.esperado)
            conteudo = seg.dados.decode(errors="replace")
            print(f"Mensagem id {self.esperado} recebida na ordem, entregando para a camada de aplicação.")
            print(f"  >> Conteúdo: \"{conteudo}\"")
            self.esperado += 1

    def _loop_recepcao(self):
        while True:
            try:
                dados, sender_addr = self.sock.recvfrom(65535)
                seg = SegmentoConfiavel.desserializar(dados)

                with self.lock:
                    seq = seg.seq_num

                
                    if seq in self.recebidos:
                        print(f"Mensagem id {seq} recebida de forma duplicada")
                
                        self._enviar_ack(seq, sender_addr)
                        continue

                    self.recebidos.add(seq)

                    if seq == self.esperado:
                        
                        self.buffer_fora_ordem[seq] = seg
                        self._entregar_em_ordem()
                    elif seq > self.esperado:
                       
                        self.buffer_fora_ordem[seq] = seg
                        faltando = [i for i in range(self.esperado, seq) if i not in self.recebidos]
                        print(f"Mensagem id {seq} recebida fora de ordem, ainda não recebidos os identificadores {faltando}")
                    else:
                        
                        print(f"Mensagem id {seq} recebida de forma duplicada")

                    
                    self._enviar_ack(seq, sender_addr)

            except Exception as e:
                pass


if __name__ == "__main__":
    r = Receiver()
    r.iniciar()
