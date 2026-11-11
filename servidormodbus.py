from pyModbusTCP.server import ModbusServer
from time import sleep
import random


class ServidorMODBUS:
    """
    Servidor Modbus TCP para testes locais.
    Atualiza os registradores 1000 a 1003 a cada 1 segundo e mantém os demais
    endereços (ex: 0 a 999) livres para leitura e escrita manual pela interface.
    """

    def __init__(self, host_ip="127.0.0.1", port=502):
        self._host = host_ip
        self._port = port
        self._server = ModbusServer(host=host_ip, port=port, no_block=True)

    def run(self):
        try:
            self._server.start()
            print(f"Servidor Modbus em execução em {self._host}:{self._port} (Ctrl+C para sair)")
            while True:
                self._server.data_bank.set_holding_registers(1000, [random.randrange(400, 500)])   # Temperatura
                self._server.data_bank.set_holding_registers(1001, [random.randrange(1000, 5000)]) # Pressão (16 bits)
                self._server.data_bank.set_holding_registers(1002, [random.randrange(20, 40)])     # Umidade
                self._server.data_bank.set_holding_registers(1003, [random.randrange(40, 100)])    # Consumo
                sleep(1)
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            self._server.stop()


if __name__ == "__main__":
    s = ServidorMODBUS("127.0.0.1", 502)
    s.run()