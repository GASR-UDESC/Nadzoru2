import time
import random
import threading
import RPi.GPIO as GPIO


NUM_EVENTOS = {{ num_eventos }}
NUM_SUPERVISORES = {{ num_supervisores }}
EVENTOS = [{% for ev in eventos %}"EV_{{ ev }}"{% if not loop.last %}, {% endif %}{% endfor %}]
EV_CONTROLAVEL = {{ ev_controlavel }}

SUP_EVENTOS = {{ sup_matriz_eventos }}
SUP_ESTADO_INICIAL = {{ sup_estado_inicial }}


SUP_POSICAO_DADOS = {{ sup_posicao_dados }} 
SUP_DADOS = {{ sup_dados }} 


EV_PINO = {{ ev_pino }}
EV_PINO_ESTADO_INICIAL = {{ ev_pino_estado_inicial }}
EV_PINO_PULL_UP = {{ ev_pino_pull_up }}
EV_TIPO = {{ ev_tipo | safe }}
EV_TEMPO_PULSO = {{ ev_tempo_pulso }}

class SupervisorSCT:
    def __init__(self):
        self.num_eventos = NUM_EVENTOS
        self.num_supervisores = NUM_SUPERVISORES
        
        self.mapa_eventos = {ev: i for i, ev in enumerate(EVENTOS)}
        self.ev_controlavel = EV_CONTROLAVEL
        self.sup_eventos = SUP_EVENTOS
        self.sup_estado_atual = list(SUP_ESTADO_INICIAL)
        
        self.sup_posicao_dados = SUP_POSICAO_DADOS
        self.sup_dados = SUP_DADOS

        self.callbacks = {}
        self.buffer_entrada = []
        self.ultimos_eventos = [0] * self.num_eventos

    def adicionar_callback(self, evento, acao, checar_entrada, dados_sup):
        self.callbacks[evento] = {'acao': acao, 'checar_entrada': checar_entrada, 'dados_sup': dados_sup}

    def executar_passo(self):
        self.buffer_entrada = [] 
        self.atualizar_entrada()

        eventos_nao_controlaveis = self.buffer_entrada
        while eventos_nao_controlaveis:
            evento = eventos_nao_controlaveis.pop(0)
            if self.transicao_habilitada(evento):
                self.fazer_transicao(evento)
                self.executar_callback(evento)

        existe_acao, acao_escolhida = self.obter_proximo_controlavel()
        if existe_acao:
            self.fazer_transicao(acao_escolhida)
            self.executar_callback(acao_escolhida)

    def ler_entrada(self, indice_ev):
        nome_evento = self.obter_nome_evento(indice_ev)
        if indice_ev < self.num_eventos and nome_evento in self.callbacks and self.callbacks[nome_evento]['checar_entrada']:
            return self.callbacks[nome_evento]['checar_entrada'](self.callbacks[nome_evento]['dados_sup'])
        return False

    def atualizar_entrada(self):
        for i in range(self.num_eventos):
            if not self.ev_controlavel[i]: 
                if EV_PINO[i] != 0: 
                    if self.ler_entrada(i):
                        self.buffer_entrada.append(i)
                        self.ultimos_eventos[i] = 1


    def obter_posicao_estado(self, supervisor, estado):
        posicao = self.sup_posicao_dados[supervisor]    
        for s in range(0, estado):                   
            en = self.sup_dados[posicao]            
            posicao += en * 3 + 1       
        return posicao

    def transicao_habilitada(self, ev):
        for i in range(self.num_supervisores):
            if self.sup_eventos[i][ev]: 
                posicao = self.obter_posicao_estado(i, self.sup_estado_atual[i])
                num_transicoes = self.sup_dados[posicao]
                posicao += 1 

                habilitado = False
                while num_transicoes:
                    num_transicoes -= 1
                    valor = self.obter_valor(self.sup_dados[posicao])
                    if valor == ev:
                        habilitado = True
                        break
                    posicao += 3
                
                if not habilitado:
                    return False
        return True

    def fazer_transicao(self, ev):
        for i in range(self.num_supervisores):
            if self.sup_eventos[i][ev]: 
                posicao = self.obter_posicao_estado(i, self.sup_estado_atual[i])
                num_transicoes = self.sup_dados[posicao]
                posicao += 1 

                while num_transicoes:
                    num_transicoes -= 1
                    valor = self.obter_valor(self.sup_dados[posicao])
                    if valor == ev:
                        byte_alto = self.sup_dados[posicao + 1] * 256
                        byte_baixo = self.sup_dados[posicao + 2]
                        self.sup_estado_atual[i] = byte_alto + byte_baixo
                        break
                    posicao += 3 

    def executar_callback(self, indice_ev):
        nome_evento = self.obter_nome_evento(indice_ev)
        if indice_ev < self.num_eventos and nome_evento in self.callbacks and self.callbacks[nome_evento]['acao']:
            self.callbacks[nome_evento]['acao'](self.callbacks[nome_evento]['dados_sup'])

    def obter_proximo_controlavel(self):
        ativos = self.obter_eventos_controlaveis_ativos()
        if not all(v == 0 for v in ativos):
            posicao_aleatoria = random.randint(0, 1000000000) % ativos.count(1)
            for i in range(self.num_eventos):
                if not posicao_aleatoria and ativos[i]:
                    return True, i
                elif ativos[i]:
                    posicao_aleatoria -= 1
        return False, None

    def obter_eventos_controlaveis_ativos(self):
        eventos = [1 if self.ev_controlavel[i] else 0 for i in range(self.num_eventos)]
        
        for i in range(self.num_supervisores):
            ev_desabilitar = [1] * self.num_eventos
            
            for j in range(self.num_eventos):
                if not self.sup_eventos[i][j]:
                    ev_desabilitar[j] = 0

            posicao = self.obter_posicao_estado(i, self.sup_estado_atual[i])
            num_transicoes = self.sup_dados[posicao]
            posicao += 1

            while num_transicoes:
                num_transicoes -= 1
                valor = self.obter_valor(self.sup_dados[posicao])
                ev_desabilitar[valor] = 0
                posicao += 3 

            for j in range(self.num_eventos):
                if ev_desabilitar[j] == 1 and eventos[j]:
                    eventos[j] = 0
        return eventos

    def obter_valor(self, indice):
        if isinstance(indice, str): return self.mapa_eventos[indice]    
        return indice
    
    def obter_nome_evento(self, indice):
        if isinstance(indice, int): return list(self.mapa_eventos.keys())[list(self.mapa_eventos.values()).index(indice)]
        return indice

