import os
from sympy import *
import numpy as np
import pandas as pd
init_printing()
import time



class NodeAnalysis:
    def __init__(self, root):
        pi = 3.141592654
        f = symbols("f")
        num_rlc = 0  # number of passive elements
        num_v = 0  # number of independent voltage sources
        num_i = 0  # number of independent current sources
        num_opamps = 0  # number of op amps
        num_vcvs = 0  # number of controlled sources of various types
        num_vccs = 0
        num_cccs = 0
        num_ccvs = 0
        num_cpld_ind = 0  # number of coupled inductors

        # ##### open file and preprocess it
        # - remove blank lines and comments
        # - convert first letter of element name to upper case
        # - removes extra spaces between entries
        # - count number of entries on each line, make sure the count is correct

        fd1 = open(root, 'r')
        content = fd1.readlines()
        content = [x.strip() for x in content]  # remove leading and trailing white space
        # remove empty lines
        while '' in content:
            content.pop(content.index(''))

        # remove comment lines, these start with a asterisk *
        content = [n for n in content if not n.startswith('*')]
        # converts 1st letter to upper case
        # content = [x.upper() for x in content] <- this converts all to upper case
        content = [x.capitalize() for x in content]
        # removes extra spaces between entries
        content = [' '.join(x.split()) for x in content]


        branch_cnt = len(content)
        # check number of entries on each line
        lista = []
        nombres = []
        valores = []
        for i in range(branch_cnt):
            x = content[i][0]
            tk_cnt = len(content[i].split())
            lista = content[i].split()
            nombres.append(lista[0])
            valores.append(lista[3])

            if (x == 'R') or (x == 'L') or (x == 'C'):
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_rlc += 1
            elif x == 'V':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_v += 1
            elif x == 'I':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_i += 1
            elif x == 'O':
                if tk_cnt != 4:
                    print("branch {:d} not formatted correctly, {:s}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_opamps += 1
            elif x == 'E':
                if (tk_cnt != 6):
                    print("branch {:d} not formatted correctly, {}".format(i, content[i]))
                    print("had {:d} items and should only be 6".format(tk_cnt))
                num_vcvs += 1
            elif x == 'G':
                if (tk_cnt != 6):
                    print("branch {:d} not formatted correctly, {}".format(i, content[i]))
                    print("had {:d} items and should only be 6".format(tk_cnt))
                num_vccs += 1
            elif x == 'F':
                if (tk_cnt != 5):
                    print("branch {:d} not formatted correctly, {}".format(i, content[i]))
                    print("had {:d} items and should only be 5".format(tk_cnt))
                num_cccs += 1
            elif x == 'H':
                if (tk_cnt != 5):
                    print("branch {:d} not formatted correctly, {}".format(i, content[i]))
                    print("had {:d} items and should only be 5".format(tk_cnt))
                num_ccvs += 1
            elif x == 'K':
                if (tk_cnt != 4):
                    print("branch {:d} not formatted correctly, {}".format(i, content[i]))
                    print("had {:d} items and should only be 4".format(tk_cnt))
                num_cpld_ind += 1
            else:
                print("unknown element type in branch {:d}, {}".format(i, content[i]))

        # ##### parser
        # - puts branch elements into structure
        # - counts number of nodes


        # build the pandas data frame
        count = []  # data frame index
        element = []  # type of element
        p_node = []  # positive node
        n_node = []  # neg node
        cp_node = []  # controlling positive node of branch
        cn_node = []  # controlling negitive node of branch
        v_out = []  # op amp output node
        value = []  # value of element or voltage
        v_name = []  # voltage source through which the controlling current flows
        l_name1 = []  # name of coupled inductor 1
        l_name2 = []  # name of coupled inductor 2

        df = pd.DataFrame(index=count, columns=['element', 'p node', 'n node', 'cp node', 'cn node',
                                                'v out', 'value', 'v name', 'l_name1', 'l_name2'])

        # ##### functions to load branch elements into data frame


        # loads voltage or current sources into branch structure
        def indep_source(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'value'] = float(tk[3])

        # loads passive elements into branch structure
        def rlc_element(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'value'] = float(tk[3])


        def opamp_sub_network(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'v out'] = int(tk[3])

        def vccs_sub_network(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'cp node'] = int(tk[3])
            df.loc[br_nu, 'cn node'] = int(tk[4])
            df.loc[br_nu, 'value'] = float(tk[5])

        def vcvs_sub_network(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'cp node'] = int(tk[3])
            df.loc[br_nu, 'cn node'] = int(tk[4])
            df.loc[br_nu, 'value'] = float(tk[5])

        def cccs_sub_network(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'v name'] = tk[3]
            df.loc[br_nu, 'value'] = float(tk[4])

        def ccvs_sub_network(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'p node'] = int(tk[1])
            df.loc[br_nu, 'n node'] = int(tk[2])
            df.loc[br_nu, 'v name'] = tk[3]
            df.loc[br_nu, 'value'] = float(tk[4])

        def cpld_ind_network(br_nu):
            tk = content[br_nu].split()
            df.loc[br_nu, 'element'] = tk[0]
            df.loc[br_nu, 'l name1'] = tk[1]
            df.loc[br_nu, 'l name2'] = tk[2]
            df.loc[br_nu, 'value'] = float(tk[3])

        # function to scan df and get largest node number
        def count_nodes():
            # need to check that nodes are consecutive
            # fill array with node numbers
            p = np.zeros(branch_cnt + 1)
            for i in range(branch_cnt - 1):
                p[df['p node'][i]] = df['p node'][i]
                p[df['n node'][i]] = df['n node'][i]

            # find the largest node number
            if df['n node'].max() > df['p node'].max():
                largest = df['n node'].max()
            else:
                largest = df['p node'].max()

                largest = int(largest)
            # check for unfilled elements, skip node 0
            for i in range(1, largest):
                if p[i] == 0:
                    print("nodes not in continuous order");

            return largest


        # load branches into data frame
        for i in range(branch_cnt):
            x = content[i][0]

            if (x == 'R') or (x == 'L') or (x == 'C'):
                rlc_element(i)
            elif (x == 'V') or (x == 'I'):
                indep_source(i)
            elif x == 'O':
                opamp_sub_network(i)
            elif x == 'E':
                vcvs_sub_network(i)
            elif x == 'G':
                vccs_sub_network(i)
            elif x == 'F':
                cccs_sub_network(i)
            elif x == 'H':
                ccvs_sub_network(i)
            else:
                print("unknown element type in branch {:d}, {}".format(i, content[i]))

        # count number of nodes
        num_nodes = count_nodes()


        # store the data frame as a pickle file
        #df.to_pickle(fn + '.pkl')


        # initialize some symbolic matrix with zeros
        # A is formed by [[G, C] [B, D]]
        # Z = [I,E]
        # X = [V, J]
        V = zeros(num_nodes, 1)
        I = zeros(num_nodes, 1)
        G = zeros(num_nodes, num_nodes)
        s = Symbol('s')

        if (num_v + num_opamps) != 0:
            B = zeros(num_nodes, num_v + num_opamps)
            C = zeros(num_v + num_opamps, num_nodes)
            D = zeros(num_v + num_opamps, num_v + num_opamps)
            E = zeros(num_v + num_opamps, 1)
            J = zeros(num_v + num_opamps, 1)

        # ##### G matrix
        # The G matrix is n by n and is determined by the interconnections between the passive circuit elements (RLC's).  The G matrix is an nxn matrix formed in two steps:
        # 1. Each element in the diagonal matrix is equal to the sum of the conductance (one over the resistance) of each element connected to the corresponding node.  So the first diagonal element is the sum of conductances connected to node 1, the second diagonal element is the sum of conductances connected to node 2, and so on.
        # 2. The off diagonal elements are the negative conductance of the element connected to the pair of corresponding node.  Therefore a resistor between nodes 1 and 2 goes into the G matrix at location (1,2) and locations (2,1).


        # G matrix
        for i in range(branch_cnt):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            # process all the passive elements, save conductance to temp value
            x = df.loc[i, 'element'][0]  # get 1st letter of element name
            if x == 'R':
                g = 1 / sympify(df.loc[i, 'element'])
            if x == 'L':
                g = 1 / (s * sympify(df.loc[i, 'element']))
            if x == 'C':
                g = sympify(df.loc[i, 'element']) * s

            if (x == 'R') or (x == 'L') or (x == 'C'):
                # If neither side of the element is connected to ground
                # then subtract it from appropriate location in matrix.
                if (n1 != 0) and (n2 != 0):
                    G[n1 - 1, n2 - 1] += -g
                    G[n2 - 1, n1 - 1] += -g

                # If node 1 is connected to ground, add element to diagonal of matrix
                if n1 != 0:
                    G[n1 - 1, n1 - 1] += g

                # same for for node 2
                if n2 != 0:
                    G[n2 - 1, n2 - 1] += g

        G  # display the G matrix

        # ##### I matrix
        # The I matrix is an n by 1 matrix with each element of the matrix corresponding to a particular node.  The value of each element of I is determined by the sum of current sources into the corresponding node.  If there are no current sources connected to the node, the value is zero.

        # generate the I matrix
        for i in range(branch_cnt):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            # process all the passive elements, save conductance to temp value
            x = df.loc[i, 'element'][0]  # get 1st letter of element name
            if x == 'I':
                g = sympify(df.loc[i, 'element'])
                # sum the current into each node
                if n1 != 0:
                    I[n1 - 1] += g
                if n2 != 0:
                    I[n2 - 1] -= g

        I  # display the I matrix

        # ##### V matrix
        # The V matrixis an nx1 matrix formed of the node voltages.  Each element in V corresponds to the voltage at the equivalent node in the circuit


        # generate the V matrix
        for i in range(num_nodes):
            V[i] = sympify('v{:d}'.format(i + 1))

        V  # display the V matrix

        # ##### B Matrix
        # Rules for making the B matrix
        # The B matrix is an nxm matrix with only 0, 1 and -1 elements.  Each location in the matrix corresponds to a particular voltage source (first dimension) or a node (second dimension).  If the positive terminal of the ith voltage source is connected to node k, then the element (i,k) in the B matrix is a 1.  If the negative terminal of the ith voltage source is connected to node k, then the element (i,k) in the B matrix is a -1.  Otherwise, elements of the B matrix are zero.


        # generate the B Matrix
        # loop through all the branches and process independent voltage sources
        sn = 0  # count source number
        for i in range(branch_cnt):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            # process all the independent voltage sources
            x = df.loc[i, 'element'][0]  # get 1st letter of element name
            if x == 'V':
                if num_v + num_opamps > 1:
                    if n1 != 0:
                        B[n1 - 1, sn] = 1
                    if n2 != 0:
                        B[n2 - 1, sn] = -1
                    sn += 1  # increment source count
                else:
                    if n1 != 0:
                        B[n1 - 1] = 1
                    if n2 != 0:
                        B[n2 - 1] = -1

        # ##### J matrix
        # The is an mx1 matrix, with one entry for the current through each voltage source.


        # The J matrix is an mx1 matrix, with one entry for the current through each voltage source.
        sn = 0  # count source number
        oan = 0  # count op amp number
        for i in range(branch_cnt):
            # process all the passive elements
            x = df.loc[i, 'element'][0]  # get 1st letter of element name
            if x == 'V':
                J[sn] = sympify('I_{:s}'.format(df.loc[i, 'element']))
                sn += 1

        # ##### C matrix
        # The C matrix is an mxn matrix with only 0, 1 and -1 elements.  Each location in the matrix corresponds to a particular node (first dimension) or voltage source (second dimension).  If the positive terminal of the ith voltage source is connected to node k, then the element (k,i) in the C matrix is a 1.  If the negative terminal of the ith voltage source is connected to node k, then the element (k,i) in the C matrix is a -1.  Otherwise, elements of the C matrix are zero.


        # generate the C matrix
        sn = 0  # count source number
        for i in range(branch_cnt):
            n1 = df.loc[i, 'p node']
            n2 = df.loc[i, 'n node']
            # process all the independent voltage sources
            x = df.loc[i, 'element'][0]  # get 1st letter of element name
            if x == 'V':
                if num_v + num_opamps > 1:
                    if n1 != 0:
                        C[sn, n1 - 1] = 1
                    if n2 != 0:
                        C[sn, n2 - 1] = -1
                    sn += 1  # increment source count
                else:
                    if n1 != 0:
                        C[n1 - 1] = 1
                    if n2 != 0:
                        C[n2 - 1] = -1

        # ##### D matrix
        # The D matrix is an mxm matrix that is composed entirely of zeros.  (It can be non-zero if dependent sources are considered.)


        # display the The D matrix

        # ##### E matrix
        # The E matrix is mx1 and holds the values of the independent voltage sources.


        # generate the E matrix
        sn = 0  # count source number
        for i in range(branch_cnt):
            # process all the passive elements
            x = df.loc[i, 'element'][0]  # get 1st letter of element name
            if x == 'V':
                E[sn] = sympify(df.loc[i, 'element'])
                sn += 1

        # ##### Z matrix
        # The Z matrix holds the independent voltage and current sources and is the combination of 2 smaller matrices I and E.  The Z matrix is (m+n) by 1, n is the number of nodes, and m is the number of independent voltage sources.  The I matrix is n by 1 and contains the sum of the currents through the passive elements into the corresponding node (either zero, or the sum of independent current sources). The E matrix is m by 1 and holds the values of the independent voltage sources.


        Z = I[:] + E[:]

        # ##### X matrix
        # The X matrix is an (n+m) by 1 vector that holds the unknown quantities (node voltages and the currents through the independent voltage sources). The top n elements are the n node voltages. The bottom m elements represent the currents through the m independent voltage sources in the circuit. The V matrix is n by 1 and holds the unknown voltages.  The J matrix is m by 1 and holds the unknown currents through the voltage sources

        X = V[:] + J[:]

        # ##### A matrix
        # The A matrix is (m+n) by (m+n) and will be developed as the combination of 4 smaller matrices, G, B, C, and D.

        n = num_nodes
        m = num_v
        A = zeros(m + n, m + n)
        for i in range(n):
            for j in range(n):
                A[i, j] = G[i, j]

        if num_v + num_opamps > 1:
            for i in range(n):
                for j in range(m):
                    A[i, n + j] = B[i, j]
                    A[n + j, i] = C[j, i]
        else:
            for i in range(n):
                A[i, n] = B[i]
                A[n, i] = C[i]

        # generate the node equations
        n = num_nodes
        m = num_v
        eq1 = 0
        equ = zeros(m + n, 1)
        for i in range(n + m):
            for j in range(n + m):
                eq1 += A[j, i] * X[j]
            equ[i] = Eq(eq1, Z[i])
            eq1 = 0

        # Declare some symbols to solve the node equations
        R1, R2, R3 = symbols('R1 R2 R3')
        v1, v2, v3 = symbols('v1 v2 v3')
        Vb, Is, IVb = symbols('Vb Is IVb')

        # enter the element values
        equ1a = equ.subs({R1: 5})
        equ1a = equ1a.subs({R2: 3})
        equ1a = equ1a.subs({R3: 10})

        equ1a = equ1a.subs({Vb: 30})
        equ1a = equ1a.subs({Is: 2})

        equ1a.row_del(0)


        V1, V2, I_V1, I_V2 = symbols('V1 V2 I_V1 I_V2 ')

        Final_Sol = solve(equ, X)
        print('Solv ----- ',Final_Sol)
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
    n = NodeAnalysis('net_2.txt')
    #print(n.Y_matriz)