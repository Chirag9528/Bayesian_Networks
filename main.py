import sys
import itertools
import random

class Solution:
    def __init__(self,f,g,h):
        self.f = open(f,'r')
        self.g = open(g,'r')
        self.h = open(h,'w')
        self.distribution_tables = dict({})
        self.random_variables = 0 
        self.adjacency_list = []
        self.list_with_no_parents = []
    
    def make_distribution_table(self):
        self.random_variables = int(self.f.readline().rstrip())
        for i in range(self.random_variables+1):  # for capturing network through adjacency list for rejection sampling
            self.adjacency_list.append([])
        for i in range(1,self.random_variables+1):
            line = [int(i) for i in self.f.readline().rstrip().split(" ")]
            if len(line)==1:
                self.list_with_no_parents.append(line[0])       # since it has no parent
                line_ = [float(i) for i in self.f.readline().rstrip().split(" ")]
                dictionary = dict({})
                dictionary[(line[0],)] = line_[0]
                dictionary[(-line[0],)] = line_[1]
                self.distribution_tables[f'P({line[0]})'] =  dictionary
            else:
                # For adjacency list
                for aa in range(1,len(line)):
                    self.adjacency_list[line[aa]].append(line[0])
                # adjacency list done
                list1 = []
                for j in range(1,len(line)):
                    lst = [line[j] , -line[j]]
                    list1.append(lst)
                allcombinations = list(itertools.product(*list1))  # generating all combinations
                dictionary = dict({})
                for j in allcombinations:
                    line_ = [float(i) for i in self.f.readline().rstrip().split(" ")]
                    dictionary[((line[0] , '|') +  j)] = line_[0]
                    dictionary[((-line[0] , '|') +  j)] = line_[1]
                string2 = f'P({line[0]}|'
                for j in range(1,len(line)-1):
                    string2+=f'{line[j]},'
                string2 += f'{line[-1]})'
                self.distribution_tables[string2] = dictionary

    def join(self,table1 , table2):
        new_dict = dict({})
        for i in table1:
            for j in table2:
                slash_table1 = -1
                slash_table2 = -1
                for x in range(len(i)):
                    if i[x]=='|':
                        slash_table1 = x
                for y in range(len(j)):
                    if j[y]=='|':
                        slash_table2 = y
                if slash_table1 == -1:
                    table1_children = [x for x in i]       # children of first table
                    table1_parent = []      # parent of first table
                else:
                    table1_children = [x for x in i[:slash_table1]]   # children of first table 
                    table1_parent = [x for x in i[slash_table1+1:]]  # parent of first table

                if slash_table2 == -1:
                    table2_children = [x for x in j]  # children of second table 
                    table2_parent = []      # parent of second table
                else:
                    table2_children = [x for x in j[:slash_table2]]  # children of second table
                    table2_parent = [x for x in j[slash_table2+1:]]  # parent of second table
                temp = []  #temp list
                flag = False
                for p in table1_children:
                    if p in table2_parent: # removing node in parent if present
                        temp.append(p) 
                        table2_parent.remove(p)
                    else:
                        temp.append(p)
                if not flag:
                    for p in table2_children:
                        if -p in temp: 
                            flag = True
                            break
                        if p not in temp:
                            if p in table1_parent: # removing node in parent if present
                                temp.append(p)
                                table1_parent.remove(p)
                            else:
                                temp.append(p) 
                if not flag:
                    temp.append('|')
                    for p in table1_parent:
                        if -p in temp:
                            flag = True
                            break
                        if p not in temp:
                            if p in table2_parent:  # removing common element from other table's parent list
                                temp.append(p)
                                table2_parent.remove(p)
                            else:
                                temp.append(p)
                
                if not flag:
                    for p in table2_parent:
                        if -p in temp :
                            flag = True
                            break
                        if p not in temp:
                            temp.append(p)
                if not flag:
                    if temp[-1] == '|':   # if no parent present on join
                        temp = temp[:-1]
                    new_dict[tuple(temp)] = table1[i]*table2[j]
        temp2 = list(new_dict.keys())[0]
        string =f"P("
        for i in temp2:
            if i=='|':
                string = string[:-1]
                string+=i
            else:
                string+=f'{i},'
        string = string[:-1]
        string+=f')'
        return string , new_dict

    def sum(self,distribution_table , variable):
        new_dict = dict({})
        for key in distribution_table.keys():
            newkey = tuple([i for i in key if i!=variable and i!=-variable])  # removing variable that is to be sum out
            if len(newkey)>0:
                if newkey[0] == '|':
                    return "#" , dict({})
                elif newkey[-1] == '|':
                    newkey = tuple(list(newkey)[:-1])
            if newkey not in new_dict.keys():
                new_dict[newkey] = distribution_table[key]
            else:
                new_dict[newkey] += distribution_table[key]
                new_dict[newkey] = new_dict[newkey]
        temp2 = list(new_dict.keys())[0]
        string =f"P("
        for i in temp2:
            if i=='|':
                string = string[:-1]
                string+=i
            else:
                string+=f'{i},'
        if string[-1]==',':
            string = string[:-1]
        string+=f')'
        return string , new_dict

    def normalize(self,table , value):
        for i in table.keys():
            table[i] = table[i]/value
        return table

    def reduce(self,joint_table , evidence):
        new_dict = dict({})
        key = list(joint_table.keys())[0]
        for i in joint_table[key].keys():
            list1 = list(i)
            flag = False
            for j in evidence:
                if j not in list1:
                    flag = True
                    break
            if not flag:
                new_dict[i] = joint_table[key][i]
        return new_dict
    
    def variable_elimination(self, q , e , h):
        dictionary = self.distribution_tables.copy()
        for i in h:     # removing hidden variables
            keys = list(dictionary.keys())
            tables = [] # tables that have i (hidden variable)
            temp = [] # just to take latest table after join for i (hidden variable)
            for j in keys:
                if f'|{i})' in j or f'|{i},' in j or f',{i}|' in j or f',{i},' in j or f',{i})' in j or f'({i})' in j or f'({i},' in j or f'({i}|' in j:  # finding tables with hidden variable
                    tables.append(j)
            if len(tables)>1:  # joining two tables with hidden variables
                table_name , new_table = self.join(dictionary[tables[0]] , dictionary[tables[1]])
                del dictionary[tables[0]]
                del dictionary[tables[1]]
                dictionary[table_name] = new_table
                temp.append(new_table)
                for j in range(2,len(tables)):
                    del_table = table_name
                    table_name , new_table = self.join(new_table , dictionary[tables[j]])
                    del dictionary[tables[j]]
                    del dictionary[del_table]
                    dictionary[table_name] = new_table
                    temp.append(new_table)
            else:
                temp = [dictionary[tables[0]]]
                table_name = tables[0]
    
            table_name2 , new_table2 = self.sum(temp[-1],i)    # summing out the hidden variable
            del dictionary[table_name]
            if table_name2 != "#":
                dictionary[table_name2] = new_table2
        
        #joining rest of tables
        query_evidence = q + e
        query_evidence = [abs(k) for k in query_evidence]
        for i in query_evidence:
            tables_join = []
            keys = list(dictionary.keys())
            for j in keys:
                if f'|{i})' in j or f'|{i},' in j or f',{i}|' in j or f',{i},' in j or f',{i})' in j or f'({i})' in j or f'({i},' in j or f'({i}|' in j:  # finding tables with hidden variable
                    tables_join.append(j)
            if len(tables_join)>1:
                table_name , new_table = self.join(dictionary[tables_join[0]] , dictionary[tables_join[1]])
                del dictionary[tables_join[0]]
                del dictionary[tables_join[1]]
                dictionary[table_name] = new_table
                for j in range(2,len(tables_join)):
                    del_table = table_name
                    table_name , new_table = self.join(new_table , dictionary[tables_join[j]])
                    del dictionary[tables_join[j]]
                    del dictionary[del_table]
                    dictionary[table_name] = new_table

        # reducing the joint distribution table
        dictionary = self.reduce(dictionary , e)

        table = dictionary.copy()
        for i in q:
            string , table = self.sum(table,i)

        # Evidence probability
        evidence_probability = list(table.values())[0]
        if evidence_probability > 0:
            # Normalization of table
            dictionary = self.normalize(dictionary , evidence_probability)

            # taking out the desired probability
            desired_probabilty = 0
            for i in dictionary.keys():
                flag = False
                for j in q:
                    if j not in i:
                        flag = True
                        break
                if not flag:
                    desired_probabilty = dictionary[i]
                    break

            self.h.write(f'{desired_probabilty}\n')
            
        else:
            desired_probabilty = 0
            self.h.write(f'{desired_probabilty}\n')

    def findtable(self, i):
        for key , value in self.distribution_tables.items():
            if key.find("|")!=-1:
                a = key.split("|")[0].split("(")[1]
                if a == str(i):
                    return value
            else:
                a = key.split("(")[1].split(")")[0]
                if a == str(i):
                    return value

    def ischildrenthere(self , table):
        for key , value in table.items():
            count = 0
            for i in key:
                if i!='|':
                    if self.visited[abs(i)] == 0:
                        count+=1
            if count == 1:
                return 0
            else:
                return 1

    def findvalue(self, table , value , list , var):
        for key , val in table.items():
            flag = False
            for i in list :
                if i not in key and -i in key:
                    flag = True
                    break
            if not flag:
                if value <= val:
                    if var in key :
                        return var
                    else:
                        return -var
                else:
                    if var in key :
                        return -var
                    else:
                        return +var

    def dfs(self , i , lst):
        table = self.findtable(i)
        flag = self.ischildrenthere(table)
        if flag == 1 :
            return lst
        self.visited[i] = 1
        random_value = random.random()
        rv = self.findvalue(table , random_value , lst , i)
        lst.append(rv)
        for z in self.adjacency_list[i]:
            if self.visited[z]==0:
                lst=self.dfs(z , lst)
        return lst

    def sampling(self):
        self.visited = [0]*(self.random_variables+1)
        sampling_list = []
        for i in self.list_with_no_parents:
            sampling_list = self.dfs(i, sampling_list)
        return sampling_list

    def rejection_sampling(self , q , e , h):
        all_samples = []
        for i in range(10000):
            sample = self.sampling()
            flag = False
            for j in e : 
                if j not in sample:
                    flag = True
                    break
            if not flag:
                all_samples.append(sample)
        count = 0
        for i in all_samples:
            flag = False
            for j in q:
                if j not in i:
                    flag = True
                    break
            if not flag :
                count+=1
        if len(all_samples)==0:
            self.h.write(f'0\n')    
        else:
            self.h.write(f'{count/len(all_samples)}\n')
                
    def solve(self):
        self.make_distribution_table()
        queries = [i.rstrip() for i in self.g.readlines()]
        for i in queries:
            l = i.split()
            q = l[l.index('q')+1:l.index('e')]   # queries
            e = l[l.index('e')+1:]  # evidence
            for x in range(len(q)):
                if (q[x].find("~"))!=-1:
                    q[x] = -int(q[x][1:])
                else:
                    q[x] = int(q[x])

            for x in range(len(e)):
                if (e[x].find("~"))!=-1:
                    e[x] = -int(e[x][1:])
                else:
                    e[x] = int(e[x])

            # for hidden variables
            h = []  # hidden variables
            for j in range(1,self.random_variables+1):
                if j not in q and -j not in q and j not in e and -j not in e:
                    h.append(j)
            
            if 've' in i:
                self.variable_elimination(q , e , h)
            else:
                self.rejection_sampling(q , e , h)

if __name__ == "__main__":
    f = sys.argv[1]
    g = sys.argv[2]
    h = 'ans'+f[-5:]
    sol = Solution(f,g,h)
    sol.solve()
    