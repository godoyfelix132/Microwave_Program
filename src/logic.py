from PySide2 import QtWidgets
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide2.QtGui import QIcon
from src.form import Ui_MainWindow
from src.root import *
from sympy import *
from decimal import Decimal
from src.node_analysis import *
from pylab import *
import skrf as rf
from skrf import Network, Frequency
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import threading
import re
import cmath
import os
from src.main_window import *

f = symbols('f')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("rsc/icon4.png"))
        pixmap_mex = QtGui.QPixmap('rsc/mex.png')
        pixmap_cinv = QtGui.QPixmap('rsc/cinv5.png')
        self.ui.label_mex.setPixmap(pixmap_mex)
        self.ui.label_cinv.setPixmap(pixmap_cinv)
        self.ui.pushButton_abrir_netlist.clicked.connect(self.get_root_netlist)
        # self.ui.pushButton_calcular_valores.clicked.connect(self.get_parameter)
        self.ui.pushButton_crear_touchstone.clicked.connect(self.create_touchstone)
        self.ui.pushButton_evaluar.clicked.connect(self.evaluate)
        self.ui.pushButton_graficar_1.clicked.connect(self.graph_1)
        self.ui.pushButton_abrir_touchstone.clicked.connect(self.get_root_touchstone)
        self.ui.pushButton_crear_netlist.clicked.connect(self.create_thread)
        self.ui.pushButton_graficar_2.clicked.connect(self.graph_2)
        self.root_netlist = Root('','')
        self.root_touchstone_r = Root('','')
        # self.y_function = Matrix([[12.566370616*I*f/(62.83185308*I*f + 20.0), -6.283185308*I*f/(62.83185308*I*f + 20.0)], [-6.283185308*I*f/(62.83185308*I*f + 20.0), (6.283185308*I*f + 1)/(62.83185308*I*f + 20.0)]])
        self.y_function = Matrix([[1,1],[1,1]])
        #ntw = rf.Network(frequency='', s=[[[0],[0]],[[0],[0]]])
        self.ntw_touchstone = ''

    def create_thread(self):
        t = threading.Thread(target=self.new_circuit_creator())
        file = open('net.txt', 'w')
        file.write('')
        file.close()
        t.start()

    def new_circuit_creator(self):
        pygame.init()
        screen = pygame.display.set_mode(SIZE)
        a = pygame.image.load('rsc/icon4.png')
        pygame.display.set_icon(a)
        pygame.display.set_caption('Parameters')
        clock = pygame.time.Clock()
        app = App()
        done = False
        while not done:
            done = app.process_events
            execute = app.execute
            if execute:
                app.execute = False
                try:
                    self.get_matrix_from_net()
                except:
                    self.ui.plainTextEdit_mostrar_netlist.setPlainText('Circuito no valido')
            app.run_logic()
            app.display_frame(screen)
            clock.tick(60)
        pygame.quit()
        #pass

    def get_matrix_from_net(self):
        root = os.path.abspath("net.txt")
        self.root_netlist = Root(root, 'netlist')
        self.ui.lineEdit_nombre_netlist.setText(self.root_netlist.file_name)
        file = open('net.txt', 'r')
        txt = file.read()
        self.ui.plainTextEdit_mostrar_netlist.setPlainText(txt)
        n = NodeAnalysis(root)
        self.y_function = n.Y_matriz

    def graph_2(self):
        flag = True
        vector_check = [int(self.ui.checkBox_11_touch.isChecked()),int(self.ui.checkBox_12_touch.isChecked()),int(self.ui.checkBox_21_touch.isChecked()),int(self.ui.checkBox_22_touch.isChecked())]
        if vector_check != [0, 0, 0, 0]:
            graph = 1
        if self.ui.comboBox_grafica_2.currentText() == 'Carta de Smith':
            graph = 1
        if self.ui.comboBox_grafica_2.currentText() == 'Magnitud':
            graph = 2
        if self.ui.comboBox_grafica_2.currentText() == 'Fase':
            graph = 3
        parameter = 1
        z0 = float(self.ui.lineEdit_z0_touch.text())
        e_init = self.ui.comboBox_unidad_f1_touch.currentText()
        e_init = self.get_exponent(e_init)
        f_init = int(self.ui.lineEdit_frecuencia_inicial_touch.text()) * e_init
        e_end = self.ui.comboBox_unidad_f2.currentText()
        e_end = self.get_exponent(e_end)
        f_end = int(self.ui.lineEdit_frecuencia_final.text()) * e_end
        if flag:
            ntw = self.ntw_touchstone
            self.graficar(parameter,vector_check,graph,ntw)

    def graph_1(self):
        flag = True
        vector_check = [int(self.ui.checkBox_11_parameter.isChecked()),int(self.ui.checkBox_12_parameter.isChecked()),int(self.ui.checkBox_21_parameter.isChecked()),int(self.ui.checkBox_22_parameter.isChecked())]
        if vector_check != [0, 0, 0, 0]:
            print(vector_check)
        graph = 1
        if self.ui.comboBox_grafica_1.currentText() == 'Carta de Smith':
            graph = 1
        if self.ui.comboBox_grafica_1.currentText() == 'Magnitud':
            graph = 2
        if self.ui.comboBox_grafica_1.currentText() == 'Fase':
            graph = 3
        parameter = 1
        z0 = float(self.ui.lineEdit_z0.text())
        if self.ui.comboBox_parametros.currentText() == 'S':
            z0 = 1
            parameter = 1
        if self.ui.comboBox_parametros.currentText() == 'Y':
            if graph==1:
                z0 =z0
            else:
                z0 = 1
            parameter = 2
        if self.ui.comboBox_parametros.currentText() == 'Z':
            if graph==1:
                z0 = 1/z0
            else:
                z0 = 1
            parameter = 3
        if self.ui.comboBox_parametros.currentText() == 'ABCD':
            flag = False
            parameter = 4
        if self.ui.comboBox_parametros.currentText() == 'T':
            flag = False
            parameter = 5
        e_init = self.ui.comboBox_unidad_f1.currentText()
        e_init = self.get_exponent(e_init)
        f_init = int(self.ui.lineEdit_frecuencia_inicial.text()) * e_init
        e_end = self.ui.comboBox_unidad_f2.currentText()
        e_end = self.get_exponent(e_end)
        f_end = int(self.ui.lineEdit_frecuencia_final.text()) * e_end
        if flag:
            ntw = self.vectores(self.y_function, f_init, f_end,z0,parameter)
            self.graficar(parameter,vector_check,graph,ntw)

    def vectores(self, Y_mat, init_f, end_f, z0, parameter):
        points = self.ui.lineEdit_points.text()
        ff = np.logspace(log10(init_f), log10(end_f), int(points))
        freq=[]
        p11 = []
        p12 = []
        p21 = []
        p22 = []
        z0_ = float(self.ui.lineEdit_z0.text())
        for frec in ff:
            temp_mat = simplify(Y_mat.subs({f: frec}))
            if parameter != 2:  # Y
                if parameter == 1: #s
                    temp_mat = self.Y2S(temp_mat,z0_)
                if parameter == 3:#Z
                    temp_mat = self.Y2Z(temp_mat)
            freq.append(frec)
            p11.append(complex(temp_mat[0, 0])*z0)
            p12.append(complex(temp_mat[0, 1])*z0)
            p21.append(complex(temp_mat[1, 0])*z0)
            p22.append(complex(temp_mat[1, 1])*z0)
        freq2 = rf.Frequency.from_f(freq, unit='GHz')
        ##Crear matriz s
        s = rand(len(freq), 2, 2) + 1j * rand(len(freq), 2, 2)
        s[:, 0, 0] = p11
        s[:, 0, 1] = p12
        s[:, 1, 0] = p21
        s[:, 1, 1] = p22

        #for i in p11:
            #print(freq,i)
        ntw = rf.Network(frequency=freq2, s=s)
        return ntw

    def create_touchstone(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save As", '')
        if file_name:
            e_init = self.ui.comboBox_unidad_f1_touch.currentText()
            e_init = self.get_exponent(e_init)
            f_init = int(self.ui.lineEdit_frecuencia_inicial_touch.text()) * e_init
            e_end = self.ui.comboBox_unidad_f2_touch.currentText()
            e_end = self.get_exponent(e_end)
            f_end = int(self.ui.lineEdit_frecuencia_final_touch.text()) * e_end
            z0 = self.ui.lineEdit_z0_touch.text()
            self.write_touchstone(self.y_function, f_init, f_end, int(z0), file_name)

    def Y2Z(self, y):
        z = simplify(y.inv())
        return z

    def Y2ABCD(self, y):
        dety = y[1,1]*y[0,0]-y[1,0]*y[0,1]
        a = -1 * y[1, 1] / y[1, 0]
        b = -1 * (1 / y[1, 0])
        c = -1 * dety / y[1, 0]
        d = -1 * y[0, 0] / y[1, 0]
        abcd = Matrix([[a, b], [c, d]])
        return abcd

    def Y2S(self, y, z0):
        Norm_Yparam = y * z0
        Den = (1 + Norm_Yparam[0, 0]) * (1 + Norm_Yparam[1, 1]) - (Norm_Yparam[0, 1] * Norm_Yparam[1, 0])
        S11 = ((1 - Norm_Yparam[0, 0]) * (1 + Norm_Yparam[1, 1]) + (Norm_Yparam[0, 1] * Norm_Yparam[1, 0])) / Den
        S12 = -2 * Norm_Yparam[0, 1] / Den
        S21 = -2 * Norm_Yparam[1, 0] / Den
        S22 = ((1 + Norm_Yparam[0, 0]) * (1 - Norm_Yparam[1, 1]) + (Norm_Yparam[0, 1] * Norm_Yparam[1, 0])) / Den
        s = Matrix([[S11, S12], [S21, S22]])
        return s

    def S2T(self, s):
        den = 1 / (s[1, 0])
        t11 = -(s[0, 0] * s[1, 1] - s[1, 0] * s[1, 0]) * den
        t12 = s[0, 0] * den
        t21 = -1 * s[1, 1] * den
        t22 = den
        t = Matrix([[t11, t12], [t21, t22]])
        return t

    def evaluate(self):
        e_eval = self.ui.comboBox_unidad_f3.currentText()
        e_eval = self.get_exponent(e_eval)
        f_eval = int(self.ui.lineEdit_frecuencia_evaluar.text()) * e_eval
        mat = simplify(self.y_function.subs({f: f_eval}))
        parameter = self.ui.comboBox_parametros.currentText()
        error = False
        if parameter != 'Y':
            if parameter == 'Z':
                try:
                    mat = self.Y2Z(mat)
                except:
                    error = True
            if parameter == 'ABCD':
                try:
                    mat = self.Y2ABCD(mat)
                except:
                    error = True
            if parameter == 'S' or parameter == 'T':
                try:
                    z0 = self.ui.lineEdit_z0.text()
                    mat = self.Y2S(mat, int(z0))
                    if parameter == 'S':
                        print('s')
                        pass
                    else:
                        print('t')
                        mat = self.S2T(mat)
                except:
                    error = True
        #print(mat)

        x11 = '%.4E' % Decimal(str((complex(mat[0, 0])).real))
        x12 = '%.4E' % Decimal(str((complex(mat[0, 1])).real))
        x21 = '%.4E' % Decimal(str((complex(mat[1, 0])).real))
        x22 = '%.4E' % Decimal(str((complex(mat[1, 1])).real))

        x11_i = '%.4E' % Decimal(str((complex(mat[0, 0])).imag))
        x12_i = '%.4E' % Decimal(str((complex(mat[0, 1])).imag))
        x21_i = '%.4E' % Decimal(str((complex(mat[1, 0])).imag))
        x22_i = '%.4E' % Decimal(str((complex(mat[1, 1])).imag))

        if not error:
            self.ui.lineEdit_real_1.setText(str(x11))
            self.ui.lineEdit_real_2.setText(str(x12))
            self.ui.lineEdit_real_3.setText(str(x21))
            self.ui.lineEdit_real_4.setText(str(x22))

            self.ui.lineEdit_imaginario_1.setText(str(x11_i))
            self.ui.lineEdit_imaginario_2.setText(str(x12_i))
            self.ui.lineEdit_imaginario_3.setText(str(x21_i))
            self.ui.lineEdit_imaginario_4.setText(str(x22_i))
        else:
            self.ui.lineEdit_real_1.setText('No disponible')
            self.ui.lineEdit_real_2.setText('No disponible')
            self.ui.lineEdit_real_3.setText('No disponible')
            self.ui.lineEdit_real_4.setText('No disponible')

            self.ui.lineEdit_imaginario_1.setText('No disponible')
            self.ui.lineEdit_imaginario_2.setText('No disponible')
            self.ui.lineEdit_imaginario_3.setText('No disponible')
            self.ui.lineEdit_imaginario_4.setText('No disponible')


    def get_exponent(self, exp):
        if exp == 'Hz':
            return 1
        if exp == 'KHz':
            return 10**3
        if exp == 'MHz':
            return 10**6
        if exp == 'GHz':
            return 10**9


    def get_parameter(self):
        e_init = self.ui.comboBox_unidad_f1.currentText()
        e_init = self.get_exponent(e_init)
        f_init = int(self.ui.lineEdit_frecuencia_inicial.text()) * e_init
        e_end = self.ui.comboBox_unidad_f2.currentText()
        e_end = self.get_exponent(e_end)
        f_end = int(self.ui.lineEdit_frecuencia_final.text()) * e_end
        z0 = self.ui.lineEdit_z0.text()
        parameter = self.ui.comboBox_parametros.currentText()

    def get_root_netlist(self):
        options = QtWidgets.QFileDialog.Options()
        root, f = QtWidgets.QFileDialog.getOpenFileName(self,"","","(*.txt)", "", options)
        if root:
            self.root_netlist = Root(root, 'netlist')
            self.ui.lineEdit_nombre_netlist.setText(self.root_netlist.file_name)
            file = open(self.root_netlist.root, 'r')
            text = file.read()
            self.ui.plainTextEdit_mostrar_netlist.setPlainText(text)
            n = NodeAnalysis(root)
            self.y_function = n.Y_matriz
            print(self.y_function)




    def get_root_touchstone(self):
        options = QtWidgets.QFileDialog.Options()
        root, f = QtWidgets.QFileDialog.getOpenFileName(self,"","","(*.s2p)", "", options)
        if root:
            self.root_touchstone_r = Root(root, 'touchstone_r')
            self.ui.lineEdit_nombre_touchstone.setText(self.root_touchstone_r.file_name)
            self.read_touchstone(self.root_touchstone_r.root)

    def read_touchstone(self,fn):
        fd1 = open(fn , 'r')
        content = fd1.readlines()
        content = [x.strip() for x in content]  # remove leading and trailing white space
        # remove empty lines
        while '' in content:
            content.pop(content.index(''))

        # remove comment lines, these start with !
        content = [n for n in content if not n.startswith('!')]
        # removes extra spaces between entries
        content = [' '.join(x.split()) for x in content]

        line_cnt = len(content)  # number of lines

        Par0 = content[0].split()[1]  # Frequency exponent
        Par1 = content[0].split()[2]  # Parameter type
        Par2 = content[0].split()[3]  # Real-Imaginary or Magnitude and Angle
        Par3 = content[0].split()[5]  # Z0

        if Par0 == 'THZ':
            freq_mul = 1e12
        elif Par0 == 'GHZ':
            freq_mul = 1e9
        elif Par0 == 'MHZ':
            freq_mul = 1e6
        elif Par0 == 'KHZ':
            freq_mul = 1e3
        else:
            freq_mul = 1

        Freq = []
        P11r = []
        P12r = []
        P21r = []
        P22r = []
        P11i = []
        P12i = []
        P21i = []
        P22i = []

        content = [n for n in content if not n.startswith('#')]  # Erase the description line

        for i in range(line_cnt - 1):
            Freq.append(float(content[i].split()[0]) * freq_mul)
            P11r.append(float(content[i].split()[1]))
            P11i.append(float(content[i].split()[2]))
            P21r.append(float(content[i].split()[3]))
            P21i.append(float(content[i].split()[4]))
            P12r.append(float(content[i].split()[5]))
            P12i.append(float(content[i].split()[6]))
            P22r.append(float(content[i].split()[7]))
            P22i.append(float(content[i].split()[8]))

        P11 = [complex(0, 0)] * (line_cnt - 1)
        P12 = [complex(0, 0)] * (line_cnt - 1)
        P21 = [complex(0, 0)] * (line_cnt - 1)
        P22 = [complex(0, 0)] * (line_cnt - 1)
        fd1.close()

        if Par2 == 'RI':
            for d in range(line_cnt - 1):
                P11[d] = ((P11r[d]) + (P11i[d] * 1j))
                P12[d] = ((P12r[d]) + (P12i[d] * 1j))
                P21[d] = ((P21r[d]) + (P21i[d] * 1j))
                P22[d] = ((P22r[d]) + (P22i[d] * 1j))

        elif Par2 == 'MA':
            for d in range(line_cnt - 1):
                P11[d] = P11r[d] * math.cos(math.radians(P11i[d])) + P11r[d] * math.sin(math.radians(P11i[d])) * 1j
                P12[d] = P12r[d] * math.cos(math.radians(P12i[d])) + P12r[d] * math.sin(math.radians(P12i[d])) * 1j
                P21[d] = P21r[d] * math.cos(math.radians(P21i[d])) + P21r[d] * math.sin(math.radians(P21i[d])) * 1j
                P22[d] = P22r[d] * math.cos(math.radians(P22i[d])) + P22r[d] * math.sin(math.radians(P22i[d])) * 1j

        t1 = ("Parámetros: " + Par1)
        t2 = ("Rango de frecuencia: " + str(Freq[0]) + " a " + str(Freq[line_cnt - 2]) + Par0)
        t3 = ("Z0: " + Par3)
        t4 = ("Número de mediciones: " + str(line_cnt - 1))
        self.ui.plainTextEdit_mostrar_touchstone.setPlainText(t1 + '\n' + t2 + '\n' + t3 + '\n' + t4)


        freq2 = rf.Frequency.from_f(Freq, unit=Par0)

        ##Crear matriz s
        s = rand(len(Freq), 2, 2) + 1j * rand(len(Freq), 2, 2)
        s[:, 0, 0] = P11
        s[:, 0, 1] = P12
        s[:, 1, 0] = P21
        s[:, 1, 1] = P22
        ntw = rf.Network(frequency=freq2, s=s)
        self.ntw_touchstone = ntw


    def write_touchstone(self, Y_mat, init_f, end_f, Z0, file_name):
        points = self.ui.lineEdit_points_touch.text()
        ff = np.logspace(log10(init_f), log10(end_f), int(points))
        mat = Y_mat
        file = open(file_name, 'w')
        if end_f / 1e12 >= 1:
            freq_not = 'THZ'
            freq_div = 1e12
        elif end_f / 1e9 >= 1:
            freq_not = 'GHZ'
            freq_div = 1e9
        elif end_f / 1e6 >= 1:
            freq_not = 'MHZ'
            freq_div = 1e6
        elif end_f / 1e3 >= 1:
            freq_not = 'KHZ'
            freq_div = 1e3
        else:
            freq_not = 'HZ'
            freq_div = 1

        file.write('! Cinvestav GDL Microondas I \n! \n')
        file.write('# ' + freq_not + '  S  RI  R  ' + str(Z0) + '\n! \n')
        file.write('!\tFreq\t\t\tRes11\t\t\tIms11\t\t\tRes21\t\t\t')
        file.write('Ims21\t\t\tRes12\t\t\tIms12\t\t\tRes22\t\t\tIms22\n')
        file.write('!\t\t----\t\t\t\t-----\t\t\t\t-----\t\t\t\t-----\t\t\t\t-----')
        file.write('\t\t\t\t-----\t\t\t\t-----\t\t\t\t----- \t\t\t\t-----\n')
        # for frec in range(init_f, end_f, 1):
        for frec in ff:
            file.write('\t' + '{0:.10f}'.format(frec / freq_div) + '\t\t')
            temp_mat = mat.subs({f: frec})

            Norm_Yparam = temp_mat * Z0
            Den = (1 + Norm_Yparam[0, 0]) * (1 + Norm_Yparam[1, 1]) - (Norm_Yparam[0, 1] * Norm_Yparam[1, 0])
            S11 = ((1 - Norm_Yparam[0, 0]) * (1 + Norm_Yparam[1, 1]) + (Norm_Yparam[0, 1] * Norm_Yparam[1, 0])) / Den
            S12 = -2 * Norm_Yparam[0, 1] / Den
            S21 = -2 * Norm_Yparam[1, 0] / Den
            S22 = ((1 + Norm_Yparam[0, 0]) * (1 - Norm_Yparam[1, 1]) + (Norm_Yparam[0, 1] * Norm_Yparam[1, 0])) / Den
            temp_mat = Matrix([[S11, S12], [S21, S22]])

            for i in range(2):
                for j in range(2):
                    file.write('{0:.10f}'.format(complex(temp_mat[j, i]).real) + '\t\t')
                    file.write('{0:.10f}'.format(complex(temp_mat[j, i]).imag) + '\t\t')
            file.write('\n')
        file.close()

    def graficar(self, parametro, parametros_elegidos, grafica, ntw):
        parametros = ['s', 'y', 'z', 'abcd', 't']
        graficas = ['plot_s_smith', 'plot_s_db', 'plot_s_deg']
        numeros_t = ['11', '12', '21', '22']
        colores_t = ['magenta', 'red', 'pink', 'orange']
        numeros_m = [['11', '12'], ['21', '22']]
        colores_m = [['magenta', 'red'], ['pink', 'orange']]
        Suma = 0
        numeros = []
        colores = []
        for i in range(0, 4):
            Suma = Suma + parametros_elegidos[i]
            if parametros_elegidos[i] == 1:
                numeros.append(numeros_t[i])
                colores.append(colores_t[i])
        if Suma == 1:
            exec("ntw.s%s.%s(color='%s',label='%s%s')" % (
                numeros[0], graficas[grafica - 1], colores[0], parametros[parametro - 1], numeros[0]))
        if Suma == 2 or Suma == 3:
            exec("fig, axes = plt.subplots(1,%i, sharex=True, figsize=(%i,6))" % (Suma, 5 * Suma))
            for i in range(0, Suma):
                exec("ntw.s%s.%s(ax=axes[i], color='%s',label='%s%s')" % (
                numeros[i], graficas[grafica - 1], colores[i], parametros[parametro - 1], numeros[i]))
            exec("fig.tight_layout()")
            plt.subplots_adjust(top=0.9)
        if Suma == 4:
            exec("fig, axes = plt.subplots(2,2, sharex=True, figsize=(14,6))")
            for i in range(0, 2):
                for j in range(0, 2):
                    exec("ntw.s%s.%s(ax=axes[i][j], color='%s',label='%s%s')" % (
                    numeros_m[i][j], graficas[grafica - 1], colores_m[i][j], parametros[parametro - 1],
                    numeros_m[i][j]))
            exec("fig.tight_layout()")
            plt.subplots_adjust(top=0.9)
        plt.show()