import pickle

class SegmentoConfiavel:
    def __init__(self, seq_num, ack_num, dados, is_ack=False, is_fin=False):
        self.seq_num = seq_num      # número de sequência do pacote
        self.ack_num = ack_num      # ACK
        self.dados = dados          # payload da mensagem
        self.is_ack = is_ack        # flag que indica se é um pacote de ACK
        self.is_fin = is_fin        # flag que indica fim de conexão

    def serializar(self):
        return pickle.dumps(self)

    @staticmethod
    def desserializar(raw):
        return pickle.loads(raw)
