import matplotlib.pyplot as plt
from decimal import Decimal

import TM_analysis_function as TM

def print_graph(score):
    label_name=[]
    
    key_ = score[0].keys()
    #value_ = []
    
    for i in range(len(score)) :
        label_name.append('block'+ str(i+1))
    #label 이름 설정
    
    # x = np.arange(divi)
    x = [1]
    for i in range(1, len(key_)):
        x.append(TM.double_plus(x[0] , 0.5*i))
    
    
    # block에 따라 score 출력
    # x축: 블록
    # y축: 점수   
    width = 0.5
    c = ['black', 'dimgrey', 'darkgray', 'silver', 'lightgrey']
    fig, ax = plt.subplots()
    for i in score:
        data = list(i.values())
        rects1 = ax.bar(x, data, width, color=c)
        #for idx, item in enumerate(data):
            
        for k in range(0, len(key_)):
            x[k] += 3
    
    x_l = []
    x_l.append(int(len(key_)/2)+0.5)
    for i in range(len(score)-1):
        x_l.append(x_l[0] + 3*(i+1))

    print(x_l)

    plt.xticks(x_l, labels=label_name)
    #plt.show()
    plt.savefig('print_graph.png')
    


print_graph(TM.main())