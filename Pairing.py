from __future__ import print_function
import pandas as pd
import numpy as np
import math
#Vamos importar o solver linear do ORTOOLS

from ortools.linear_solver import pywraplp
#Vamos importar o numpy como uma ferramenta auxiliar 


solver = pywraplp.Solver.CreateSolver('GLOP')

def mi2ai(i,j,line_length):
	return i*line_length+j

def ai2mi(index, line_length):
	return [maph.floor(index/line_length), index%line_length]

def ajuste(tabela):
	tabela.index = tabela.columns
	asd = sorted(list(tabela.columns))
	tabela = tabela.reindex(asd,axis=1)
	tabela = tabela.reindex(asd,axis=0)
	return tabela	



def TA(DF0,DF1,DF2,DF3,DF4):
	DF0 = ajuste(DF0)
	DF1 = ajuste(DF1)
	DF2 = ajuste(DF2)
	DF3 = ajuste(DF3)
	DF4 = ajuste(DF4)
	Aloc = DF2
	NU = []
	FU = []
	N = len(Aloc.columns)
	# Matriz de interesses
	sub_util = {}
	sumrate = {}
	i=0
	for c in Aloc.columns:
		#print(DF2[c][i])
		#print(np.diag(DF_OMA)[i])
		if DF2[c][i] < np.diag(DF1)[i]:
			sub_util[c] = Aloc[c]/np.diag(DF1)[i]
			sumrate[c] = DF0[c]
		else:
			#print(f'{c}alo')
			sub_util[c] = 0
			sumrate[c] = 0
		#desp[c] = DF[c]/np.diag(DF2)[i]
		i=i+1

	

	sub_util = pd.DataFrame(sub_util)
	sumrate = pd.DataFrame(sumrate) 


	Aloc = sumrate
	for i in range(N):
		for j in range(N):
			
			if sumrate.iloc[i][j] > 0.0:
				Aloc.iloc[i,j] = DF2.iloc[i][j]
			
			if sumrate.iloc[i][i] == 0:
				Aloc.iloc[i,j] = DF1.iloc[i,j]
	#A = Aloc1.values
	# i*j variaveis serao necessarias
	'''
	for j in range(0,N):
			NU.append(solver.NumVar(0, 1, f'NU_{j}'))
	print ('Numero de variaveis =', solver.NumVariables())
	'''
	for i in range(0,N):
		for j in range(0,N):
			FU.append(solver.NumVar(0, 1,f'FU_{i}_{j}'))
	#print ('Numero de variaveis =', solver.NumVariables())


	head = 1


	for j in range(N):
		R = '0 <= '
		ct = solver.Constraint(1,2, str(head))

		for i in range(N):
			if i == j:
				ct.SetCoefficient(FU[mi2ai(j,j,N)], 1)
				R += f'{FU[mi2ai(j,j,N)]} + '
			else:    
				ct.SetCoefficient(FU[mi2ai(i,j,N)], 1)
				R += f'{FU[mi2ai(i,j,N)]} + '
				ct.SetCoefficient(FU[mi2ai(j,i,N)], 1)
				R += f'{FU[mi2ai(j,i,N)]} + '
		head+=1
		#print(R)    

	ct = solver.Constraint(N,N, str(head)) 
	for j in range(N):
		R = '0 <= '
		
		ct.SetCoefficient(FU[mi2ai(j,j,N)], 1)  

	
	for i in range(N):
		R = '0 <= '
		ct = solver.Constraint(0,2, str(head)) 
		for j in range(N):
			ct.SetCoefficient(FU[mi2ai(i,j,N)], 1)     
		head +=1
	solver.NumConstraints()

	objective = solver.Objective()
	for j in range(N):
		#objective.SetCoefficient(FU[mi2ai(i,i,N)], 1)
		for i in range(N):
			objective.SetCoefficient(FU[mi2ai(i,j,N)], float(Aloc.iloc[i,j]))
			#ct.SetCoefficient(FU[mi2ai(j,i,N)], 1)
	objective.SetMaximization()

	# #Executaremos o solver
	solver.Solve()


	#print('Solution:')
	#print('Valor objetivo =', (objective.Value()))
	pair = 0
	matriz = np.zeros(shape=(N,N))
	for i in range(0,N):
		for j in range(0,N):
			matriz[i,j] = (int(FU[mi2ai(i,j,N)].solution_value()))
	for i in range(0,N):
		for j in range(0,N):
			if i != j:
				matriz[i,j] = (int(FU[mi2ai(i,j,N)].solution_value()))
				if int(FU[mi2ai(i,j,N)].solution_value()) ==1:
						matriz[i,i] = 0
						matriz[j,j] = 0
	usuario_atendido = list(DF0.columns)
	#print(usuario_atendido)
	tot = 0
	ftot = 0
	outage = 0
	NomaP= 0
	FNomaP = 0
	for i in range(0,N):
		for j in range(0,N):
			if matriz[i,j] ==1:
				if i == j:
					#print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc.iloc[i,i]}')
					#print(f'Used {(Aloc.iloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
					usuario_atendido.remove(DF0.columns[j])
					tot +=Aloc.iloc[i,j]
					ftot += Aloc.iloc[i,i]
					#ftot += FNOMA.iloc[i,j]
				else:
					#print(f'NOMA Pair {pair} Near  User: {FU[j]}, data rate = {Aloc.iloc[j,j]}') 
					#print(f'NOMA Pair {pair} Far  User: {FU[i]}, data rate = {DF_NOMA.iloc[i,j]}')
					NomaP +=1
					#print(f'FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}') 
					#print(f'FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
					#print(f'Gain over OMA:{(Aloc.iloc[i,j]/np.diag(Aloc)[j])*100}% ') 
					tot +=Aloc.iloc[j,j]
					if DF3.iloc[i,j] >= Aloc.iloc[i,i] and DF4.iloc[j,j] >= Aloc.iloc[j,j]:
						#print(f'alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}') 
						#print(f'alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}')
						FNomaP +=1
						ftot += DF4.iloc[i,j]
						ftot += DF3.iloc[j,j]
						usuario_atendido.remove(DF0.columns[j])
						usuario_atendido.remove(DF0.index[i])
						
					else:
						#print(f'Não alocado:FIXED NOMA Pair {pair} Near  User: {FU[j]}, data rate = {NUFNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc.iloc[j,j]}') 
						#print(f'Não alocado:FIXED NOMA Pair {pair} Far  User: {FU[i]}, data rate = {FNOMA.iloc[i,j]}, Alocado Ortogonal: {Aloc.iloc[i,i]}')
						outage +=1
						#print(f'OMA User: {DF_NOMA.columns[j]}, data rate = {Aloc.iloc[i,i]}')
						#print(f'Used {(Aloc.iloc[i,j]/np.diag(Aloc)[i])*100}% from Shannon Channel Capacity')
						#usuario_atendido.remove(DF_NOMA.columns[j])
						tot +=Aloc.iloc[i,j]
						ftot += Aloc.iloc[i,i]
						ftot += Aloc.iloc[j,j]
						pass
					pair = pair +1
			else:
				pass
	#print(matriz)
	#print(f'Fixed PA NOMA SumRate = {ftot}')
	#print('Total SumRate =', np.sum(np.sum(Aloc*matriz)))
	#print(f'OMA Total SumRate = {np.sum(np.sum(np.diag(Aloc)))}')
	
	return {'Aloc':Aloc,'matriz':matriz,'OMA':np.sum(np.sum(np.diag(Aloc))),'NOMA':np.sum(np.sum(Aloc*matriz)),'FixNOMA':ftot,'NOMA_PAIRS':NomaP,'FNOMA_PAIRS':FNomaP,'OUTAGE':outage}
