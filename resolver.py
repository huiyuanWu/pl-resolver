import re
import itertools
import collections
import sys


def read_kb(path):
    file1 = path
    with open(file1) as f:
        kb = f.readlines()
    kb = [line.strip('\n') for line in kb]
    return kb

def read_alpha(path):
    file2 = path
    with open(file2) as f1:
        alpha = f1.readlines()
    alpha = [line.strip('\n') for line in alpha]
    return alpha

def add_alpha(kb, alpha):
    for x in alpha:
        kb.append(x)
    return kb

def negate(clause):
   l = clause.split('|')
   s = ""
   for x in l:
        if len(x) == 1:
            x = '-'+x
        elif len(x) == 2:
            x = x.replace('-','')
        s = s + x + '&'
   return s[:-1]

#to cnf step 3, from the input to a negated cnf. E.g: a & (b | -c)
def move_not_in(alpha):
    alpha_list = []
    for x in range(len(alpha)):
        if len(alpha[x]) > 2:
            alpha[x] = alpha[x].replace(" ", "|")
        alpha_list.append(alpha[x])
        alpha_list.append('&')
    alpha_list = alpha_list[:-1]
    list1 = []
    for y in alpha_list:
        if len(y) == 1:
            if y == '&':
                y = '|'
            else:
                y = '-'+y
        elif len(y) == 2:
            y = y.replace("-","")
        else:
            y = negate(y)
        list1.append(y)
    #print(list1)
    return list1

#take a list of negate sentence, perform the distributive and over or step
def format_alpha(list1):
    c = ''.join(list1)
    #print(c)
    new_alpha = []
    if '&' in c:
        alpha = c.split('|')
        #print(alpha)
        for i in range(len(alpha)):
            if '&' in alpha[i]:
                #print(alpha[i])
                new_alpha.append(distribute(alpha[i], alpha[i-1]))
            #else:
                new_alpha.append(alpha[i])
   # print(new_alpha)
    #print(res)
    else:
        for x in list1:
            if x != '|':
                new_alpha.append(x)
        c1 = ''.join(new_alpha)
        new_alpha = [c1]

    #print(list(flatten(new_alpha)))
    return list(flatten(new_alpha))

def distribute_and(and_atoms):
    new = set()
    for x in and_atoms[0]:
        new.add(x)
    del and_atoms[0]
    #print(list(new))
    if not and_atoms:
        return list(new)
    #print(and_atoms)
    n = len(new)
    for x in and_atoms:
        for i in x:
            for j in range(n):
                new.add(new.pop()+ ' ' + i)
    print(new)

#input is two sentences, peform distribute and over or. return tuple of new (s1, s2)
def distribute(list1):

    c = ''.join(list1)
    alpha = c.split('|')
    #print(alpha)
    l_and = []
    l_other = []
    temp = []
    for i in range(len(alpha)):
        if '&' in alpha[i]:
            l_and.append(alpha[i])
        else:
            l_other.append(alpha[i])
    for i in range(len(l_and)):
        temp.append(l_and[i].split('&'))
    

    while len(temp) > 1:
        res = dist(temp[0], temp[1])
        del temp[0]
        del temp[0]
        temp.insert(0, res)
        #print(temp)   

    temp_and = []
    
    if temp:
        
        if len(temp) == 1:
            for x in temp[0]:
                temp_and.append(x)
                #print(temp_and)
        else:
            temp0 = temp[0]
            del temp[0] 
            for e in temp0:
                for x in temp:
                    for i in x:
                        temp_and.append(i+' '+e)
               
    
    c1 = ' '.join(l_other)
    new_alpha = []

    temp_and = list(flatten(temp))
    
    if not temp_and:
        new_alpha.append(c1)

    if not c1:
        new_alpha = temp_and

    if temp_and and c1:
        for i in range(len(temp_and)):
            new_alpha.append(temp_and[i] + ' ' + c1)

    temp_alpha = []

    for x in new_alpha:
        atom = x.split(' ')
        atom = unique(atom)
        n = len(atom)
        if n == 1:
            temp_alpha.append(atom)
            continue

        pairs = [(atom[i], atom[j]) for i in range(n) for j in range(i+1, n)]
        for (xi, xj) in pairs:
 
            if xi == ('-'+xj) or xj == ('-'+xi):
                atom.remove(xi)
                atom.remove(xj)
            temp_alpha.append(atom)

    unique_data = [list(x) for x in set(tuple(x) for x in temp_alpha)]
    result = []
    for x in unique_data:
        if x:
            result.append(' '.join(x))

    return result

def dist(s1, s2):
    res = []
    for x in s1:
        for y in s2:
            res.append(x + ' '+ y)

    return res


def removeall(i, l):
    return [x for x in l if x!= i]

def unique(l):
    return list(set(l))


def flatten(foo):
    for x in foo:
        if hasattr(x, '__iter__') and not isinstance(x, str):
            for y in flatten(x):
                yield y
        else:
            yield x


def pl_resolution(kb, alpha):
    clauses = add_alpha(kb,alpha)
    #print(clauses)
    new = set()
    count = 0 
    while True:
        n = len(clauses)
        #print(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i+1, n)]
        for (ci, cj) in pairs:
            r = pl_resolve(ci, cj)
        
            count += r[1]
            if 'f' in r[0]:
                return'true ', count
            new = new.union(set(r[0]))
        if new.issubset(set(clauses)):
            return('false ', count)
        for c in new:
            if c not in clauses:
                #print(c)
                clauses.append(c)

def pl_resolve(ci, cj):
    li = ci.split()
    lj = cj.split()
    #print(li)
    clauses = []
    count = 0
    for di in li:
        #print(di)
        for dj in lj:
            if di == ('-'+dj) or ('-'+di) == dj:
                count += 1
                new = unique(removeall(di, li) + removeall(dj, lj))
                #print(new)
                res = ' '.join(new)
                #print(res)
                if len(res) == 0:
                    clauses.append('f')
                else:
                    clauses.append([res])
                    
    return (list(flatten(clauses)), count)

def main():
    kb_path = sys.argv[1]
    alpha_path = sys.argv[2]
    kb = read_kb(kb_path)
    alpha = read_alpha(alpha_path)
    a_list = move_not_in(alpha)
    f_alpha = distribute(a_list)
    #print(f_alpha)
    r = pl_resolution(kb, f_alpha)
    print(r[0], int(r[1]))


if  __name__ == '__main__':
    main()