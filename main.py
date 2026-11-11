import os 
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from datetime import datetime
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from clientemodbus import ClienteMODBUS
from kivy.core.window import Window

class ClienteModbusApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modbus = ClienteMODBUS()
        self.evento_recorrente = None

    def build(self):
        Window.maximize()
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"

    def registrar_log(self, mensagem: str):
        horario = datetime.now().strftime("%H:%M:%S")
        nova_linha = f"[{horario}] {mensagem}"
        campo_log = self.root.ids.log_output

        if campo_log.text:
            linhas = campo_log.text.split("\n")[-14:]
            linhas.append(nova_linha)
            campo_log.text = "\n".join(linhas)
        else:
            campo_log.text = nova_linha

    def conectar(self):
        """Vinculado a: on_release: app.conectar()"""
        ip = self.root.ids.ip_input.text.strip() or "127.0.0.1"
        porta_str = self.root.ids.port_input.text.strip() or "502"

        try:
            porta = int(porta_str)
        except ValueError:
            self.registrar_log("Erro: A porta deve ser um número inteiro (ex: 502).")
            return

        ok, msg = self.modbus.conectar(ip, porta)
        self.registrar_log(msg)

    def ler_dados(self):
        """Vinculado a: on_release: app.ler_dados()"""
        if not self.modbus.esta_conectado:
            self.registrar_log("Erro: Conecte ao servidor Modbus antes de ler!")
            return

        if self.root.ids.cb_recorrente.active:
            self._iniciar_clock_recorrente()
        else:
            self._executar_leitura_unica()

    def escrever_dados(self):
        """Vinculado a: on_release: app.escrever_dados()"""
        if not self.modbus.esta_conectado:
            self.registrar_log("Erro: Conecte ao servidor Modbus antes de escrever!")
            return

        addr_str = self.root.ids.address_input.text.strip()
        valor_str = self.root.ids.value_input.text.strip()

        if not addr_str:
            self.registrar_log("Erro: Informe o Endereço Modbus.")
            return
        if not valor_str:
            self.registrar_log("Erro: Informe o Valor para escrita.")
            return

        try:
            if self.root.ids.chk_coil.active:
                _, msg = self.modbus.escrever_coil(int(addr_str), valor_str)
            elif self.root.ids.chk_register.active:
                _, msg = self.modbus.escrever_holding_register(int(addr_str), valor_str)
            elif self.root.ids.chk_float.active:
                _, msg = self.modbus.escrever_float(int(addr_str), valor_str)
            elif self.root.ids.chk_bits.active:
                _, msg = self.modbus.escrever_bits(addr_str, valor_str)
            else:
                msg = "Erro: Selecione um tipo de dado (Coils, Registers, Float ou Bits)."
        except ValueError:
            msg = "Erro: O endereço deve ser um número inteiro."

        self.registrar_log(msg)

    def toggle_recorrente(self, checkbox, value):
        """Vinculado a: on_active: app.toggle_recorrente(*args)"""
        if value:
            if not self.modbus.esta_conectado:
                self.registrar_log("Aviso: Conecte ao servidor para iniciar a leitura recorrente.")
                return
            self._iniciar_clock_recorrente()
        else:
            self._parar_clock_recorrente()
            self.registrar_log("Leitura recorrente desativada.")

    def _iniciar_clock_recorrente(self):
        if self.evento_recorrente is None:
            self.registrar_log("Leitura recorrente iniciada (intervalo: 1s)...")
            self._executar_leitura_unica()
            self.evento_recorrente = Clock.schedule_interval(self._ciclo_recorrente, 1.0)

    def _parar_clock_recorrente(self):
        if self.evento_recorrente is not None:
            self.evento_recorrente.cancel()
            self.evento_recorrente = None

    def _ciclo_recorrente(self, dt):
        if not self.modbus.esta_conectado:
            self._parar_clock_recorrente()
            self.root.ids.cb_recorrente.active = False
            self.registrar_log("Conexão perdida. Leitura recorrente interrompida.")
            return
        self._executar_leitura_unica()

    def _executar_leitura_unica(self):
        addr_str = self.root.ids.address_input.text.strip()
        if not addr_str:
            self.registrar_log("Erro: Informe o Endereço Modbus para leitura.")
            self._parar_clock_recorrente()
            return

        try:
            if self.root.ids.chk_coil.active:
                _, msg = self.modbus.ler_coil(int(addr_str))
            elif self.root.ids.chk_register.active:
                _, msg = self.modbus.ler_holding_register(int(addr_str))
            elif self.root.ids.chk_float.active:
                _, msg = self.modbus.ler_float(int(addr_str))
            elif self.root.ids.chk_bits.active:
                _, msg = self.modbus.ler_bits(addr_str)
            else:
                msg = "Erro: Selecione um tipo de dado (Coils, Registers, Float ou Bits)."
        except ValueError:
            msg = "Erro: O endereço deve ser um número inteiro."

        self.registrar_log(msg)


if __name__ == "__main__":
    ClienteModbusApp().run()