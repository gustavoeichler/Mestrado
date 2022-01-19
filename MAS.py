from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour

from datetime import datetime
from sys import argv

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaContractNetProtocol
from sys import argv
from random import uniform, randint
from Otimin import Otimizar_NOMA, Canal, db2pow
import numpy as np
import pandas as pd


class CompContNet1(FipaContractNetProtocol):
    '''CompContNet1

       Initial FIPA-ContractNet Behaviour that sends CFP messages
       to other feeder agents asking for restoration proposals.
       This behaviour also analyzes the proposals and selects the
       one it judges to be the best.'''

    def __init__(self, agent, message, m):
        super(CompContNet1, self).__init__(
            agent=agent, message=message, is_initiator=True)
        self.cfp = message

    def handle_all_proposes(self, proposes):
        """
        """

        super(CompContNet1, self).handle_all_proposes(proposes)

        best_proposer = None
        higher_power = 0.0
        other_proposers = list()
        display_message(self.agent.aid.name, 'Analyzing proposals...')
        CG_DB = {}
        DE_DB = {}
        t = 0
        DB = {}
        # logic to select proposals by the higher available power.
        m = 0

        for message in proposes[t:]:
            content = message.content
            # print(content)
            now = datetime.now()
            now.strftime('%d/%m/%Y - %H:%M:%S')
            CG = content[0:-1]
            # print(CG)
            DE = content[-1:]
            #DI = float(content.split(',')[2])
            # print(CG)
            # print(DE)
            name = str(message.sender).split("_")[2].split("@")[0]
            #power = float(content)
            display_message(self.agent.aid.name,
                            'Analyzing proposal {t}'.format(t=t))
            display_message(self.agent.aid.name,
                            f'Agent {name}: CG = {float(CG)}dB, DE = {int(DE)}bps/Hz')
            CG_DB[f'Proposal {name}'] = float(CG)
            DE_DB[f'Proposal {name}'] = int(DE)
            DB[name] = {'index': t, 'time': now.strftime(
                '%d/%m/%Y - %H:%M:%S'), 'agent': name, 'Channel Gain': CG, 'Demand': DE}

            t = t+1

            DATA = pd.DataFrame(DB).T

            DATA.append(DATA, ignore_index=True)

            # print(CG_DB)
            # print(DE_DB)
            linha = {}
            linha2 = {}
            linha3 = {}
            linha4 = {} #Far user FNOMA
            linha5 = {} #Near user FNOMA
            No = db2pow(-174)/1000
            Pt = db2pow(44)/1000

            Banda = 1   # 1MHz
            R1_min = 1
            for i in CG_DB:
                #print(f'i = {i}, {CG_DB[i][199]},{len(CG_DB[i])}')
                #print(f'NU Agent {i}: ')
                row = list()
                row2 = list()
                row3 = list()
                row4 = list()
                row5 = list()
                for j in CG_DB:
                    if CG_DB[j] > CG_DB[i]:
                        row.append(0)
                        row2.append(0)
                        row3.append(0)
                        row4.append(0)
                        row5.append(0)
                        
                    else:

                        # print(ans)
                        if j == i:
                            OMA = np.log2(1 + ((CG_DB[i]*Pt)/(No)))
                            # print(ans[1])
                            row.append(DE_DB[i])
                            row2.append(OMA)
                            row3.append(DE_DB[i])
                            row4.append(DE_DB[i])
                            row5.append(DE_DB[i])
                            # print(f'OMA:{ans}')
                        else:
                            ans = Otimizar_NOMA(
                                CG_DB[i], CG_DB[j], No, Pt, Banda, DE_DB[i], DE_DB[j])
                            row.append(ans[2])
                            row2.append(0)
                            row3.append(ans[0])
                            row4.append(ans[12])
                            row5.append(ans[11])
                            #print(f'FU Agent{j} NOMA:{ans[0]}')
                    linha[i] = row
                    linha2[i] = row2
                    linha3[i] = row3
                    linha4[i] = row4
                    linha5[i] = row5

            DF = pd.DataFrame(linha)
            #DF = DF.set_index(DF.columns)
            DF.to_csv(f'{m}DF.csv')
            DF1 = pd.DataFrame(linha2)
        # DF1 = DF1.set_index(DF1.columns)
            DF1.to_csv(f'{m}DF1.csv')
            DF2 = pd.DataFrame(linha3)
        # DF1 = DF1.set_index(DF1.columns)
            DF2.to_csv(f'{m}DF2.csv')
            DF3 = pd.DataFrame(linha4)
        # DF1 = DF1.set_index(DF1.columns)
            DF3.to_csv(f'{m}DF3.csv')
            DF4 = pd.DataFrame(linha5)
        # DF1 = DF1.set_index(DF1.columns)
            DF4.to_csv(f'{m}DF4.csv')

        DATA.to_csv(f'DATA.csv')
        proposes = list()

    def handle_inform(self, message):
        """
        """
        super(CompContNet1, self).handle_inform(message)

        display_message(self.agent.aid.name, 'INFORM message received')

    def handle_refuse(self, message):
        """
        """
        super(CompContNet1, self).handle_refuse(message)

        display_message(self.agent.aid.name, 'REFUSE message received')

    def handle_propose(self, message):
        """
        """
        super(CompContNet1, self).handle_propose(message)

        display_message(self.agent.aid.name, 'PROPOSE message received')


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
        self.agent.call_later(1.0, self._handle_cfp, message)

    def _handle_cfp(self, message):
        """
        """
        super(CompContNet2, self).handle_cfp(message)
        self.message = message

        display_message(self.agent.aid.name, 'CFP message received')

        answer = self.message.create_reply()
        answer.set_performative(ACLMessage.PROPOSE)
        CG = self.agent.pot_disp
        DE = self.agent.spec_effi
        
        CG = np.append(CG, DE)

        DI = self.agent.distance
        answer.set_content(CG)
        self.agent.send(answer)

    def handle_reject_propose(self, message):
        """
        """
        super(CompContNet2, self).handle_reject_propose(message)

        display_message(self.agent.aid.name,
                        'REJECT_PROPOSAL message received')

    def handle_accept_propose(self, message):
        """
        """
        super(CompContNet2, self).handle_accept_propose(message)

        display_message(self.agent.aid.name,
                        'ACCEPT_PROPOSE message received')

        answer = message.create_reply()
        answer.set_performative(ACLMessage.INFORM)
        answer.set_content('OK')
        self.agent.send(answer)


