from os import stat
from ortools.linear_solver import pywraplp
import numpy as np
import pandas as pd
from random import uniform


# Funções utilizadas

def db2pow(ydB):
    """Função que converte uma entrada em decibels (dB) em potência (W)"""
    return np.power(10,(ydB/10))

def pow2db(ypow):
    """Função que converte uma entrada em potência (W) em decibels (dB)"""
    return 10*np.log10(ypow)

def Canal(d,f=2,N=200):
    """ Função que retorna o canal em potência de um usuário dada a distância em metros e a frequencia da portadora em GHz"""
    
    #np.random.seed(639869500)
    K = 8e-4
    d0 = 1
    gamma = 2
    sigma2_psi = 6
    #pathloss = K*((d0/d)**gamma)
    shadowing_db = np.random.randn(1)*np.sqrt(sigma2_psi)
    shadowing  = 10**(0.1*shadowing_db)
    fast_fading = np.random.exponential(1,N)
    
    pathloss = db2pow(-(39.081*np.log10(d) + 13.54 + 20*np.log10(f)))    
    
    #db2pow(-(20*np.log10(f)+20*np.log10(d) -27.55))
    #print(f'Fast Fading:{fast_fading}')
    #print(f'Shadowing:{shadowing}')
    #print(f'Pathloss: {db2pow(pathloss)}')f
    return abs(pathloss*shadowing*fast_fading)**2

def Otimizar_NOMA(Canal1,Canal2,No,Pt, Banda, R1_min,R2_min):
    """Função para otimizar uma transmissão NOMA.

    Canal 1 = potencia de atenuação do canal referente ao usuário proximo (W)
    Canal 2 = potencia de atenuação do canal referente ao usuário distante (W)
    No      = Figura de ruído presente no sistema (W)
    Pt      = Potencia de Transmissão (W)
    Banda   = Largura de Banda de transmissão (Hz)
    R1_min  = Throughput Alvo para o usuário 1 (Bps/Hz)
    """
    # Criando o Solver
    solver = pywraplp.Solver('LinearProgrammingExample',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    #solver = pywraplp.Solver.CreateSolver('GLOP')
    X = solver.NumVar(-solver.infinity(),solver.infinity(),'x')
    Y_line = solver.NumVar(-solver.infinity(),solver.infinity(), 'y_line')
    
    #Constantes
    A = Pt*(Canal1)
    B = Pt*(Canal2)

 


    #Constraint 1
    solver.Add(X >= (2**(R1_min/Banda) - 1))

    # Constraint 2: X - AB Y_line + ANo Y_line + (A/B) = 0
    solver.Add(X - (A*Y_line) - (A*No*Y_line/B) +(A/B) == 0)

    # Constraint 3: R2 >0
    solver.Add(Y_line <=(1/No))
    #solver.Add(Y_line <= (1/((No*2**(-R2_min/Banda)))))
    # Constraint 4: alpha <= 0.5
    solver.Add(X*No/A <= 0.5)
    # Constraint 5: alpha >= 0
    solver.Add(X*No/A >= 0)
    solver.Minimize(Y_line)
    status = solver.Solve()
    #print(status)
        
    Falpha = 0.25 
    if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:   
        alpha = X.solution_value()*No/A
    else:
        alpha = 0
    R2 = Banda*np.log2(1+(B*(1-alpha)/((B*alpha)+No)))
    R1 = Banda*np.log2(1+(A*alpha/No))
    OMA2 = Banda*np.log2(1+(B/No))
    OMA1 = Banda*np.log2(1+(A/No))
    SNROMA1 = (A/No)
    SNROMA2 = (B/No)
    SNR2= (B*(1-alpha)/((B*alpha)+No))
    SNR1= (A*alpha/No)
    FNOMA2 = Banda*np.log2(1+(B*(1-Falpha)/((B*Falpha)+No)))
    FNOMA1 = Banda*np.log2(1+(A*Falpha/No))
    FSNR2 = (B*(1-Falpha)/((B*Falpha)+No))
    FSNR1 = (A*Falpha/No)
    ans = R1 + R2

    if R2<R2_min:
        status = 2
    else:
        status=0
            
    return {'SumRate': ans, 'R_NU':R1/Banda, 'R_FU':R2/Banda, 'alpha': alpha, 'SNR_NU': SNR1,'SNR_FU': SNR2, 'R_OMA_NU': OMA1/Banda,'R_OMA_FU': OMA2/Banda, 'SNR_OMA_NU':SNROMA1, 'SNR_OMA_FU':SNROMA2, 'R_FNOMA_NU': FNOMA1/Banda,'R_FNOMA_FU': FNOMA2/Banda, 'SNR_FNOMA_NU':FSNR1, 'SNR_FNOMA_FU':FSNR2, 'Status':status}
    
    
    #return [ans,R1/Banda,R2/Banda,alpha, (SNR1),(SNR2),status,OMA2/Banda,SNROMA2,OMA1/Banda,SNROMA1,FNOMA1/Banda,FNOMA2/Banda,FSNR1,FSNR2]

