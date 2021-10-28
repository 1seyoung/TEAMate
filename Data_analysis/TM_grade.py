import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import TM_analysis_function as TM
def grade(name_score, contri, result) :
    parti = name_score
    min_parti = sum(list(name_score.values()))*1/(len(name_score)*2)    ##참여도 최솟값
    
    for i in list(parti.keys()) : 
        parti[i] -= min_parti

    result_grade = name_score
    for i in list(parti.keys()) : # i = user_id
        if parti[i] > 0 :
            result_grade[i] = (contri[i] * result) + parti[i]
        else :
            result_grade[i] = 0
    
    return result_grade
def print_graph(score, group_id):
    label_name=[]
    
    key_ = score[0].keys()
    #value_ = []
    
    for i in range(len(score)) :
        label_name.append('b'+ str(i+1))
    #label 이름 설정
    
    # x = np.arange(divi)
    x = [1]
    for i in range(1, len(key_)):
        x.append(TM.double_plus(x[0] , 0.5*i))
    
    
    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수   
    width = 0.5
    c = ['slategrey', 'lightblue', 'cornflowerblue', 'royalblue', 'slateblue']
    fig, ax = plt.subplots()
    for idx, i in enumerate(score):
        data = list(i.values())
        name_g = list(i.keys())
        if idx == 0 :
            for idx2, j in enumerate(data) :
                rects1 = ax.bar(x[idx2], j, width, color=c[idx2], label = str(name_g[idx2]))
            for k in range(0, len(key_)):
                x[k] += 3
            continue
        rects1 = ax.bar(x, data, width, color=c)
        #for idx, item in enumerate(data):
            
        for k in range(0, len(key_)):
            x[k] += 3
    
    plt.legend((key_))
    x_l = []
    x_l.append(int(len(key_)/2)+0.5)
    for i in range(len(score)-1):
        x_l.append(x_l[0] + 3*(i+1))

    plt.xticks(x_l, labels=label_name)
    ax.set_ylabel('Scores')
    ax.set_title('TEAMate')
    #plt.show()
    save_name = group_id
    plt.savefig('print_graph' + str(group_id))

score = [{1750342024: 2.0, 1937944242: 0.0, 1739915236: 1.6}, {1750342024: 11.2, 1937944242: 0, 1739915236: 11.8}, {1750342024: 10.2, 1937944242: 24.1, 1739915236: 25.1}, {1750342024: 0, 1937944242: 1.0, 1739915236: 2.0}, {1750342024: 6.3, 1937944242: 0, 1739915236: 6.6}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 6.5, 1937944242: 0, 1739915236: 8.3}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}, {1750342024: 0, 1937944242: 0, 1739915236: 1.0}]
print_graph(score, -472653938)