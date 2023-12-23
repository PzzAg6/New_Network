import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import copy
import numpy as np
import time
import pickle
import os

def Create_Network(NODE_NUM):

    Set_2simplx = dict.fromkeys([p for p in range(NODE_NUM)])
    for node in Set_2simplx.keys():
        Set_2simplx[node] = []

    G = nx.Graph()
    node_list = [p for p in range(NODE_NUM)]
    G.add_nodes_from(node_list)
    nx.set_node_attributes(G, False, "INFECTED")#设置节点属性
    nx.set_node_attributes(G, None, "INFECTED_TIME")#设置节点属性

    #1-simplex
    for i in range(NODE_NUM):
        for j in range(i + 1, NODE_NUM):
            t_random = random.random()
            if t_random <= p:
                print("add_edge {}-{}".format(i,j))
                G.add_edge(i,j)
    #2-simplex
    for i in range(NODE_NUM):
        for j in range (i + 1, NODE_NUM):
            for k in range(j + 1, NODE_NUM):
                p2_cmp = random.random()
                if(p2_cmp <= p2):
                    add_edge = [(i,j), (j,k), (i,k)]
                    #set
                    #虽然不够优雅
                    Set_2simplx[i].append([j,k])
                    Set_2simplx[j].append([i,k])
                    Set_2simplx[k].append([i,j])
                    print("{}-{}-{}".format(i,j,k))
                    G.add_edges_from(add_edge)
    return G, Set_2simplx

def Network_Save(Root_Name, Doc_Name, NODE_NUM, N_LAYERS, MULTI_G, twondsimplex_Dict):
    New_Root = Root_Name + '/' + str(NODE_NUM) + Doc_Name

    smp_inf = "2smp"
    try:
        os.mkdir(New_Root)
    except FileExistsError:
        pass

    network = 0
    for Network in MULTI_G:
        read_nt = open(New_Root + '/' + '{}.nt'.format(network), 'wb')
        network += 1
        nx.write_edgelist(Network, read_nt, delimiter = ',')
        read_nt.close
    
    L = 0
    for smp_dict in twondsimplex_Dict:
        twodict_write = open(New_Root + '/' + 'L{}_{}.pkl'.format(L, Doc_Name + '_' + smp_inf), 'wb')
        L += 1
        pickle.dump(smp_dict, twodict_write)
        twodict_write.close()
        
    read = open(New_Root + '/' + 'detail.txt', 'w')
    read.write("#NODES #LAYERS" + '\n')
    read.write("{0:^5d} {1:^5d}".format(NODE_NUM, N_LAYERS) + '\n')
    read.close()

    read = open(New_Root + '/' + 'detail_k.txt', 'w')
    read.write("#K1 #K2" + '\n')
    read.write("{0:^5d} {1:^5d}".format(k1, k2) + '\n')
    read.close()

def Generated_Connected_NX(NODE_NUM):
    Generate_connected = False
    while(not Generate_connected):
        NT, NT_2Simp = Create_Network(NODE_NUM)
        if(nx.is_connected(NT)):
            Generate_connected = True
    return NT, NT_2Simp

if __name__ == '__main__':
	NODE_NUM = 1000
	N_LAYERS = 2
	k1 = 20
	k2 = 4
	p2 = 2*k2/((NODE_NUM - 1)*(NODE_NUM - 2))
	p = (k1 - 2*k2)/(NODE_NUM - 1 - 2*k2)
	PP = [p, p2]
	GROUP_NAME = "Thousand_2_12_21"#自行命名

	NT_1, NT_1_2Simp = Generated_Connected_NX(NODE_NUM)
	NT_2, NT_2_2Simp = Generated_Connected_NX(NODE_NUM)
	MULTI_NT = [NT_1, NT_2]
	MULTI_NT_2Simp = [NT_1_2Simp, NT_2_2Simp]

	ROOT_NAME = os.getcwd()
	Network_Save(ROOT_NAME, GROUP_NAME, NODE_NUM, N_LAYERS, MULTI_NT, MULTI_NT_2Simp)

