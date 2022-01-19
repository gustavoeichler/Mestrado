from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour
from datetime import datetime
from sys import argv
from random import uniform, randint
from Otimin import Otimizar_NOMA, Canal, db2pow, pow2db
import numpy as np
import pandas as pd
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaContractNetProtocol
from sys import argv
from random import uniform, randint
import numpy as np
import pandas as pd
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour
#import BaseLinePairing as PA
import Pairing_fairness as PA
from datetime import datetime
from sys import argv

class CompRequest(FipaRequestProtocol):
    """FIPA Request Behaviour of the Time agent.
    """
    def __init__(self, agent):
        super(CompRequest, self).__init__(agent=agent,
                                          message=None,
                                          is_initiator=False)

    def handle_request(self, message):
        super(CompRequest, self).handle_request(message)
        #display_message(self.agent.aid.localname, 'request message received')
        
        No = db2pow(-174)/1000
        Pt = db2pow(44)/1000
        DF = pd.read_csv('TABELA.csv',index_col=0)
        linha = {}
        linha2 = {}
        linha3 = {}
        linha4 = {} #Far user FNOMA
        linha5 = {} #Near user FNOMA
        linha6 = {} #Baseline
        NOMA_DB = {}
        for i in range(len(DF.columns)):
            row = list()
            row2 = list()
            row3 = list()
            row4 = list()
            row5 = list()
            row_Channel_Capacity = list()
            row_NOMA = list()
            row_BL = list()
            index = DF.columns[i]
            for j in range(len(DF.columns)):
                jndex = DF.columns[j]
                ans = Otimizar_NOMA(db2pow(DF[index]['canal']),db2pow(DF[jndex]['canal']),No,Pt,1,DF[index]['demanda'],DF[jndex]['demanda'])
                if i == j:
                    row.append(DF[index]['demanda'])
                    row2.append(ans['R_OMA_NU'])
                    row3.append(DF[index]['demanda'])
                    row4.append(DF[index]['demanda'])
                    row5.append(DF[index]['demanda'])
                    row_NOMA.append(1)
                    row_BL.append(DF[index]['demanda'])
                else:
                    #print(f'Par {index}-{jndex}')
                    
                    #message = ACLMessage(ACLMessage.INFORM)
                    #message.add_receiver(AID('Transmission_Agent_9999@localhost:9999'))
                    
                    row_Channel_Capacity.append(0)
                    

                    if ans['Status'] != 0:
                        reply = message.create_reply()
                        reply.set_performative(ACLMessage.INFORM)
                        reply.set_content(f'Par {index}-{jndex}--Usar OMA')
                        row.append(0)
                        row2.append(0)
                        row3.append(0)
                        row4.append(0)
                        row5.append(0)
                        row_BL.append(0)
                        row_NOMA.append(0)
                        self.agent.send(reply) 
                    else:
                        reply = message.create_reply()
                        reply.set_performative(ACLMessage.INFORM)
                        reply.set_content(f'Par {index}-{jndex}--Usar NOMA')  
                        row.append(ans['R_FU'])
                        row2.append(0)
                        row3.append(ans['SumRate'])
                        row4.append(ans['R_FNOMA_FU'])
                        row5.append(ans['R_FNOMA_NU'])
                        row_BL.append(ans['SumRate'])
                        row_NOMA.append(1)
                        self.agent.send(reply) 
                linha[i] = row
                linha2[i] = row2
                linha3[i] = row3
                linha4[i] = row4
                linha5[i] = row5
                NOMA_DB[i] = row_NOMA
                linha6[i] = row_BL
        DF = pd.DataFrame(linha)
            #DF = DF.set_index(DF.columns)
        DF.to_csv(f'0DF.csv')
        DF1 = pd.DataFrame(linha2)
        # DF1 = DF1.set_index(DF1.columns)
        DF1.to_csv(f'0DF1.csv')
        DF2 = pd.DataFrame(linha3)
        # DF1 = DF1.set_index(DF1.columns)
        DF2.to_csv(f'0DF2.csv')
        DF3 = pd.DataFrame(linha4)
        # DF1 = DF1.set_index(DF1.columns)
        DF3.to_csv(f'0DF3.csv')
        DF4 = pd.DataFrame(linha5)
        # DF1 = DF1.set_index(DF1.columns)
        DF4.to_csv(f'0DF4.csv')

        DF5 = pd.DataFrame(NOMA_DB)
        DF5.to_csv('NOMA_DB')

        DF6 = pd.DataFrame(linha6)
        DF6.to_csv('Baseline.csv')





class CompRequest2(FipaRequestProtocol):
    """FIPA Request Behaviour of the Clock agent.
    """
    def __init__(self, agent, message):
        super(CompRequest2, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)

    def handle_inform(self, message):
        pass
        #display_message(self.agent.aid.localname, message.content)



