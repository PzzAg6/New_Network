import time
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import copy
import numpy as np
import time
import pickle
import os
import sys
import csv
import math

def copy_networkdata(path):
    read = open(path, "rb")
    network = nx.read_edgelist(read, delimiter = ',', nodetype = int)
    nx.set_node_attributes(network, False, "INFECTED")#设置节点属性
    nx.set_node_attributes(network, None, "INFECTED_TIME")#设置节点属性
    read.close()
    return network
def copy_2smpxdata(path):
    read = open(path, 'rb')
    twosmpx = pickle.load(read)
    read.close()
    return twosmpx
def network_reset(network):
    nx.set_node_attributes(network, False, "INFECTED")#设置节点属性
    nx.set_node_attributes(network, None, "INFECTED_TIME")#设置节点属性

def SPREAD(MULTI_NT, Seed_Nodes, Beta, MAX_UNCHANGE_TIME):
    #UNCHANGE_MAX  is a number
    TIME = 0
    Is_End = False
    MAX_UNCHANGE_TIME_LAYER = [MAX_UNCHANGE_TIME, MAX_UNCHANGE_TIME]
    UNCHANGE_TIME_LAYER = [0, 0]

    INFECTED_LIST = list()
    
    Cur_TESTED_UNINFECTED_NODE = [set() for i in range(N_LAYERS)]
    Cur_INFECTED_LIST = set()
    Forget_List = []

    TIME_LAYER_LIST = []
    LAYER_DICT = {}.fromkeys([i for i in range(N_LAYERS)])
    for i in range(N_LAYERS):
        LAYER_DICT[i] = list()

    TIME_LAYER_LIST.append(copy.deepcopy(LAYER_DICT))#这个可以暂时不需要，因为不需要这么多次
    
    for network in MULTI_NT:
        nx.set_node_attributes(network, False, "INFECTED")#设置节点属性
        nx.set_node_attributes(network, None, "INFECTED_TIME")#设置节点属性

    for Layer_, infected_Node_Set in Seed_Nodes.items():
        for Node in infected_Node_Set:
            MULTI_NT[Layer_].nodes[Node]["INFECTED"] = True
            MULTI_NT[Layer_].nodes[Node]["INFECTED_TIME"] = TIME
            INFECTED_LIST.append((Layer_, Node))
            TIME_LAYER_LIST[TIME][Layer_].append(Node)
    while(len(INFECTED_LIST) != 0 and \
          not (UNCHANGE_TIME_LAYER[0] > MAX_UNCHANGE_TIME_LAYER[0] and UNCHANGE_TIME_LAYER[1] > MAX_UNCHANGE_TIME_LAYER[1])):
        # print(UNCHANGE_TIME_LAYER[0])
        # print(UNCHANGE_TIME_LAYER[1])
        Layer, init = INFECTED_LIST.pop(0)
        if TIME == MULTI_NT[Layer].nodes[init]['INFECTED_TIME']:
            #statics for unchange:
            #注意长度为零的情况，如果退化了咋整
            Test_Change_Rate_L0 = abs((len(TIME_LAYER_LIST[TIME][0]) - len(TIME_LAYER_LIST[TIME - 1][0])))/len(TIME_LAYER_LIST[TIME - 1][0])
            Test_Change_Rate_L1 = abs((len(TIME_LAYER_LIST[TIME][1]) - len(TIME_LAYER_LIST[TIME - 1][1])))/len(TIME_LAYER_LIST[TIME - 1][1])
            if(Test_Change_Rate_L0 <= Unchange_Ratio and TIME >= 1):
                UNCHANGE_TIME_LAYER[0] += 1
            else:
                UNCHANGE_TIME_LAYER[0] = 0

            if(Test_Change_Rate_L1 <= Unchange_Ratio and TIME >= 1):
                UNCHANGE_TIME_LAYER[1] += 1
            else:
                UNCHANGE_TIME_LAYER[1] = 0

                
            for Layer_, Node in Forget_List:
                MULTI_NT[Layer_].nodes[Node]["INFECTED"] = False
                MULTI_NT[Layer_].nodes[Node]["INFECTED_TIME"] = None
            Cur_TESTED_UNINFECTED_NODE = [set() for i in range(N_LAYERS)]
            Cur_INFECTED_LIST = set()
            Forget_List = []
            print("-" * 20)
            print("TIME = {}.".format(TIME))
            print("-" * 20)
            TIME += 1
            TIME_LAYER_LIST.append(copy.deepcopy(LAYER_DICT))

        print("Starting node {0} in layer#{1}".format(init, Layer))
        uninfected_nbr_init = [(Layer, node) for node in nx.neighbors(MULTI_NT[Layer], init)\
            if (MULTI_NT[Layer].nodes[node]["INFECTED"] == False and (init not in Cur_TESTED_UNINFECTED_NODE[Layer]))]

        #这个是不是不用考虑了    
        # if(MULTI_NT[1 - Layer].nodes[init]["INFECTED"] == False and (init not in Cur_TESTED_UNINFECTED_NODE[1 - Layer])):
        #     layer_nbr_init = [(1 - Layer, init)]
        # else:
        #     layer_nbr_init = []

        # uninfected_nbr_init += layer_nbr_init


        if len(uninfected_nbr_init) == 0:
    #         continue#不应该用continue啊..
            pass
        else:
            for un_node in uninfected_nbr_init:
                #layer, node = un_node
                print("    Started test Node {} at Layer {}.".format(un_node[1], un_node[0]))
                Cur_TESTED_UNINFECTED_NODE[un_node[0]].update([un_node[1]])
                Is_Infected = False

                #查看另一层的状态，决定参数 
                try:   
                    if MULTI_NT[1 - un_node[0]].nodes[un_node[1]]["INFECTED"] == True:
                        #infected
                        print("        intra-layer beta")
                        Beta_Edge = Beta[un_node[0]]['edge']['A']
                        Beta_2splx = Beta[un_node[0]]['2simplx']['A']
                    else:
                        #uninfected
                        print("        inter-layer beta")
                        Beta_Edge = Beta[un_node[0]]['edge']['U']
                        Beta_2splx = Beta[un_node[0]]['2simplx']['U']
                except:
                    ##有可能另一层是一个single node
                    print("        inter-layer beta")
                    Beta_Edge = Beta[un_node[0]]['edge']['U']
                    Beta_2splx = Beta[un_node[0]]['2simplx']['U']
                
                INFECTED_Prb = 1

                #edges    
                inf_nbr_node = [(un_node[0], node) for node in nx.neighbors(MULTI_NT[un_node[0]], un_node[1]) \
                    if (MULTI_NT[un_node[0]].nodes[node]["INFECTED"] == True)]
                unnode_set = set([node[1] for node in inf_nbr_node])
                #2simplex
                # print(un_node[0])
                for node_2splx in MULTI_NT_2Simp[un_node[0]][un_node[1]]:
                    # print(node_2splx)
                    node_1, node_2 = node_2splx
                    # node_1, node_2 = node_2splx#注意这里不止对应有一个2simplex
                    if (node_1 in unnode_set) and (node_2 in unnode_set):
                        print("        2-simplex account. {} and {} to {} at Layer {}.".format(node_1, node_2, un_node[1], un_node[0]))
                        INFECTED_Prb *= (1 - Beta_2splx)


                for layer_, inf_node in inf_nbr_node:
                    #edges
                    INFECTED_Prb *= (1 - Beta_Edge)

                INFECTED_Prb = 1 - INFECTED_Prb

                if INFECTED_Prb > random.random():
                    Is_Infected = True
                if Is_Infected:
                    print("Node {} infected at Layer {}.".format(un_node[1], un_node[0]))
                    Cur_INFECTED_LIST.update([un_node])
                    TIME_LAYER_LIST[TIME][un_node[0]].append(un_node[1])
                    MULTI_NT[un_node[0]].nodes[un_node[1]]["INFECTED"] = Is_Infected
                    MULTI_NT[un_node[0]].nodes[un_node[1]]["INFECTED_TIME"] = TIME
                    INFECTED_LIST.append((un_node))
                else:
                    continue
                #别忘了考虑遗忘
        if Forget_Rate[Layer] <= random.random():
            #not forget
            print("Node {} staying active at Layer {}.".format(init, Layer))
            Cur_INFECTED_LIST.update([init])
            TIME_LAYER_LIST[TIME][Layer].append(init)
            MULTI_NT[Layer].nodes[init]["INFECTED"] = True
            MULTI_NT[Layer].nodes[init]["INFECTED_TIME"] = TIME
            INFECTED_LIST.append((Layer, init))
        else:
            #forget
            #应该在TIME + 1时刻再考虑传播的问题,就是传播完这轮
            print("Node {} was forgotten".format(init))
            Forget_List.append((Layer,init))
    #         MULTI_NT[Layer].nodes[init]["INFECTED"] = False
    #         MULTI_NT[Layer].nodes[init]["INFECTED_TIME"] = None            
        
        
        
    return TIME_LAYER_LIST, TIME


