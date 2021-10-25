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

