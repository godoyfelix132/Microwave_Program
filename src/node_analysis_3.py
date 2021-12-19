import os
from sympy import *
import numpy as np
import pandas as pd
init_printing()
import time

class NodeAnalysis:
    def __init__(self, root):
        num_rlc = 0  # number of passive elements
        num_ind = 0  # number of inductors
        num_v = 0    # number of independent voltage sources
        num_i = 0    # number of independent current sources
        i_unk = 0  # number of current unknowns
        pi = 3.141592654
        f = symbols('f')                       # RCL circuit
        fd1 = open(root, 'r')
        content = fd1.readlines()
        content = [x.strip() for x in content]  # remove leading and trailing white space
        while '' in content:
            content.pop(content.index(''))

        content = [n for n in content if not n.startswith('*')]
        content = [n for n in content if not n.startswith(';')]
        content = [n for n in content if not n.startswith('.')]
        content = [x.capitalize() for x in content]
        content = [' '.join(x.split()) for x in content]

        line_cnt = len(content)  # number of lines in the netlist
        branch_cnt = 0  # number of branches in the netlist
        lista = []
        nombres = []
        valores = []

        for i in range(line_cnt):
            x = content[i][0]
            tk_cnt = len(content[i].split()) # split the line into a list of words
            lista = content[i].split()
            nombres.append(lista[0])
            valores.append(lista[3])
            if (x == 'R') or (x == 'L') or (x == 'C'):
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_rlc += 1
                branch_cnt += 1
                if x == 'L':
                    num_ind += 1
            elif x == 'V':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_v += 1
                branch_cnt += 1
            else:
                print("unknown element type in branch {:d}, {:s}".format(i, content[i]))

        df = pd.DataFrame(columns=['element', 'p node', 'n node', 'cp node', 'cn node',
            'Vout', 'value', 'Vname', 'Lname1', 'Lname2'])

        df2 = pd.DataFrame(columns=['element', 'p node', 'n node'])

        def indep_source(line_nu):
            tk = content[line_nu].split()
            df.loc[line_nu, 'element'] = tk[0]
            df.loc[line_nu, 'p node'] = int(tk[1])
            df.loc[line_nu, 'n node'] = int(tk[2])
            df.loc[line_nu, 'value'] = float(tk[3])


        def rlc_element(line_nu):
            tk = content[line_nu].split()
            df.loc[line_nu, 'element'] = tk[0]
            df.loc[line_nu, 'p node'] = int(tk[1])
            df.loc[line_nu, 'n node'] = int(tk[2])
            df.loc[line_nu, 'value'] = float(tk[3])


        def count_nodes():
            p = np.zeros(line_cnt+1)
            for i in range(line_cnt-1):
                p[df['p node'][i]] = df['p node'][i]
                p[df['n node'][i]] = df['n node'][i]
            if df['n node'].max() > df['p node'].max():
                largest = df['n node'].max()
            else:
                largest = df['p node'].max()
            largest = int(largest)
            for i in range(1, largest):
                if p[i] == 0:
                    print('nodes not in continuous order, node {:.0f} is missing'.format(p[i-1]+1))
            return largest


        def count_nodes():
            p = np.zeros(line_cnt+1)
            for i in range(line_cnt-1):
                p[df['p node'][i]] = df['p node'][i]
                p[df['n node'][i]] = df['n node'][i]
            if df['n node'].max() > df['p node'].max():
                largest = df['n node'].max()
            else:
                largest = df['p node'].max()
            largest = int(largest)
            for i in range(1,largest):
                if p[i] == 0:
                    print('nodes not in continuous order, node {:.0f} is missing'.format(p[i-1]+1))
            return largest


        for i in range(line_cnt):
            x = content[i][0]

            if (x == 'R') or (x == 'L') or (x == 'C'):
                rlc_element(i)
            elif x == 'V':
                indep_source(i)
            else:
                print("unknown element type in branch {:d}, {:s}".format(i, content[i]))

        num_nodes = count_nodes()

        count = 0
        for i in range(len(df)):
            # process all the elements creating unknown currents
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if (x == 'L') or (x == 'V'):
                df2.loc[count, 'element'] = df.loc[i,'element']
                df2.loc[count, 'p node'] = df.loc[i,'p node']
                df2.loc[count, 'n node'] = df.loc[i,'n node']
                count += 1

        V = zeros(num_nodes, 1)
        I = zeros(num_nodes, 1)
        G = zeros(num_nodes, num_nodes)  # also called Yr, the reduced nodal matrix
        s = Symbol('s')  # the Laplace variable

        i_unk = num_v+num_ind

        B = zeros(num_nodes, i_unk)
        C = zeros(i_unk, num_nodes)
        D = zeros(i_unk, i_unk)
        Ev = zeros(i_unk, 1)
        J = zeros(i_unk, 1)

        for i in range(len(df)):  # process each row in the data frame
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            cn1 = df.loc[i, 'cp node']
            cn2 = df.loc[i, 'cn node']
            # process all the passive elements, save conductance to temp value
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if x == 'R':
                g = 1/sympify(df.loc[i, 'element'])
            if x == 'C':
                g = s*sympify(df.loc[i, 'element'])
            if (x == 'R') or (x == 'C'):
                if (n1 != 0) and (n2 != 0):
                    G[n1-1, n2-1] += -g
                    G[n2-1, n1-1] += -g
                if n1 != 0:
                    G[n1-1, n1-1] += g
                if n2 != 0:
                    G[n2-1, n2-1] += g

        sn = 0   # count source number as code walks through the data frame
        for i in range(len(df)):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            n_vout = df.loc[i, 'Vout']    # node connected to op amp output
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if x == 'V':
                if i_unk > 1:  # is B greater than 1 by n?, V
                    if n1 != 0:
                        B[n1-1, sn] = 1
                    if n2 != 0:
                        B[n2-1, sn] = -1
                else:
                    if n1 != 0:
                        B[n1-1] = 1
                    if n2 != 0:
                        B[n2-1] = -1
                sn += 1   # increment source count
            if x == 'L':
                if i_unk > 1:  # is B greater than 1 by n?, L
                    if n1 != 0:
                        B[n1-1, sn] = 1
                    if n2 != 0:
                        B[n2-1, sn] = -1
                else:
                    if n1 != 0:
                        B[n1-1] = 1
                    if n2 != 0:
                        B[n2-1] = -1
                sn += 1   # increment source count

        if sn != i_unk:
            print('source number, sn={:d} not equal to i_unk={:d} in matrix B'.format(sn, i_unk))


        def find_vname(name):
            # need to walk through data frame and find these parameters
            for i in range(len(df2)):
                # process all the elements creating unknown currents
                if name == df2.loc[i, 'element']:
                    n1 = df2.loc[i, 'p node']
                    n2 = df2.loc[i, 'n node']
                    return n1, n2, i  # n1, n2 & col_num are from the branch of the controlling element
            print('failed to find matching branch element in find_vname')


        sn = 0   # count source number as code walks through the data frame
        for i in range(len(df)):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            cn1 = df.loc[i, 'cp node']  # nodes for controlled sources
            cn2 = df.loc[i, 'cn node']
            n_vout = df.loc[i, 'Vout']  # node connected to op amp output
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if x == 'V':
                if i_unk > 1:  # is B greater than 1 by n?, V
                    if n1 != 0:
                        C[sn, n1-1] = 1
                    if n2 != 0:
                        C[sn, n2-1] = -1
                else:
                    if n1 != 0:
                        C[n1-1] = 1
                    if n2 != 0:
                        C[n2-1] = -1
                sn += 1   # increment source count
            if x == 'L':
                if i_unk > 1:  # is B greater than 1 by n?, L
                    if n1 != 0:
                        C[sn, n1-1] = 1
                    if n2 != 0:
                        C[sn, n2-1] = -1
                else:
                    if n1 != 0:
                        C[n1-1] = 1
                    if n2 != 0:
                        C[n2-1] = -1
                sn += 1   # increment source count

        if sn != i_unk:
            print('source number, sn={:d} not equal to i_unk={:d} in matrix C'.format(sn, i_unk))

        sn = 0   # count source number as code walks through the data frame
        for i in range(len(df)):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if (x == 'V') or (x == 'O') or (x == 'E'):  # need to count V, E & O types
                sn += 1   # increment source count
            if x == 'L':
                if i_unk > 1:  # is D greater than 1 by 1?
                    D[sn, sn] += -s*sympify(df.loc[i, 'element'])
                else:
                    D[sn] += -s*sympify(df.loc[i, 'element'])
                sn += 1   # increment source count

        for i in range(num_nodes):
            V[i] = sympify('v{:d}'.format(i+1))

        for i in range(len(df2)):
            # process all the unknown currents
            J[i] = sympify('I_{:s}'.format(df2.loc[i, 'element']))

        for i in range(len(df)):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if x == 'I':
                g = sympify(df.loc[i, 'element'])
                if n1 != 0:
                    I[n1-1] -= g
                if n2 != 0:
                    I[n2-1] += g

        sn = 0   # count source number
        for i in range(len(df)):
            # process all the passive elements
            x = df.loc[i, 'element'][0]   # get 1st letter of element name
            if x == 'V':
                Ev[sn] = sympify(df.loc[i, 'element'])
                sn += 1

        Z = I[:] + Ev[:]  # the + operator in python concatenates the lists
        X = V[:] + J[:]  # the + operator in python concatenates the lists
        n = num_nodes
        m = i_unk
        A = zeros(m+n, m+n)


        for i in range(n):
            for j in range(n):
                A[i, j] = G[i, j]

        if i_unk > 1:
            for i in range(n):
                for j in range(m):
                    A[i, n+j] = B[i, j]
                    A[n+j, i] = C[j, i]

            for i in range(m):
                for j in range(m):
                    A[n+i, n+j] = D[i, j]

        if i_unk == 1:
            for i in range(n):
                A[i, n] = B[i]
                A[n, i] = C[i]

        n = num_nodes
        m = i_unk
        eq_temp = 0  # temporary equation used to build up the equation
        equ = zeros(m+n, 1)  # initialize the array to hold the equations
        for i in range(n+m):
            for j in range(n+m):
                eq_temp += A[i, j]*X[j]
            equ[i] = Eq(eq_temp, Z[i])
            eq_temp = 0

        print('X',X)
        print('A',A)
        print('equ',equ)
        V1, V2, I_V1, I_V2 = symbols('V1 V2 I_V1 I_V2 ')

        Final_Sol = solve(equ, X)
        print(Final_Sol)
        iv1 = Final_Sol[I_V1]
        iv2 = Final_Sol[I_V2]

        y11 = -1*(I_V1/V1)
        Y11 = y11.subs({I_V1: iv1})
        Y11 = Y11.subs({V1: 1})
        Y11 = Y11.subs({V2: 0})


        y21 = -1*(I_V2/V1)
        Y21 = y21.subs({I_V2: iv2})
        Y21 = Y21.subs({V1: 1})
        Y21 = Y21.subs({V2: 0})


        y12 = -1*(I_V1/V2)
        Y12 = y12.subs({I_V1: iv1})
        Y12 = Y12.subs({V1: 0})
        Y12 = Y12.subs({V2: 1})

        y22 = -1*(I_V2/V2)
        Y22 = y22.subs({I_V2: iv2})
        Y22 = Y22.subs({V1: 0})
        Y22 = Y22.subs({V2: 1})

        xx = Matrix([[Y11, Y12], [Y21, Y22]])
        print(xx)

        y_11 = Y11
        y_22 = Y22
        y_21 = Y21
        y_12 = Y12
        _locals = locals()
        for i in range(0, len(nombres)):
            exec("%s=symbols('%s')" % (nombres[i], nombres[i]))
            if i == 0:
                exec("y_11 = Y11.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
                exec("y_22 = Y22.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
                exec("y_21 = Y21.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
                exec("y_12 = Y12.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
            else:
                exec("y_11 = y_11.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
                exec("y_22 = y_22.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
                exec("y_21 = y_21.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
                exec("y_12 = y_12.subs({symbols('%s'):float(%s)})" % (nombres[i], valores[i]), globals(), _locals)
            y_11 = _locals["y_11"]
            y_22 = _locals["y_22"]
            y_21 = _locals["y_21"]
            y_12 = _locals["y_12"]

        y_11 = simplify(y_11.subs({s: 1J * f * 2 * pi}))
        y_22 = simplify(y_22.subs({s: 1J * f * 2 * pi}))
        y_21 = simplify(y_21.subs({s: 1J * f * 2 * pi}))
        y_12 = simplify(y_12.subs({s: 1J * f * 2 * pi}))

        self.Y_matriz = Matrix([[y_11, y_12], [y_21, y_22]])
        print(self.Y_matriz)
        print(X)
        for i in A:
            pass
            #print(i)

if __name__ == '__main__':
    n = NodeAnalysis('net.txt')
    #print(n.Y_matriz)