#限定传播时长
def SPREAD_TIME_STOP(MULTI_NT, Seed_Nodes, Beta, MAX_UNCHANGE_TIME):
    #UNCHANGE_MAX  is a number
    TIME = 0
    Is_End = False
    MAX_UNCHANGE_TIME_LAYER = [MAX_UNCHANGE_TIME, MAX_UNCHANGE_TIME]
    UNCHANGE_TIME_LAYER = [0, 0]

    INFECTED_LIST = list()
    
    Cur_TESTED_UNINFECTED_NODE = [set() for i in range(N_LAYERS)]
    Cur_INFECTED_LIST = set()
    Forget_List = []

    TIME_LAYER_LIST = []
    LAYER_DICT = {}.fromkeys([i for i in range(N_LAYERS)])
    for i in range(N_LAYERS):
        LAYER_DICT[i] = list()

    TIME_LAYER_LIST.append(copy.deepcopy(LAYER_DICT))#这个可以暂时不需要，因为不需要这么多次
    
    for network in MULTI_NT:
        nx.set_node_attributes(network, False, "INFECTED")#设置节点属性
        nx.set_node_attributes(network, None, "INFECTED_TIME")#设置节点属性

    for Layer_, infected_Node_Set in Seed_Nodes.items():
        for Node in infected_Node_Set:
            MULTI_NT[Layer_].nodes[Node]["INFECTED"] = True
            MULTI_NT[Layer_].nodes[Node]["INFECTED_TIME"] = TIME
            INFECTED_LIST.append((Layer_, Node))
            TIME_LAYER_LIST[TIME][Layer_].append(Node)
    while(len(INFECTED_LIST) != 0 and \
          TIME <= 1000):
        Layer, init = INFECTED_LIST.pop(0)
        if TIME == MULTI_NT[Layer].nodes[init]['INFECTED_TIME']:
            #statics for unchange:
            if(abs((len(TIME_LAYER_LIST[TIME][Layer]) - len(TIME_LAYER_LIST[TIME - 1][Layer])))/len(TIME_LAYER_LIST[TIME - 1][Layer]) <= 0.1\
              and TIME >= 1):
                UNCHANGE_TIME_LAYER[Layer] += 1
            else:
                UNCHANGE_TIME_LAYER[Layer] = 0
                
            for Layer_, Node in Forget_List:
                MULTI_NT[Layer_].nodes[Node]["INFECTED"] = False
                MULTI_NT[Layer_].nodes[Node]["INFECTED_TIME"] = None
            Cur_TESTED_UNINFECTED_NODE = [set() for i in range(N_LAYERS)]
            Cur_INFECTED_LIST = set()
            Forget_List = []
            print("-" * 20)
            print("TIME = {}.".format(TIME))
            print("-" * 20)
            TIME += 1
            TIME_LAYER_LIST.append(copy.deepcopy(LAYER_DICT))

        print("Starting node {0} in layer#{1}".format(init, Layer))
        uninfected_nbr_init = [(Layer, node) for node in nx.neighbors(MULTI_NT[Layer], init)\
            if (MULTI_NT[Layer].nodes[node]["INFECTED"] == False and (init not in Cur_TESTED_UNINFECTED_NODE[Layer]))]

        #这个是不是不用考虑了    
        # if(MULTI_NT[1 - Layer].nodes[init]["INFECTED"] == False and (init not in Cur_TESTED_UNINFECTED_NODE[1 - Layer])):
        #     layer_nbr_init = [(1 - Layer, init)]
        # else:
        #     layer_nbr_init = []

        # uninfected_nbr_init += layer_nbr_init


        if len(uninfected_nbr_init) == 0:
    #         continue#不应该用continue啊..
            pass
        else:
            for un_node in uninfected_nbr_init:
                #layer, node = un_node
                print("    Started test Node {} at Layer {}.".format(un_node[1], un_node[0]))
                Cur_TESTED_UNINFECTED_NODE[un_node[0]].update([un_node[1]])
                Is_Infected = False

                #查看另一层的状态，决定参数
                try:    
                    if MULTI_NT[1 - un_node[0]].nodes[un_node[1]]["INFECTED"] == True:
                        #infected
                        print("        intra-layer beta")
                        Beta_Edge = Beta[un_node[0]]['edge']['A']
                        Beta_2splx = Beta[un_node[0]]['2simplx']['A']
                    else:
                        #uninfected
                        print("        inter-layer beta")
                        Beta_Edge = Beta[un_node[0]]['edge']['U']
                        Beta_2splx = Beta[un_node[0]]['2simplx']['U']
                except:
                    ##有可能另一层是一个single node
                    print("        inter-layer beta")
                    Beta_Edge = Beta[un_node[0]]['edge']['U']
                    Beta_2splx = Beta[un_node[0]]['2simplx']['U']

                INFECTED_Prb = 1

                #edges    
                inf_nbr_node = [(un_node[0], node) for node in nx.neighbors(MULTI_NT[un_node[0]], un_node[1]) \
                    if (MULTI_NT[un_node[0]].nodes[node]["INFECTED"] == True)]
                unnode_set = set([node[1] for node in inf_nbr_node])
                #2simplex
                # print(un_node[0])
                for node_2splx in MULTI_NT_2Simp[un_node[0]][un_node[1]]:
                    # print(node_2splx)
                    node_1, node_2 = node_2splx
                    # node_1, node_2 = node_2splx#注意这里不止对应有一个2simplex
                    if (node_1 in unnode_set) and (node_2 in unnode_set):
                        print("        2-simplex account. {} and {} to {} at Layer {}.".format(node_1, node_2, un_node[1], un_node[0]))
                        INFECTED_Prb *= (1 - Beta_2splx)


                for layer_, inf_node in inf_nbr_node:
                    #edges
                    INFECTED_Prb *= (1 - Beta_Edge)

                INFECTED_Prb = 1 - INFECTED_Prb

                if INFECTED_Prb > random.random():
                    Is_Infected = True
                if Is_Infected:
                    print("Node {} infected at Layer {}.".format(un_node[1], un_node[0]))
                    Cur_INFECTED_LIST.update([un_node])
                    TIME_LAYER_LIST[TIME][un_node[0]].append(un_node[1])
                    MULTI_NT[un_node[0]].nodes[un_node[1]]["INFECTED"] = Is_Infected
                    MULTI_NT[un_node[0]].nodes[un_node[1]]["INFECTED_TIME"] = TIME
                    INFECTED_LIST.append((un_node))
                else:
                    continue
                #别忘了考虑遗忘
        if Forget_Rate[Layer] <= random.random():
            #not forget
            print("Node {} staying active at Layer {}.".format(init, Layer))
            Cur_INFECTED_LIST.update([init])
            TIME_LAYER_LIST[TIME][Layer].append(init)
            MULTI_NT[Layer].nodes[init]["INFECTED"] = True
            MULTI_NT[Layer].nodes[init]["INFECTED_TIME"] = TIME
            INFECTED_LIST.append((Layer, init))
        else:
            #forget
            #应该在TIME + 1时刻再考虑传播的问题,就是传播完这轮
            print("Node {} was forgotten".format(init))
            Forget_List.append((Layer,init))
    #         MULTI_NT[Layer].nodes[init]["INFECTED"] = False
    #         MULTI_NT[Layer].nodes[init]["INFECTED_TIME"] = None            
        
        
        
    return TIME_LAYER_LIST, TIME