flags_eventos = {i: False for i in range(NUM_EVENTOS) if EV_CONTROLAVEL[i] == 0}

def callback_gpio(canal_pino):
    time.sleep(0.02) 
    estado_atual = GPIO.input(canal_pino)
    print(f"\n[Hardware] Pino {canal_pino} -> {'HIGH' if estado_atual else 'LOW'}")

    for i in range(NUM_EVENTOS):
        if EV_CONTROLAVEL[i] == 0:
            for j in range(len(EV_PINO[i])):
                if EV_PINO[i][j] == canal_pino:
                    tipo_ev = str(EV_TIPO[i][j]).lower()
                    if (estado_atual == GPIO.HIGH and tipo_ev == 'rising') or (estado_atual == GPIO.LOW and tipo_ev == 'falling'):
                        flags_eventos[i] = True

def checar_entrada_generica(dados_sup, indice_evento):
    if flags_eventos.get(indice_evento, False):
        flags_eventos[indice_evento] = False 
        return True
    return False

def aplicar_pulso_thread(pino, tempo, tipo_ev):
    if tipo_ev == 'pulse_lh':
        GPIO.output(pino, GPIO.LOW)
        time.sleep(tempo)
        GPIO.output(pino, GPIO.HIGH)
    else:
        GPIO.output(pino, GPIO.HIGH)
        time.sleep(tempo)
        GPIO.output(pino, GPIO.LOW)

def acao_generica(dados_sup, indice_evento):
    for j in range(len(EV_PINO[indice_evento])):
        pino = EV_PINO[indice_evento][j]
        tipo_ev = str(EV_TIPO[indice_evento][j]).lower()
        
        if pino == 0 or tipo_ev == 'none': continue 
            
        print(f"\n[Ação] Disparando '{EVENTOS[indice_evento]}' no pino {pino} ({tipo_ev.upper()})")
        
        if tipo_ev == 'high':
            GPIO.output(pino, GPIO.HIGH)
        elif tipo_ev == 'low':
            GPIO.output(pino, GPIO.LOW)
        elif tipo_ev.startswith('pulse'):
            tempo = EV_TEMPO_PULSO[indice_evento][j] if j < len(EV_TEMPO_PULSO[indice_evento]) else 1.0
            threading.Thread(target=aplicar_pulso_thread, args=(pino, tempo, tipo_ev), daemon=True).start()

def configurar_hardware():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pinos_configurados = set()

    for i in range(NUM_EVENTOS):
        for j in range(len(EV_PINO[i])):
            pino = EV_PINO[i][j]
            tipo_ev = str(EV_TIPO[i][j]).lower()
            
            if pino == 0 or tipo_ev == 'none' or pino in pinos_configurados:
                continue
                
            pinos_configurados.add(pino)
            
            if tipo_ev in ['falling', 'rising']: 
                config_pull_up = GPIO.PUD_UP if EV_PINO_PULL_UP[i][j] == 1 else GPIO.PUD_DOWN
                GPIO.setup(pino, GPIO.IN, pull_up_down=config_pull_up)
                GPIO.add_event_detect(pino, GPIO.BOTH, callback=callback_gpio, bouncetime=200)
            else: 
                estado_inicial = GPIO.HIGH if EV_PINO_ESTADO_INICIAL[i][j] == 1 else GPIO.LOW
                GPIO.setup(pino, GPIO.OUT)
                GPIO.output(pino, estado_inicial)

def iniciar_sistema():
    configurar_hardware()
    print("\n[INFO] Sistema Inicializado. Abordagem Memory Safe Ativa.")
    supervisor = SupervisorSCT()
    
    for i in range(NUM_EVENTOS):
        nome_evento = EVENTOS[i]
        acao = lambda ds, idx=i: acao_generica(ds, idx)
        checar = lambda ds, idx=i: checar_entrada_generica(ds, idx) if EV_CONTROLAVEL[idx] == 0 else None
        supervisor.adicionar_callback(nome_evento, acao, checar, None)

    try:
        while True:
            supervisor.executar_passo()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n[ALERTA] Desligando...")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    iniciar_sistema()
