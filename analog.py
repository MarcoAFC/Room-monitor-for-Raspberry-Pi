import time
#thingspeak.com api
import thingspeak
#dht heat/humidity sensor
import Adafruit_DHT
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import math
from gpiozero import LED
ch = thingspeak.Channel(id=727460, write_key='HM0PNUXWAKN9MN8U')
led = LED(19)
GAIN = 1

# Cria uma instancia do ads 1115.
adc = Adafruit_ADS1x15.ADS1115()
sensor = Adafruit_DHT.DHT11
pin = 12
humidity, temperature = Adafruit_DHT.read_retry(sensor,pin)

lamps = 0.0
ac = 0.0
consumo = 0.0
custo = 0.0
projetor = 0.0
pc = 0.0
def soundChange(value):
    # lineariza os dados de som para representar a variacao de acordo com o valor base associado
    value = value*40.96/32767
    base = 16.5
    var = abs(value-base)
    return (var)


print('Reading ADS1x15 values, press Ctrl-C to quit...')

# Imprimir os canais em colunas
print('|    LIGHT    |    SOUND    | TEMPERATURE |   HUMIDITY  |'.format(*range(4)))
print('-' * 60)
# Main loop.
while True:
    atividade=0.0
    # Le todos os canais em uma lista
    values = [0]*4
    for i in range(4):
        # Le os valores usando o ganho escolhido
        values[i] = adc.read_adc(i, gain=GAIN, data_rate=860)
    #lineariza os valores de luminosidade
    values[0] = 0.15*math.log(1024.0/values[0], 2)+0.749994
    values[1] = soundChange(values[1])
    humidity, temperature = Adafruit_DHT.read_retry(sensor,pin)
    temp = [0]*2
    temp[0] = temperature
    temp[1] = humidity
    print('| {0:>6} | {1:>6} |'.format(*values),'| {0:>6} | {1:>6} |'.format(*temp))

    if (values[0]>0.2):
       #determina se as lampadas estao acesas para o calculo energetico, lamp 110 w
        lamps+=1
        #usa as lampadas acessas como indicador de atividade
        atividade+=0.2

    if (temp[0]<25  and temp[1]<60):
        # determina se os ac estao ligados para o calc energetico, ac 12000 btu = 1450 w
        ac+=1
        # se o ac esta ligado, considere 90% de chance de o pc estar ligado, consumo +-160w
        pc+=0.9
        # se o acestiver ligado, considere 70% de chance de o projetor estar ligado, 210 W
        projetor+=0.7
        # usa o ac como indicador de atividade
        atividade+=0.2
    #calcula o consumo
    consumo = (24*lamps/240) * 0.110 + (4*ac/240) * 1.450 + projetor * 0.210 + pc*0.160 #kwh
    custo = consumo*0.554
    
    #estima a atividade pelo ruido
    atividade += values[1]/8.3333
    ch.update({'field1':values[0], 'field2':values[1], 'field3':temp[0], 'field4':temp[1], 'field5':consumo, 'field6':custo, 'field7':atividade});
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(14.5)