def Output_TIME_LAYER_LIST(Time_Layer_List, TIME_Interval, path_name, N_NODES):
    #输出个数
    NUM_LAYER_TIME = {0:[], 1:[]}
    for t in range(TIME_Interval):
        for layer in range(2):
            NUM_LAYER_TIME[layer].append(len(Time_Layer_List[t][layer])/N_NODES)
    for l in range(2):
        print("第{}层:".format(l))
        print(NUM_LAYER_TIME[l])
    headers = ["L1", "L2"]
    with open(path_name + ".csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(zip(NUM_LAYER_TIME[0], NUM_LAYER_TIME[1]))

def Output_Beta(path_name, Beta):

    headers = ["", "A", "U"]
    para_dict = {"A": 0, "U": 1, "edge": 0, "2simplx" : 1}
    #Beta_0 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}
    # smpl_row = {'A':[None, None], 'U':[None, None]}

    with open(path_name + '.csv', "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for layer, beta_layer in Beta.items():
            writer.writerow(["L" + str(layer), '', ''])
            smpl_row = {'A':[None, None], 'U':[None, None]}
            for simplex, A_U_Beta in beta_layer.items():
                for A_U, beta_au in A_U_Beta.items():
                    #A_U:"A" or "U"
                    smpl_row[A_U][para_dict[simplex]] = beta_au
            writer.writerow(["edge", \
                smpl_row['A'][para_dict["edge"]], \
                smpl_row['U'][para_dict["edge"]]])
            writer.writerow(["2simplx", \
                smpl_row['A'][para_dict["2simplx"]], \
                smpl_row['U'][para_dict["2simplx"]]])            
                    


def Experiment_1_1(Path, MULTI_NT, Beta, Para_BETA_X, Beta_Step):
    #一个文件夹存放？
    #Path是节点根目录
    Cur_Time = time.strftime("_%m_%d_%H_%M_%S", time.localtime())#提前固定时间，都在同一个文件内表示
    Tag = "EP_1_Beta_X"#后面跟个时间
    Path = Path + '/' + Tag + Cur_Time#不含/
    try:
        os.mkdir(Path)
    except FileExistsError:
        pass
    Random_Gen_Seed = random.sample(range(0, N_NODES), int(N_NODES * Random_Gen_Ratio))
    inf_index_L1 = Random_Gen_Seed
    inf_index_L2 = Random_Gen_Seed
    Seed_Nodes = {Infected_Layer_L1: inf_index_L1, Infected_Layer_L2: inf_index_L2}   
    #此时输出一个原本的beta
    Output_Beta(Path + '/' + 'Beta', Beta)
    for Para_Beta in Para_BETA_X:
        Loop_Para = dict(zip(Para_Dict, Para_Beta))
        Origin_Beta_Val = Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']]
        while(Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']] < 0.9999):
            
            TIME_LAYER_LIST, TIME_L = SPREAD(MULTI_NT, Seed_Nodes, Beta, MAX_UNCHANGE_TIME)
            Output_TIME_LAYER_LIST(TIME_LAYER_LIST, TIME_L, Path + '/' + '{}_{}_{}_{}'.format(Loop_Para['layer'], \
                Loop_Para['simplex'], \
                Loop_Para['state'], \
                Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']]), N_NODES)
            # Output_Beta(NETWORK_PATH + '/' + 'Beta', Beta)
            Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']] += Beta_Step

            #写入TIME_LAYER_LIST
        #reset
        Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']] = Origin_Beta_Val

def Experiment_1_2(Path, MULTI_NT, Beta, Para_BETA_Y, Beta_Step):
    #参照1_1修改
    #一个文件夹存放？
    Cur_Time = time.strftime("_%Y_%m_%d_%H_%M_%S", time.localtime())#提前固定时间，都在同一个文件内表示
    Tag = "EP_1_Beta_X"
    Path = Path + '/' + Tag + Cur_Time#不含/
    try:
        os.mkdir(Path)
    except FileExistsError:
        pass
    Random_Gen_Seed = random.sample(range(0, N_NODES), int(N_NODES * Random_Gen_Ratio))
    inf_index_L1 = Random_Gen_Seed
    inf_index_L2 = Random_Gen_Seed
    Seed_Nodes = {Infected_Layer_L1: inf_index_L1, Infected_Layer_L2: inf_index_L2}
    #此时输出一个原本的beta
    Output_Beta(Path + '/' + 'Beta', Beta)
    for Para_Beta in Para_BETA_Y:
        Loop_Para = dict(zip(Para_Dict, Para_Beta))
        Origin_Beta_Val = Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']]
        while(Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']] < 0.9999):

            TIME_LAYER_LIST, TIME_L = SPREAD(MULTI_NT, Seed_Nodes, Beta, MAX_UNCHANGE_TIME)
            Output_TIME_LAYER_LIST(TIME_LAYER_LIST, TIME_L, Path + '/' + '{}_{}_{}_{}'.format(Loop_Para['layer'], \
                Loop_Para['simplex'], \
                Loop_Para['state'], \
                Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']]), N_NODES)
            # Output_Beta(NETWORK_PATH + '/' + 'Beta', Beta)
            Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']] += Beta_Step
            
            #写入TIME_LAYER_LIST
            #表明beta
        #reset
        Beta[Loop_Para['layer']][Loop_Para['simplex']][Loop_Para['state']] = Origin_Beta_Val    

def Experiment_2(Path, MULTI_NT, Beta):
    Cur_Time = time.strftime("_%Y_%m_%d_%H_%M_%S", time.localtime())#提前固定时间，都在同一个文件内表示
    Tag = "EP_2"
    Path = Path + '/' + Tag + Cur_Time
    try:
        os.mkdir(Path)
    except FileExistsError:
        pass
    Random_Gen_Seed = random.sample(range(0, N_NODES), int(N_NODES * Random_Gen_Ratio))
    inf_index_L1 = Random_Gen_Seed
    inf_index_L2 = Random_Gen_Seed
    Seed_Nodes = {Infected_Layer_L1: inf_index_L1, Infected_Layer_L2: inf_index_L2}      
    TIME_LAYER_LIST, TIME_L = SPREAD(MULTI_NT, Seed_Nodes, Beta, MAX_UNCHANGE_TIME)

    Output_TIME_LAYER_LIST(TIME_LAYER_LIST, TIME_L, Path + '/' + Tag + Cur_Time, N_NODES)


if __name__ == '__main__':
    Input_Filename = "100Hundred6_2_12_21"#指定的文件夹名称
    smp_inf = "2smp"#不用改
    ROOT_NAME = os.getcwd()
    NETWORK_PATH = ROOT_NAME + '/' + Input_Filename
    NAME_NT = lambda x: x + '.nt'
    Infected_Layer_L1 = 0
    Infected_Layer_L2 = 1
    Random_Gen_Ratio = 0.05#随机节点的比例 N_NODES * Random_Gen_Ratio
    Forget_Rate = [0.3, 0.3]#mu_X, mu_Y,自行指定
    MAX_UNCHANGE_TIME = 30
    Unchange_Ratio = 0.2#波动比例
    Beta_Step = 0.3#每次改变beta的步长
    Para_Dict = ['layer', 'simplex', 'state']#不需要改变



    detail = open(NETWORK_PATH + '/' + 'detail.txt', 'r')
    details = detail.readlines()
    detail.close()
    value = details[0].replace('\n', '').split(' ')
    value_2 = [int(nb) for nb in details[1].replace('\n', '').split()]
    infm = zip(value, value_2)
    N_NODES, N_LAYERS = value_2
    real_Filename = Input_Filename[len(str(N_NODES)): len(Input_Filename)]

    MULTI_NT = []
    MULTI_NT_2Simp = []
    for layer in range(N_LAYERS):
        G = copy_networkdata(NETWORK_PATH + '/' + NAME_NT(str(layer)))
        G_twosmpx = copy_2smpxdata(NETWORK_PATH + '/' + 'L{}_{}.pkl'.format(layer, real_Filename + '_' + smp_inf))
        MULTI_NT.append(G)
        MULTI_NT_2Simp.append(G_twosmpx)

    for network in MULTI_NT:
        nx.set_node_attributes(network, False, "INFECTED")#设置节点属性
        nx.set_node_attributes(network, None, "INFECTED_TIME")#设置节点属性
        
    #需要改变的参数
    Para_Beta_Set = [[0, 'edge', 'A']]

    
    # Output_Beta(NETWORK_PATH + '/' + 'Beta', Beta)
    #=========================实验1_1==========================
    #需要改变的参数
    # EP_1_1_Beta_0 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}#layer 0, A对应beta'
    # EP_1_1_Beta_1 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}#layer 1, U对应beta'
    # EP_1_1_Beta = {0:EP_1_1_Beta_0, 1:EP_1_1_Beta_1}
    # Para_Beta_Set_X = [[0, 'edge', 'A']]
    # Experiment_1_1(NETWORK_PATH, MULTI_NT, EP_1_1_Beta, Para_Beta_Set_X, Beta_Step)

    # #=========================实验1_2==========================
    # #需要改变的参数
    # EP_1_2_Beta_0 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}#layer 0, A对应beta'
    # EP_1_2_Beta_1 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}#layer 1, U对应beta'
    # EP_1_2_Beta = {0:EP_1_2_Beta_0, 1:EP_1_2_Beta_1}
    # Para_Beta_Set_Y = [[1, 'edge', 'A']]
    # Experiment_1_2(NETWORK_PATH, MULTI_NT, EP_1_2_Beta, Para_Beta_Set_Y, Beta_Step)

    #=========================实验2============================
    EP_2_Beta_0 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}#layer 0, A对应beta'
    EP_2_Beta_1 = {'edge':{'A': 0.1, 'U': 0.1}, '2simplx':{'A': 0.1, 'U': 0.1}}#layer 1, U对应beta'
    EP_2_Beta = {0:EP_2_Beta_0, 1:EP_2_Beta_1}    
    Experiment_2(NETWORK_PATH, MULTI_NT, EP_2_Beta)

    
