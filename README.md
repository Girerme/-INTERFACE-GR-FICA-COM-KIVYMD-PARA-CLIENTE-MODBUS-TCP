# Atividade - Interface Gráfica com KivyMD para Cliente Modbus TCP

**Disciplina:** ENE118 – Informática Industrial  
**Instituição:** Universidade Federal de Juiz de Fora (UFJF)

## Integrantes e Divisão de Responsabilidades

- **Guilherme de Almeida Paula:** Desenvolvimento da interface gráfica em KivyMD (`modbusclient.kv`), estruturação de layouts e estilização dos widgets (`MDTextField`, `MDButton`, `MDCheckbox` e `MDLabel`).
- **Henrique Brandão Bairral Muniz:** Implementação da classe de comunicação e conversão de dados (`clientemodbus.py`), lógica de controle da aplicação principal (`main.py`), agendamento de leituras periódicas com `Clock` e servidor Modbus de testes (`servidormodbus.py`).

## Estrutura do Projeto

- `modbusclient.kv`: Definição visual da interface gráfica em KivyMD.
- `main.py`: Inicialização da aplicação (`ModbusClientApp`), gerenciamento de eventos da interface e controle do ciclo de leitura recorrente via `kivy.clock.Clock`.
- `clientemodbus.py`: Classe `ClienteMODBUS` responsável exclusivamente pela comunicação TCP, leitura, escrita e conversão de tipos de dados (Coils, Holding Registers, Float IEEE 754 e manipulação de Bits).
- `servidormodbus.py`: Servidor Modbus TCP local para simulação e validação das operações de leitura e escrita.
- `requirements.txt`: Lista de dependências do projeto.

## Instalação e Execução

1. Instale as dependências no seu ambiente virtual:
   pip install -r requirements.txt

2. Inicie o servidor Modbus de teste (em um terminal, a partir da raiz do projeto):
   python servidormodbus.py
   *Servidor configurado por padrão para rodar em 127.0.0.1 na porta 502.*

3. Execute a aplicação gráfica (em outro terminal, a partir da raiz do projeto):
   python main.py

## Comportamento da Aplicação e Modos de Operação

A aplicação separa a camada visual da lógica de protocolo. Na interface, o usuário informa o **IP** e a **Porta** do servidor e clica em **Conectar**. Em seguida, seleciona o tipo de dado desejado por meio dos checkboxes:

- **Coils:** Leitura e escrita de variáveis booleanas (aceita `0`, `1`, `True` ou `False`).
- **Registers (Holding Registers):** Leitura e escrita de valores inteiros de 16 bits sem sinal (`0` a `65535`).
- **Float:** Leitura e escrita de números em ponto flutuante de 32 bits (padrão IEEE 754), ocupando dois registradores consecutivos a partir do endereço informado.
- **Bits:** Permite operar tanto sobre os 16 bits de um Holding Register simultaneamente quanto sobre um único bit específico (`0` a `15`):
  - **Múltiplos bits (16 bits):** Informe apenas o endereço do registrador no campo de endereço (ex: `20`). Na leitura, exibe a palavra binária de 16 bits; na escrita, informe a sequência binária desejada no campo de valor (ex: `0000000011110000`).
  - **Bit individual:** Informe o endereço no formato `registrador.bit` (ex: `20.0` para o bit 0 ou `20.3` para o bit 3). Na escrita, informe `0` ou `1` no campo de valor para modificar apenas o bit selecionado sem alterar os demais 15 bits do registrador.
- **Leitura Recorrente:** Ao marcar a opção **Leitura recorrente**, a aplicação utiliza o objeto `Clock` do Kivy (`Clock.schedule_interval`) para realizar leituras automáticas a cada `1.0` segundo no endereço e tipo de dado selecionados, registrando os resultados com carimbo de tempo no console da interface.

## Mapa de Dados do Servidor de Teste

O arquivo `servidormodbus.py` disponibiliza todos os endereços de Coils e Holding Registers para leitura e escrita livre (ex: endereços `0` a `999`) e atualiza automaticamente quatro registradores a cada 1 segundo para simular variáveis dinâmicas de processo[cite: 1]:

| Endereço | Tipo | Descrição Simulada | Faixa de Valores Sorteados |
| :---: | :---: | :--- | :---: |
| `1000` | Holding Register (4X) | Temperatura | 400 a 499 |
| `1001` | Holding Register (4X) | Pressão | 1000 a 4999 |
| `1002` | Holding Register (4X) | Umidade | 20 a 39 |
| `1003` | Holding Register (4X) | Consumo | 40 a 99 |
| `0` – `999` | Coils / Holding Registers | Área livre para testes de leitura/escrita (Int, Float e Bits) | Definido pelo usuário |

## Detalhes Técnicos e Padrões Adotados

- **Representação de Ponto Flutuante (Float 32 bits):** Utilizam-se as funções `encode_ieee`, `decode_ieee`, `long_list_to_word` e `word_list_to_long` do módulo `pyModbusTCP.utils` para converter valores `float` no padrão IEEE 754 distribuídos em 2 Holding Registers consecutivos de 16 bits.
- **Manipulação de Bits (Read-Modify-Write):** Na escrita de um bit individual de um registrador, o cliente realiza primeiro a leitura do valor inteiro de 16 bits atual do Holding Register, aplica máscaras lógicas *bitwise* (`|` com deslocamento `1 << bit` para ativar, ou `& ~` para desativar) e reescreve o registrador atualizado, preservando o estado dos demais bits.
