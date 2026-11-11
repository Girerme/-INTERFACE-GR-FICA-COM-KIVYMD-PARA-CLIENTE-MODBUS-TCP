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
   ```bash
   pip install -r requirements.txt