class AgentInitiator(Agent):

    def __init__(self, aid, participants, m=0):
        super(AgentInitiator, self).__init__(aid=aid, debug=False)

        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.set_content('60.0')

        for participant in participants:
            message.add_receiver(AID(name=participant))

        self.comport_request = CompContNet1(self, message, m)
        self.comport_temp = ComportTemporal(self, 10, message)

        self.behaviours.append(self.comport_request)
        m = m+1
        self.behaviours.append(self.comport_temp)

    def launch_contract_net_protocol(self, message):
        comp = CompContNet1(self, message)
        self.behaviours.append(comp)
        comp.on_start()


class AgentParticipant(Agent):

    def __init__(self, aid, distance):
        super(AgentParticipant, self).__init__(aid=aid, debug=False)
        self.distance = distance
        self.pot_disp = Canal(self.distance, N=1)
        demand = [1,2,4,8,16,32]
        self.spec_effi = demand[randint(0, 5)]

        self.comport_temp = Mudadist(self, 15, uniform(10, 150))
        comp = CompContNet2(self)
        self.behaviours.append(comp)
        self.behaviours.append(self.comport_temp)


class Mudadist(TimedBehaviour):
    """Timed Behaviour of the Clock agent"""

    def __init__(self, agent, time, distance):
        super(Mudadist, self).__init__(agent, time)
        self.distance = distance

    def on_time(self):
        super(Mudadist, self).on_time()
        self.agent.pot_disp = Canal(self.distance, N=1)
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


# class TimeAgent(Agent):
#    """Class that defines the Time agent."""
#    def __init__(self, aid):
#        super(TimeAgent, self).__init__(aid=aid, debug=False)
#
#        self.comport_request = CompRequest(self)
#
#        self.behaviours.append(self.comport_request)


class ClockAgent(Agent):
    """Class thet defines the Clock agent."""

    def __init__(self, aid, time_agent_name):
        super(ClockAgent, self).__init__(aid=aid)

        # message that requests time of Time agent.
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=time_agent_name))
        message.set_content('time')

        self.comport_request = CompContNet1(self, message)
        self.comport_temp = ComportTemporal(self, 2000.0, message)

        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)


if __name__ == "__main__":
    agents_per_process = 1
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        k = 1000
        participants = list()
        for i in range(1, 4):

            agent_name = f'User_Device_{port +i}@localhost:{port +i}'
            participants.append(agent_name)
            distance = uniform(10, 150)
            agente_part_1 = AgentParticipant(AID(name=agent_name), distance)
            agents.append(agente_part_1)

        #agent_name = 'agent_participant_{}@localhost:{}'.format(port + k, port + k)
        # participants.append(agent_name)
        #agente_part_2 = AgentParticipant(AID(name=agent_name),Canal(15),randint(1,10))
        # agents.append(agente_part_2)

        agent_name = 'Service_Agent_{}@localhost:{}'.format(port, port)
        agente_init_1 = AgentInitiator(AID(name=agent_name), participants)
        agents.append(agente_init_1)

        c += 1000

    start_loop(agents)