class CompContNet1(FipaContractNetProtocol):
    '''CompContNet1

       Initial FIPA-ContractNet Behaviour that sends CFP messages
       to other feeder agents asking for restoration proposals.
       This behaviour also analyzes the proposals and selects the
       one it judges to be the best.'''

    def __init__(self, agent, message):
        super(CompContNet1, self).__init__(
            agent=agent, message=message, is_initiator=True)
        self.cfp = message

    def handle_all_proposes(self, proposes):
        """
        """

        super(CompContNet1, self).handle_all_proposes(proposes)

        #display_message(self.agent.aid.name, 'Analyzing proposals...')
        tabela = {}
        # logic to select proposals by the higher available power.
        for messages in proposes:
            name = str(messages.sender).split("_")[2].split("@")[0]
            demand = float(str(messages.content).split(',')[0])
            channel_gain = float(str(messages.content).split(',')[1])
            distance = float(str(messages.content).split(',')[2])
            #display_message(self.agent.aid.name, f'Agente {name} = demanda:{demand}, ganho do canal: {pow2db((channel_gain))}, distancia = {distance}')
            tabela[name] = {'demanda': demand,'canal': pow2db((channel_gain)), 'distancia': distance}

        DF = pd.DataFrame.from_dict(tabela)
        DF.to_csv('TABELA.csv') 

        
               
            


    def handle_inform(self, message):
        """
        """
        super(CompContNet1, self).handle_inform(message)

        #display_message(self.agent.aid.name, 'INFORM message received')

    def handle_refuse(self, message):
        """
        """
        super(CompContNet1, self).handle_refuse(message)

        #display_message(self.agent.aid.name, 'REFUSE message received')

    def handle_propose(self, message):
        """
        """
        super(CompContNet1, self).handle_propose(message)

        #display_message(self.agent.aid.name, 'PROPOSE message received')

class CompContNet2(FipaContractNetProtocol):
    '''CompContNet2

       FIPA-ContractNet Participant Behaviour that runs when an agent
       receives a CFP message. A proposal is sent and if it is selected,
       the restrictions are analized to enable the restoration.'''

    def __init__(self, agent):
        super(CompContNet2, self).__init__(agent=agent,
                                           message=None,
                                           is_initiator=False)

    def handle_cfp(self, message):
        """
        """
        self.agent.call_later(0.1, self._handle_cfp, message)

    def _handle_cfp(self, message):
        """
        """
        super(CompContNet2, self).handle_cfp(message)

        self.message = message

        #display_message(self.agent.aid.name, 'CFP message received')
        reply = list()
        answer = self.message.create_reply()
        answer.set_performative(ACLMessage.PROPOSE)
        CG = self.agent.channel_gain
        DE = self.agent.spec_effi
        DI = self.agent.distance
        reply.append(DE)
        reply.append(CG)
        reply.append(DI)
        #print(reply)
        #print(type(CG))
        answer.set_content(f'{DE},{CG},{DI}')
        self.agent.send(answer)

    def handle_reject_propose(self, message):
        """
        """
        super(CompContNet2, self).handle_reject_propose(message)

        #display_message(self.agent.aid.name,
        #                'REJECT_PROPOSAL message received')

    def handle_accept_propose(self, message):
        """
        """
        super(CompContNet2, self).handle_accept_propose(message)

        #display_message(self.agent.aid.name,
         #               'ACCEPT_PROPOSE message received')

        answer = message.create_reply()
        answer.set_performative(ACLMessage.INFORM)
        answer.set_content('OK')
        self.agent.send(answer)

class Mudadist(TimedBehaviour):
    """Timed Behaviour of the Clock agent"""

    def __init__(self, agent, time, distance):
        super(Mudadist, self).__init__(agent, time)
        self.distance = distance

    def on_time(self):
        super(Mudadist, self).on_time()
        self.agent.channel_gain = float(Canal(self.distance,f=2 ,N=1))
        demand = [1,2,4,8,16,32]
        self.agent.spec_effi = demand[randint(0, 5)]
        #comp = CompContNet2(self)
        # self.agent.behaviours.append(comp)


class ComportTemporal(TimedBehaviour):
    """Timed Behaviour of the Clock agent"""

    def __init__(self, agent, time, message):
        super(ComportTemporal, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportTemporal, self).on_time()
        self.agent.send(self.message)

