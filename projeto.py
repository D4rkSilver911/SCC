import salabim as sim
import random

n_placas_por_dia = int((5280+440*8)/22)
n_rodas_por_dia = int((2640*4+5280*4)/22)
n_produtos_por_dia = int((5280+2640+440)/22)
Conjunto_placa = 0
Conjunto_Roda = 0
n_skate = 0
n_placas = 0
n_rodas = 0
horario = "aberta"


class Dia(sim.Component):
    def process(self):
        global horario
        while True:
            horario = "aberta"
            yield self.hold(60*8)
            horario = "fechado"
            yield self.hold(16*60)
            
#Generator
class Gerador(sim.Component):
    def process(self):
        global horario
        while (horario == "aberta"):
            
           
           

            for _ in range(n_placas_por_dia):
                Prancha()
                yield self.hold(sim.Uniform(5, 15).sample())
            for _ in range(n_rodas_por_dia):
                Roda()
                yield self.hold(sim.Uniform(5,15).sample())
            for _ in range(n_produtos_por_dia):
                Finish()
                yield self.hold(sim.Uniform(5, 15).sample())
            

#Etapas da placa
class Prancha(sim.Component):
    def process(self):
        global n_placas
        self.enter(pressqueue) #Entrar na Queue do Pressing
        yield self.request((prensa, 4)) #Pedir as prensas necessárias
        self.leave(pressqueue) #Sair do Queue do Pressing
        yield self.hold(100) #Tempo do Pressing
        self.release((prensa, 4)) #Libertar as prensas
        self.enter(storage1queue) #Após terminar o pressing, meter no armazem

        yield self.hold(24*60) #Ficar no storage1 1 dia para dps continuar

        storage1queue.pop() #Retirar do storage1
        self.enter(cutqueue) # Entrar na queue no cutting
        yield self.request((worker, 3)) #Pedir os workers
        self.leave(cutqueue) #Sair da Queue do Cutting
        yield self.hold(60) #Tempo do Cutting
        self.release((worker, 3)) #Libertar os workers

       
        self.enter(finqueue) #Entrar na Fin Queue
        yield self.request((worker, 1)) #Pedir 1 worker
        self.leave(finqueue) #Sair do Queue
        yield self.hold(15) #Tempo do Finishing
        self.release((worker, 1)) #Libertar o Worker

        
        self.enter(paintqueue) #Entrar Paint Queue
        yield self.request((worker, 1)) #Pedir 1 worker
        self.leave(paintqueue) #Sair da Paint Queue
        yield self.hold(20) #Tempo do Painting
        self.release((worker, 1)) #Libertar worker
     
        self.enter(storage2queue)#Após estar pronta entra no storage2
        yield self.hold(24*60) #Esperar na area de secagem 1 dia
        n_placas+=24 #Um lote de placas criados
        prancha.set_capacity(n_placas) #Aumentar o numero de resources disponiveis
    
        

#Roda
class Roda(sim.Component):
    def process(self):
        global n_rodas

        self.enter(foundryqueue)
        yield self.request((fornalha, 1))
        self.leave(foundryqueue)
        yield self.hold(55)
        self.release((fornalha, 1))

        self.enter(storage3queue)
        yield self.hold(24*60)
        
        storage3queue.pop()
        self.enter(machiningqueue)
        yield self.request((torno, 2))
        self.leave(machiningqueue)
        yield self.hold(60)
        self.release((torno,2))

       
        self.enter(printingqueue)
        yield self.request((impressora, 1))
        self.leave(printingqueue)
        yield self.hold(20)
        self.release((impressora, 1))

       
        self.enter(storage4queue)
        yield self.hold(24*60)
        n_rodas += 192
        roda.set_capacity(n_rodas)

  


class Finish(sim.Component):
    def process(self):
        global Conjunto_placa, Conjunto_Roda, n_skate, n_rodas, n_placas
        escolha = random.choice(finish)
        if(escolha == "packing"):
            self.enter(packpranchaqueue)
            yield self.request((worker,2), (prancha, 8*12))
            self.leave(packpranchaqueue)

            for _ in range(8*12):
                storage2queue.pop()
            yield self.hold(10)
            self.release((worker, 2))
            Conjunto_placa += 12
        elif(escolha == "packingwheel"):
            self.enter(packwheelqueue)
            yield self.request((maq_embalagem, 1), (roda, 4*48))
            self.leave(packwheelqueue)
            for _ in range(4*48):
                storage4queue.pop()
            yield self.hold(30)
            self.release((maq_embalagem, 1))
            Conjunto_Roda += 48
        elif(escolha == "assembly"):
            self.enter(assemblyqueue)
            yield self.request((worker, 2), (prancha, 24), (roda, 24*4))
            self.leave(assemblyqueue)
            for _ in range(24):
                storage2queue.pop()
            for _ in range(24*4):
                storage4queue.pop()
            yield self.hold(30)
            self.release((worker, 2))
            n_skate += 24
        
env = sim.Environment(time_unit = "minutes")
Dia()
Gerador()



#Filas de espera
pressqueue = sim.Queue("Pressing Queue")
cutqueue = sim.Queue("Cutting Queue")
finqueue = sim.Queue("Finishing Queue")
paintqueue = sim.Queue("Painting Queue")
packpranchaqueue = sim.Queue("Packing Prancha Queue")
packwheelqueue = sim.Queue("Packing Wheel Queue")
assemblyqueue = sim.Queue("Assembly Queue")
foundryqueue = sim.Queue("Foundry Queue")
machiningqueue = sim.Queue("Machining Queue")
printingqueue = sim.Queue("Printing Queue")

finish = ["packing", "packingwheel",
          "assembly", "assembly", "assembly", "packing", "packingwheel",
          "assembly", "assembly", "assembly"]

#Resources
prancha = sim.Resource("prancha")
roda = sim.Resource("rodas")
worker = sim.Resource("Worker", capacity=3)
prensa = sim.Resource("prensa", capacity=4)
fornalha = sim.Resource("fornalha", capacity=5)
torno = sim.Resource("torno", capacity=2)
impressora = sim.Resource("impressora", capacity=1)
maq_embalagem = sim.Resource("maq_embalagem", capacity=1)

#Fila Espera Armazem
storage1queue = sim.Queue("storage1")
storage2queue = sim.Queue("storage2")
storage3queue = sim.Queue("storage3")
storage4queue = sim.Queue("storage4")

env.run(till=34560) #22 dias

print()
pressqueue.print_statistics()
storage1queue.print_statistics()
cutqueue.print_statistics()
finqueue.print_statistics()
paintqueue.print_statistics()
storage2queue.print_statistics()
packpranchaqueue.print_statistics()
packwheelqueue.print_statistics()
assemblyqueue.print_statistics()
foundryqueue.print_statistics()
storage3queue.print_statistics()
machiningqueue.print_statistics()
printingqueue.print_statistics()
storage4queue.print_statistics()

print("Skates: "+str(int(n_skate)))
print("Caixas de Rodas: " + str(int(Conjunto_Roda)))
print("Caixa de placas: "+ str(int(Conjunto_placa)))

