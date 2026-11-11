from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils


class ClienteMODBUS:
    """
    Classe responsável exclusivamente pela comunicação Modbus TCP,
    leitura, escrita e conversão de dados (Coils, Holding Registers, Float e Bits).
    """

    def __init__(self, server_ip="127.0.0.1", porta=502):
        self._cliente = ModbusClient(host=server_ip, port=int(porta), auto_open=False, timeout=2.0)

    def conectar(self, server_ip: str, porta: int) -> tuple[bool, str]:
        """Configura IP e Porta e estabelece a conexão com o servidor Modbus."""
        try:
            if self._cliente.is_open:
                self._cliente.close()

            self._cliente.host = server_ip.strip()
            self._cliente.port = int(porta)

            if self._cliente.open():
                return True, f"Conectado com sucesso em {self._cliente.host}:{self._cliente.port}"
            return False, f"Falha ao conectar em {self._cliente.host}:{self._cliente.port}"
        except ValueError:
            return False, "Erro: A porta deve ser um número inteiro."
        except Exception as e:
            return False, f"Erro na conexão: {e}"

    def desconectar(self) -> tuple[bool, str]:
        """Fecha a conexão TCP."""
        self._cliente.close()
        return True, "Conexão encerrada."

    @property
    def esta_conectado(self) -> bool:
        return self._cliente.is_open

    # COILS

    def ler_coil(self, addr: int) -> tuple[bool, str]:
        res = self._cliente.read_coils(int(addr), 1)
        if res is not None:
            return True, f"Coil [{addr}] = {bool(res[0])} ({int(res[0])})"
        return False, f"Erro ao ler Coil no endereço {addr}."

    def escrever_coil(self, addr: int, valor_str: str) -> tuple[bool, str]:
        limpo = valor_str.strip().lower()
        if limpo in ("1", "true", "on", "v", "sim"):
            val_bool = True
        elif limpo in ("0", "false", "off", "f", "nao", "não"):
            val_bool = False
        else:
            return False, "Valor inválido para Coil. Use 1/0 ou True/False."

        ok = self._cliente.write_single_coil(int(addr), val_bool)
        if ok:
            return True, f"Escrita OK -> Coil [{addr}] = {val_bool}"
        return False, f"Erro ao escrever Coil no endereço {addr}."

    # HOLDING REGISTERS

    def ler_holding_register(self, addr: int) -> tuple[bool, str]:
        res = self._cliente.read_holding_registers(int(addr), 1)
        if res is not None:
            return True, f"Holding Register [{addr}] = {res[0]}"
        return False, f"Erro ao ler Holding Register no endereço {addr}."

    def escrever_holding_register(self, addr: int, valor_str: str) -> tuple[bool, str]:
        try:
            val_int = int(valor_str.strip())
            if not (0 <= val_int <= 65535):
                return False, "Erro: Holding Register (16 bits) aceita valores de 0 a 65535."
        except ValueError:
            return False, "Erro: Informe um número inteiro para o Holding Register."

        ok = self._cliente.write_single_register(int(addr), val_int)
        if ok:
            return True, f"Escrita OK -> Holding Register [{addr}] = {val_int}"
        return False, f"Erro ao escrever no Holding Register {addr}."

    # FLOAT

    def ler_float(self, addr: int) -> tuple[bool, str]:
        addr_int = int(addr)
        regs = self._cliente.read_holding_registers(addr_int, 2)
        if regs is not None and len(regs) == 2:
            val_32 = utils.word_list_to_long(regs)[0]
            val_float = utils.decode_ieee(val_32)
            return True, f"Float [{addr_int}, {addr_int + 1}] = {val_float:.4f}"
        return False, f"Erro ao ler Float nos endereços {addr_int} e {addr_int + 1}."

    def escrever_float(self, addr: int, valor_str: str) -> tuple[bool, str]:
        try:
            addr_int = int(addr)
            val_float = float(valor_str.strip().replace(",", "."))
        except ValueError:
            return False, "Erro: Informe um número decimal válido para Float (ex: 25.4)."

        val_32 = utils.encode_ieee(val_float)
        regs = utils.long_list_to_word([val_32])
        ok = self._cliente.write_multiple_registers(addr_int, regs)
        if ok:
            return True, f"Escrita OK -> Float [{addr_int}, {addr_int + 1}] = {val_float:.4f}"
        return False, f"Erro ao escrever Float nos endereços {addr_int} e {addr_int + 1}."

    # BITS DE UM REGISTRADOR

    @staticmethod
    def _separar_endereco_bit(addr_raw: str) -> tuple[int, int | None]:
        """
        Interpreta o campo de endereço:
        - '1000' -> (1000, None) -> Opera nos 16 bits do registrador 1000.
        - '1000.3' ou '1000:3' -> (1000, 3) -> Opera apenas no bit 3 do registrador 1000.
        """
        texto = addr_raw.strip().replace(":", ".")
        if "." in texto:
            partes = texto.split(".", 1)
            return int(partes[0]), int(partes[1])
        return int(texto), None

    def ler_bits(self, addr_raw: str) -> tuple[bool, str]:
        try:
            addr, bit_idx = self._separar_endereco_bit(addr_raw)
        except ValueError:
            return False, "Use 'endereco' (ex: 1000) para 16 bits ou 'endereco.bit' (ex: 1000.3) para 1 bit."

        res = self._cliente.read_holding_registers(addr, 1)
        if res is None:
            return False, f"Erro ao ler registrador {addr}."

        reg_val = res[0]
        bits_list = [(reg_val >> i) & 1 for i in range(16)]

        if bit_idx is not None:
            if not (0 <= bit_idx <= 15):
                return False, "Erro: O índice do bit deve estar entre 0 e 15."
            bit_val = int(bits_list[bit_idx])
            return True, f"Reg [{addr}] Bit {bit_idx} = {bit_val} (Bin: {reg_val:016b})"

        bits_formatados = " ".join(str(int(b)) for b in reversed(bits_list))
        return True, f"Reg [{addr}] Bits (15..0): {bits_formatados} (Int: {reg_val})"

    def escrever_bits(self, addr_raw: str, valor_str: str) -> tuple[bool, str]:
        try:
            addr, bit_idx = self._separar_endereco_bit(addr_raw)
        except ValueError:
            return False, "Use 'endereco' (ex: 1000) ou 'endereco.bit' (ex: 1000.3)."

        limpo = valor_str.strip()

        if bit_idx is None and ":" in limpo:
            try:
                b_str, v_str = limpo.split(":", 1)
                bit_idx = int(b_str.strip())
                limpo = v_str.strip()
            except ValueError:
                return False, "Formato inválido. Use 'bit:valor' (ex: 3:1) ou sequência binária."

        if bit_idx is not None:
            if not (0 <= bit_idx <= 15):
                return False, "Erro: O índice do bit deve estar entre 0 e 15."
            if limpo.lower() not in ("0", "1", "true", "false"):
                return False, "Para bit individual, o valor deve ser 0 ou 1."

            bit_bool = limpo.lower() in ("1", "true")
            res = self._cliente.read_holding_registers(addr, 1)
            if res is None:
                return False, f"Erro ao ler registrador {addr} antes de alterar o bit."

            reg_atual = res[0]
            novo_reg = (reg_atual | (1 << bit_idx)) if bit_bool else (reg_atual & ~(1 << bit_idx))

            if self._cliente.write_single_register(addr, novo_reg):
                return True, f"Escrita OK -> Reg [{addr}] Bit {bit_idx} = {int(bit_bool)} (Bin: {novo_reg:016b})"
            return False, f"Erro ao escrever bit {bit_idx} no registrador {addr}."

        bin_clean = limpo.replace(" ", "").replace(",", "")
        if not bin_clean or not all(c in "01" for c in bin_clean) or len(bin_clean) > 16:
            return False, (
                "Para múltiplos bits, digite até 16 bits com 0 e 1 (ex: 00001111). "
                "Para 1 bit, use endereço 'reg.bit' (ex: 1000.3)."
            )

        novo_reg = int(bin_clean, 2)
        if self._cliente.write_single_register(addr, novo_reg):
            return True, f"Escrita OK -> Reg [{addr}] = {novo_reg:016b} (Int: {novo_reg})"
        return False, f"Erro ao escrever múltiplos bits no registrador {addr}."