class Transmissao(TimedBehaviour):
    """Timed Behaviour of the Clock agent"""

    def __init__(self, agent, time, message):
        super(Transmissao, self).__init__(agent, time)
        self.message = message
        self.m=0
        self.sla = {}
        self.OMA = list()
        self.NOMA = list()
        self.BaselineNOMA = list()
        self.FixNOMA = list()
        self.OUTAGE = list()
        self.NOMA_PAIRS = list()
        self.BL_NOMA_PAIRS = list()
        self.FNOMA_PAIRS = list()

    def on_time(self):
        super(Transmissao, self).on_time()
        
        #print(self.m)
        Transmission = PA.TA(DF0=pd.read_csv('0DF.csv',index_col=0),DF1=pd.read_csv('0DF1.csv',index_col=0),DF2=pd.read_csv('0DF2.csv',index_col=0),DF3=pd.read_csv('0DF3.csv',index_col=0),DF4=pd.read_csv('0DF4.csv',index_col=0),DF5=pd.read_csv('Baseline.csv',index_col=0))
        self.m +=1
        self.OMA.append(Transmission['OMA'])
        self.NOMA.append(Transmission['AHNOMA'])
        self.BaselineNOMA.append(Transmission['Baseline_NOMA'])
        self.FixNOMA.append(Transmission['FixNOMA'])
        self.NOMA_PAIRS.append(Transmission['NOMA_PAIRS'])
        self.BL_NOMA_PAIRS.append(Transmission['Baseline_Pairs'])
        self.FNOMA_PAIRS.append(Transmission['FNOMA_PAIRS'])
        self.OUTAGE.append(Transmission['OUTAGE'])
        self.sla['OMA Sum rate'] = self.OMA
        self.sla['Architecture Sum rate'] = self.NOMA
        self.sla['Baseline Sum rate'] = self.BaselineNOMA
        self.sla['Fixed NOMA Sum rate'] = self.FixNOMA
        self.sla['Fixed NOMA Pairs'] = self.FNOMA_PAIRS
        self.sla['NOMA Pairs'] = self.NOMA_PAIRS
        self.sla['Baseline NOMA Pairs'] = self.BL_NOMA_PAIRS
        self.sla['Fixed NOMA Outage'] = self.OUTAGE
        KCT = pd.DataFrame(self.sla)
        KCT.to_csv('Arq.csv',)
        self.agent.send(self.message)        
        


class ServiceAgent(Agent):

    def __init__(self, aid, participants):
        super(ServiceAgent, self).__init__(aid=aid, debug=False)

        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.set_content('Aberto a propostas')

        for participant in participants:
            message.add_receiver(AID(name=participant))

        self.comport_request = CompContNet1(self, message)
        self.call_later(0.5, self.launch_contract_net_protocol, message)

        messagem = ACLMessage(ACLMessage.CFP)
        messagem.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        messagem.set_content('Atualizem a propostas')

        for participant in participants:
            messagem.add_receiver(AID(name=participant))
        self.comport_temp = ComportTemporal(self, 0.1, messagem)
        self.behaviours.append(self.comport_temp)
        self.comport_request = CompRequest(self)
        self.behaviours.append(self.comport_request)

    def launch_contract_net_protocol(self, message):
        comp = CompContNet1(self, message)
        self.behaviours.append(comp)
        comp.on_start()


class Devices(Agent):

    def __init__(self, aid, distance):
        super(Devices, self).__init__(aid=aid, debug=False)
        self.distance = distance
        self.channel_gain = float(Canal(self.distance,f=2, N=1))
        demand = [1,2,4,8,16,32]
        self.spec_effi = demand[randint(0, 5)]

        self.comport_temp = Mudadist(self,0.1, uniform(10, 150))
        comp = CompContNet2(self)
        self.behaviours.append(comp)
        self.behaviours.append(self.comport_temp)

class Transmission_Agent(Agent):
    def __init__(self, aid):
        super(Transmission_Agent, self).__init__(aid=aid, debug=False)

        # message that requests time of Time agent.
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=SA_agent_name))
        message.set_content('Pairs')

        self.comport_request = CompRequest2(self, message)
        self.comport_temp = ComportTemporal(self, 1, message)
        self.trans = Transmissao(self, 5, message)

        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)
        self.behaviours.append(self.trans)

           



if __name__ == "__main__":
    agents_per_process = 1
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        k = 1000
        participants = list()
        for i in range(1, 41):


            agent_name = f'User_Device_{port +2*i}@localhost:{port +2*i}'
            participants.append(agent_name)
            distance = uniform(10, 150)
            agente_part_1 = Devices(AID(name=agent_name), distance)
            agents.append(agente_part_1)

        #agent_name = 'agent_participant_{}@localhost:{}'.format(port + k, port + k)
        # participants.append(agent_name)
        #agente_part_2 = AgentParticipant(AID(name=agent_name),Canal(15),randint(1,10))
        # agents.append(agente_part_2)

        SA_agent_name = 'Service_Agent_{}@localhost:{}'.format(port, port)
        agente_init_1 = ServiceAgent(AID(name=SA_agent_name), participants)
        agents.append(agente_init_1)

        TA_agent_name = 'Transmission_Agent_{}@localhost:{}'.format(port-1, port-1)
        agente_init_2 = Transmission_Agent(AID(name=TA_agent_name))
        agents.append(agente_init_2)

        c += 1000

    start_loop(agents)