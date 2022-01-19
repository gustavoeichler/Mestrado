from __future__ import print_function
import pandas as pd
import numpy as np
import math
# Vamos importar o solver linear do ORTOOLS

from ortools.linear_solver import pywraplp
# Vamos importar o numpy como uma ferramenta auxiliar


solver = pywraplp.Solver.CreateSolver('GLOP')


def calculo(matriz):
    N = len(matriz)
    soma = 0
    for i in range(N):
        for j in range(N):
            if i == j:
                if matriz[i, j] == 1:
                    pass
                else:
                    pass
            else:
                if matriz[i, j] == 1:
                    soma += 1
                else:
                    pass

    return soma


def mi2ai(i, j, line_length):
    return i*line_length+j


def ai2mi(index, line_length):
    return [maph.floor(index/line_length), index % line_length]


def ajuste(tabela):
    tabela.index = tabela.columns
    asd = sorted(list(tabela.columns))
    tabela = tabela.reindex(asd, axis=1)
    tabela = tabela.reindex(asd, axis=0)
    return tabela


def TA(DF0, DF1, DF2, DF3, DF4, DF5):
    DF_NOMA = ajuste(DF0)
    DF1 = ajuste(DF1)
    DF2 = ajuste(DF2)
    DF3 = ajuste(DF3)
    DF4 = ajuste(DF4)
    DF5 = ajuste(DF5)
    Channel_Capacity = np.diag(DF1)  # Capacidade do canal

    Baseline = DF5
    User_Demand = np.diag(DF0)  # Demanda do Usuário
    User_Demand[0]
    N = len(Channel_Capacity)
    IM = np.zeros((N, N))
    DF_NOMA = np.matrix(DF_NOMA)
    DF2 = np.matrix(DF2)
    print(Channel_Capacity)
    '''	for i in range(N):
			for j in range(N):
				if i == j:

					if Channel_Capacity[i]<DF2[i,j]:
						IM[i,j] = Channel_Capacity[i]
					else:
						IM[i,j] = User_Demand[i]
				else:
					IM[i,j] = DF_NOMA[i,j]   '''

    for i in range(N):
        for j in range(N):
            if i == j:
                IM[i, j] = User_Demand[i]
                # print(f'{Channel_Capacity[i]}<{IM[i,j]}')
                if Channel_Capacity[i] < IM[i, j]:
                    IM[i, j] = Channel_Capacity[i]
                    # print(f'Trocou indice {i},{j}, antes era {User_Demand[i]}, agora é {IM[i,j]} ')
                else:
                    pass
            else:
                IM[i, j] = DF_NOMA[i, j]

    for i in range(N):
        for j in range(N):
            if i == j:
                pass
            else:
                if IM[i, i]+IM[j, j] <= IM[i, j]:
                    pass
                else:
                    IM[i, j] = 0

    Baseline = np.matrix(Baseline)

    for i in range(N):
        for j in range(N):
            if i == j:
                Baseline[i, i] = User_Demand[i]
                if Channel_Capacity[i] < Baseline[i, i]:
                    Baseline[i, j] = Channel_Capacity[i]
                else:
                    pass
            else:
                Baseline[i, j] = Baseline[i, j]
    solver = pywraplp.Solver.CreateSolver('SCIP')
    FU = list()
    for i in range(0, N):
        for j in range(0, N):
            FU.append(solver.IntVar(0, 1, f'FU_{i}_{j}'))

    head = 1

    for j in range(N):
        ct = solver.Constraint(1, 1, str(head))
        # print(f'Restrição {head}:')
        for i in range(N):
            if i == j:
                ct.SetCoefficient(FU[mi2ai(j, i, N)], 1)
                # print(f'{FU[mi2ai(j,i,N)]}+',end='')
            else:
                ct.SetCoefficient(FU[mi2ai(j, i, N)], 1)
                # print(f'{FU[mi2ai(j,i,N)]}+',end='')
                ct.SetCoefficient(FU[mi2ai(i, j, N)], 1)
                # if i == N-1:
                # print(f'{FU[mi2ai(i,j,N)]}')
                # else:
                # print(f'{FU[mi2ai(i,j,N)]}+',end='')
        head += 1

    ct = solver.Constraint(N, N, str(head))
    # print(f'Restrição {head}')
    for i in range(N):
        for j in range(N):
            if i == j:
                ct.SetCoefficient(FU[mi2ai(i, j, N)], 1)
            else:
                ct.SetCoefficient(FU[mi2ai(i, j, N)], 2)

            # if i  == N-1 and j ==N-1:
                # print(f'{FU[mi2ai(i,j,N)]} == {N}')
            # else:
                # print(f'{FU[mi2ai(i,j,N)]}+',end='')

    # #Executaremos o solver
    objective = solver.Objective()
    for j in range(N):
        for i in range(N):
            objective.SetCoefficient(FU[mi2ai(i, j, N)], IM[i, j])

    objective.SetMaximization()


    solver.Solve()

    # print('Solution:')
    # print('Valor objetivo =', (objective.Value()))
    pair = 0
    matriz = np.zeros(shape=(N, N))
    Fmatriz = np.zeros(shape=(N, N))
    Omatriz = np.zeros(shape=(N, N))
    matriz1 = np.zeros(shape=(N, N))
    conta = 0
    for i in range(0, N):
        for j in range(0, N):
            matriz[i, j] = (int(FU[mi2ai(i, j, N)].solution_value()))
            conta += (int(FU[mi2ai(i, j, N)].solution_value()))
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                matriz[i, j] = (int(FU[mi2ai(i, j, N)].solution_value()))
                conta += (int(FU[mi2ai(i, j, N)].solution_value()))
                if int(FU[mi2ai(i, j, N)].solution_value()) == 1:
                    matriz[i, i] = 0
                    matriz[j, j] = 0
    usuario_atendido = list(DF1.columns)
    tot = 0
    ftot = 0
    outage = 0
    NomaP = 0
    FNomaP = 0
    print(f'Conta AHNOMA = {conta}')
    for i in range(0, N):
        for j in range(0, N):

            if matriz[i, j] == 1:
                if i == j:
                    Omatriz[i, j] = 1
                    Fmatriz[i, j] = 1
                    # print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc[i,i]}')
                    # print(f'Used {(Aloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
                    usuario_atendido.remove(DF1.columns[j])
                    tot += IM[i, i]
                    ftot += IM[i, i]
                    # print(Aloc[i,j])
                    # ftot += FNOMA.iloc[i,j]
                else:
                    # print(f'NOMA Pair {pair} Near  User: {FU[j]}, data rate = {Aloc[j,j]}')
                    # print(f'NOMA Pair {pair} Far  User: {FU[i]}, data rate = {DF_NOMA.iloc[i,j]}')
                    NomaP += 1
                    # print(f'FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}')
                    # print(f'FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
                    # print(f'Gain over OMA:{(Aloc.iloc[i,j]/np.diag(Aloc)[j])*100}% ')
                    # print(Aloc[i,j])

                    tot += IM[i, j]
                    if DF3.iloc[i, j] >= DF_NOMA[i, i] and DF4.iloc[j, j] >= DF_NOMA[j, j]:
                        # print(f'alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}')
                        # print(f'alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
                        FNomaP += 1
                        ftot += DF4.iloc[i, j]
                        ftot += DF3.iloc[j, j]
                        # print(Aloc[i,j])
                        Fmatriz[i, j] = 1
                        # usuario_atendido.remove(DF_NOMA.columns[j])
                        # usuario_atendido.remove(DF_NOMA.index[i])

                    else:
                        # print(f'Não alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc[j,j]}')
                        # print(f'Não alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc[i,i]}')
                        outage += 1
                        Fmatriz[i, i] = 1
                        Fmatriz[j, j] = 1
                        Fmatriz[i, j] = 0
                        # print(Aloc[i,j])
                        # print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc[i,i]}')
                        # print(f'Used {(Aloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
                        # usuario_atendido.remove(DF_NOMA.columns[j])
                        tot += DF_NOMA[j, i]
                        ftot += DF4.iloc[i, j]
                        ftot += DF3.iloc[i, j]
                        pass
                    pair = pair + 1
            else:
                Omatriz[i, i] = 1

    matriz1 = matriz

    solver1 = pywraplp.Solver.CreateSolver('SCIP')
    FU1 = list()
    for i in range(0, N):
        for j in range(0, N):
            FU1.append(solver1.IntVar(0, 1, f'FU_{i}_{j}'))
    # print ('Numero de variaveis =', solver1.NumVariables())

    head = 1

    for j in range(N):
        ct1 = solver1.Constraint(1, 1, str(head))
        # print(f'Restrição {head}:')
        for i in range(N):
            if i == j:
                ct1.SetCoefficient(FU1[mi2ai(i, i, N)], 1)
                # print(f'{FU[mi2ai(j,i,N)]}+',end='')
            else:
                ct1.SetCoefficient(FU1[mi2ai(j, i, N)], 1)
                # print(f'{FU[mi2ai(j,i,N)]}+',end='')
                ct1.SetCoefficient(FU1[mi2ai(i, j, N)], 1)
                # if i == N-1:
                # print(f'{FU[mi2ai(i,j,N)]}')
                # else:
                # print(f'{FU[mi2ai(i,j,N)]}+',end='')
        head += 1

    ct1 = solver1.Constraint(N, N, str(head))
    # print(f'Restrição {head}')
    for i in range(N):
        for j in range(N):
            if i == j:
                ct1.SetCoefficient(FU1[mi2ai(i, j, N)], 1)
            else:
                ct1.SetCoefficient(FU1[mi2ai(i, j, N)], 2)

            # if i  == N-1 and j ==N-1:
                # print(f'{FU[mi2ai(i,j,N)]} == {N}')
            # else:
                # print(f'{FU[mi2ai(i,j,N)]}+',end='')

    # #Executaremos o solver
    objective1 = solver1.Objective()
    for j in range(N):
        for i in range(N):
            objective1.SetCoefficient(FU1[mi2ai(i, j, N)], Baseline[i, j])

            # ct.SetCoefficient(FU[mi2ai(j,i,N)], 1)
    objective1.SetMaximization()

    solver1.Solve()

    print('Solution:')
    print('Valor objetivo BaseLine =', (objective1.Value()))
    print('Valor objetivo AHNOMA =', (objective.Value()))
    pair = 0
    matriz = np.zeros(shape=(N, N))
    conta = 0
    Fmatriz = np.zeros(shape=(N, N))
    Omatriz = np.zeros(shape=(N, N))
    for i in range(0, N):
        for j in range(0, N):
            matriz[i, j] = (int(FU1[mi2ai(i, j, N)].solution_value()))
            conta += (int(FU1[mi2ai(i, j, N)].solution_value()))
            # print(int(FU1[mi2ai(i,j,N)].solution_value()))
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                matriz[i, j] = (int(FU1[mi2ai(i, j, N)].solution_value()))
                conta += (int(FU1[mi2ai(i, j, N)].solution_value()))
                # print(int(FU1[mi2ai(i,j,N)].solution_value()))
                if int(FU1[mi2ai(i, j, N)].solution_value()) == 1:
                    matriz[i, i] = 0
                    matriz[j, j] = 0

    usuario_atendido = list(DF1.columns)
    tot = 0
    ftot = 0
    outage = 0
    NomaP = 0
    FNomaP = 0
    print(f'Conta BASELINE = {conta}')
    for i in range(0, N):
        for j in range(0, N):

            if matriz[i, j] == 1:
                if i == j:
                    Omatriz[i, j] = 1
                    Fmatriz[i, j] = 1
                    # print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc[i,i]}')
                    # print(f'Used {(Aloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
                    usuario_atendido.remove(DF1.columns[j])
                    tot += Baseline[i, i]
                    ftot += Baseline[i, i]
                    # print(Aloc[i,j])
                    # ftot += FNOMA.iloc[i,j]
                else:
                    # print(f'NOMA Pair {pair} Near  User: {FU[j]}, data rate = {Aloc[j,j]}')
                    # print(f'NOMA Pair {pair} Far  User: {FU[i]}, data rate = {DF_NOMA.iloc[i,j]}')
                    NomaP += 1
                    # print(f'FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}')
                    # print(f'FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
                    # print(f'Gain over OMA:{(Aloc.iloc[i,j]/np.diag(Aloc)[j])*100}% ')
                    # print(Aloc[i,j])

                    tot += Baseline[i, j]
                    if DF3.iloc[i, j] >= Baseline[i, i] and DF4.iloc[j, j] >= Baseline[j, j]:
                        # print(f'alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}')
                        # print(f'alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
                        FNomaP += 1
                        ftot += DF4.iloc[i, j]
                        ftot += DF3.iloc[j, j]
                        # print(Aloc[i,j])
                        Fmatriz[i, j] = 1
                        # usuario_atendido.remove(DF_NOMA.columns[j])
                        # usuario_atendido.remove(DF_NOMA.index[i])

                    else:
                        # print(f'Não alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc[j,j]}')
                        # print(f'Não alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc[i,i]}')
                        outage += 1
                        Fmatriz[i, i] = 1
                        Fmatriz[j, j] = 1
                        Fmatriz[i, j] = 0
                        # print(Aloc[i,j])
                        # print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc[i,i]}')
                        # print(f'Used {(Aloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
                        # usuario_atendido.remove(DF_NOMA.columns[j])
                        tot += Baseline[j, i]
                        ftot += Baseline[i, i]
                        ftot += Baseline[j, j]
                        pass
                    pair = pair + 1
            else:
                Omatriz[i, i] = 1
    # print(matriz)
    # print(matriz1)
    # print(Omatriz)
    # print(Fmatriz)

    print(f'Fixed PA NOMA SumRate = {ftot}')
    # print('BL Total SumRate =', np.sum(np.multiply(Baseline,matriz)))
    # print(f'OMA Total SumRate = {np.sum(np.sum(np.diag(Baseline)))}')
    # print('AHNOMA SumRate2 =', np.sum(np.multiply(IM,matriz)))
    # print(f'Base Line = {sum(Channel_Capacity)}')

    solver2 = pywraplp.Solver.CreateSolver('SCIP')
    FU2 = list()
    for i in range(0, N):
        for j in range(0, N):
            FU2.append(solver2.IntVar(0, 1, f'FU_{i}_{j}'))
    # print ('Numero de variaveis =', solver1.NumVariables())

    head = 1

    for j in range(N):
        ct2 = solver2.Constraint(1, 1, str(head))
        # print(f'Restrição {head}:')
        for i in range(N):
            if i == j:
                ct2.SetCoefficient(FU2[mi2ai(i, i, N)], 1)
                # print(f'{FU[mi2ai(j,i,N)]}+',end='')
            else:
                ct2.SetCoefficient(FU2[mi2ai(j, i, N)], 1)
                # print(f'{FU[mi2ai(j,i,N)]}+',end='')
                ct2.SetCoefficient(FU2[mi2ai(i, j, N)], 1)
                # if i == N-1:
                # print(f'{FU[mi2ai(i,j,N)]}')
                # else:
                # print(f'{FU[mi2ai(i,j,N)]}+',end='')
        head += 1

    ct2 = solver2.Constraint(N, N, str(head))
    # print(f'Restrição {head}')
    for i in range(N):
        for j in range(N):
            if i == j:
                ct2.SetCoefficient(FU2[mi2ai(i, j, N)], 1)
            else:
                ct2.SetCoefficient(FU2[mi2ai(i, j, N)], 2)

            # if i  == N-1 and j ==N-1:
                # print(f'{FU[mi2ai(i,j,N)]} == {N}')
            # else:
                # print(f'{FU[mi2ai(i,j,N)]}+',end='')
        # #Executaremos o solver
    objective2 = solver2.Objective()
    for j in range(N):
        for i in range(N):
            
            if i == j:
                objective2.SetCoefficient(FU2[mi2ai(i, j, N)], (np.power(
                    DF3.iloc[i, j], 2)/np.power(DF4.iloc[i, j], 2)))
            else:
                objective2.SetCoefficient(FU2[mi2ai(i, j, N)], (np.power(
                    DF3.iloc[i, j]+DF4.iloc[j, j], 2)/2*(np.power(DF3.iloc[i, j], 2)+np.power(DF4.iloc[j, j], 2))))

    objective2.SetMaximization()
        


    solver2.Solve()

    print('Solution:')
    print('Valor objetivo BaseLine =', (objective1.Value()))
    print('Valor objetivo AHNOMA =', (objective.Value()))
    #pair = 0
    #matriz = np.zeros(shape=(N, N))
    #conta = 0
    #Fmatriz = np.zeros(shape=(N, N))
    #Omatriz = np.zeros(shape=(N, N))
    Fairnessmatriz= np.zeros(shape=(N, N))
    for i in range(0, N):
        for j in range(0, N):
            Fairnessmatriz[i, j] = (int(FU2[mi2ai(i, j, N)].solution_value()))
            conta += (int(FU2[mi2ai(i, j, N)].solution_value()))
            # print(int(FU1[mi2ai(i,j,N)].solution_value()))
    for i in range(0, N):
        for j in range(0, N):
            if i != j:
                Fairnessmatriz[i, j] = (int(FU2[mi2ai(i, j, N)].solution_value()))
                conta += (int(FU2[mi2ai(i, j, N)].solution_value()))
                # print(int(FU1[mi2ai(i,j,N)].solution_value()))
                if int(FU2[mi2ai(i, j, N)].solution_value()) == 1:
                    Fairnessmatriz[i, i] = 0
                    Fairnessmatriz[j, j] = 0

    #usuario_atendido = list(DF1.columns)
    #tot = 0
    fairnesstot = 0
    #outage = 0
    #NomaP = 0
    FairnessNomaP = 0
    print(f'Conta BASELINE = {conta}')
    for i in range(0, N):
        for j in range(0, N):

            if Fairnessmatriz[i, j] == 1:
                if i == j:
                    #Omatriz[i, j] = 1
                    #Fmatriz[i, j] = 1
                    # print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc[i,i]}')
                    # print(f'Used {(Aloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
                    #usuario_atendido.remove(DF1.columns[j])
                    #tot += IM[i, i]
                    fairnesstot += DF3.iloc[i, j]
                    # print(Aloc[i,j])
                    # ftot += FNOMA.iloc[i,j]
                else:
                    # print(f'NOMA Pair {pair} Near  User: {FU[j]}, data rate = {Aloc[j,j]}')
                    # print(f'NOMA Pair {pair} Far  User: {FU[i]}, data rate = {DF_NOMA.iloc[i,j]}')
                    #NomaP += 1
                    # print(f'FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}')
                    # print(f'FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
                    # print(f'Gain over OMA:{(Aloc.iloc[i,j]/np.diag(Aloc)[j])*100}% ')
                    # print(Aloc[i,j])

                    #tot += IM[i, j]
                    if DF3.iloc[i, j] >= DF_NOMA[i, i] and DF4.iloc[j, j] >= DF_NOMA[j, j]:
                        # print(f'alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}')
                        # print(f'alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
                        FairnessNomaP += 1
                        fairnesstot += DF4.iloc[j, j]
                        fairnesstot += DF3.iloc[i, j]
                        # print(Aloc[i,j])
                        Fairnessmatriz[i, j] = 1
                        # usuario_atendido.remove(DF_NOMA.columns[j])
                        # usuario_atendido.remove(DF_NOMA.index[i])

                    else:
                        # print(f'Não alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc[j,j]}')
                        # print(f'Não alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc[i,i]}')
                        outage += 1
                        Fairnessmatriz[i, i] = 1
                        Fairnessmatriz[j, j] = 1
                        Fairnessmatriz[i, j] = 0
                        # print(Aloc[i,j])
                        # print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc[i,i]}')
                        # print(f'Used {(Aloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
                        # usuario_atendido.remove(DF_NOMA.columns[j])
                        #tot += DF_NOMA[j, i]
                        fairnesstot += DF4.iloc[j, j]
                        fairnesstot += DF3.iloc[i, i]
                        pass
                    #pair = pair + 1
            else:
                #Omatriz[i, i] = 1
                pass

    # print(matriz)
    # print(matriz1)
    # print(Omatriz)
    print(Fairnessmatriz)

    #print(f'Fixed PA NOMA SumRate = {ftot}')                    
    return {'FairnessNOMA_PAIRS': FairnessNomaP,'FairnessAHNOMA': np.sum(np.multiply(Fairnessmatriz, (IM))),'FairnessNOMA_Matrix': Fairnessmatriz,'FNOMA_Matrix': Fmatriz, 'Baseline_Matriz': matriz, 'matriz': matriz1, 'OMA': np.sum(np.sum(np.diag(Baseline))), 'Baseline_NOMA': np.sum(np.multiply(matriz, (Baseline))), 'AHNOMA': np.sum(np.multiply(matriz1, (IM))), 'FixNOMA': ftot, 'NOMA_PAIRS': calculo(matriz1), 'FNOMA_PAIRS': calculo(Fmatriz), 'OUTAGE': outage, 'Max_Capacity': sum(Channel_Capacity), 'Baseline_Pairs': calculo(matriz), 'Baseline': Baseline, 'IM': IM}
