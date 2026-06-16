# 📡 Protocolo de Transporte Confiável — Simulador UDP

Simulação de um protocolo de transporte confiável sobre UDP, implementando os mecanismos fundamentais de controle de transmissão presentes em protocolos como o TCP. Desenvolvido em Python como projeto acadêmico para a disciplina de Redes de Computadores.

---

## 🧠 Conceitos implementados

- **Janela deslizante (Sliding Window)** com tamanho configurável (`JANELA = 4`)
- **Numeração de sequência** para ordenação e identificação de pacotes
- **Temporizador com retransmissão automática** em caso de timeout
- **Buffer de reordenação** no receptor para lidar com pacotes fora de ordem
- **Detecção de duplicatas** no receptor
- **ACK cumulativo** com confirmação individual por pacote

---

## 🗂️ Estrutura do projeto

```
.
├── Sender.py              # Remetente — envia mensagens com diferentes comportamentos
├── Receiver.py            # Receptor — recebe, reordena e confirma pacotes
└── SegmentoConfiavel.py   # Modelo do segmento (serialização com pickle)
```

---

## ⚙️ Como executar

### Pré-requisitos

- Python 3.8+
- Nenhuma dependência externa — apenas a biblioteca padrão do Python

### 1. Iniciar o Receiver

```bash
python Receiver.py
```

Ao iniciar, informe o IP e a porta onde o receptor vai escutar (padrão: `127.0.0.1:5000`).

### 2. Iniciar o Sender

```bash
python Sender.py
```

Ao iniciar, informe o IP/porta do sender e o IP/porta do receiver para conectar.

---

## 🧪 Modos de envio simulados

Ao enviar uma mensagem, o remetente oferece 5 modos de envio para testar diferentes cenários de rede:

| Opção | Modo | Descrição |
|-------|------|-----------|
| 1 | **Normal** | Entrega imediata e confiável |
| 2 | **Lenta** | Atraso superior ao timeout, forçando retransmissão |
| 3 | **Perda** | Pacote não é enviado; o timeout dispara a retransmissão |
| 4 | **Fora de ordem** | Duas mensagens enviadas em ordem invertida |
| 5 | **Duplicada** | Mesmo pacote enviado duas vezes consecutivas |

---

## Fluxo de funcionamento

```
Sender                         Receiver
  |                               |
  |── seg(seq=N) ───────────────► |  Recebe pacote
  |                               |  Se em ordem → entrega à aplicação
  |                               |  Se fora de ordem → armazena no buffer
  |◄─────────────── ACK(ack=N) ── |
  |                               |
  |  [timeout] → reenvia seg(N)   |
```

---

## Detalhes técnicos

- **Transporte subjacente:** UDP (`SOCK_DGRAM`)
- **Serialização:** `pickle` (módulo `SegmentoConfiavel`)
- **Concorrência:** `threading` para gerenciar temporizadores e recepção de ACKs em paralelo
- **Timeout padrão:** 3 segundos (`TIMEOUT = 3.0`)
- **Tamanho da janela:** 4 pacotes (`JANELA = 4`)

---

##  Contexto acadêmico

Este projeto simula os mecanismos da camada de transporte descritos no livro *Redes de Computadores e a Internet* (Kurose & Ross), em especial o protocolo **Go-Back-N** e o **Selective Repeat**, com foco em:

- Controle de fluxo
- Retransmissão seletiva
- Reordenação de pacotes
- Detecção e descarte de duplicatas
