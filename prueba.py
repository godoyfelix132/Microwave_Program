from sympy import *


def touchstone(Y_mat, init_f, end_f, Z0):
    mat = Y_mat

    file = open('touchs.s2p', 'w')

    if end_f/1e12 >= 1:
        freq_not = 'THZ'
        freq_div = 1e12
    elif end_f/1e9 >= 1:
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
    file.write('!\t\tFreq\t\t\t\tRes11\t\t\t\tIms11\t\t\t\tRes21\t\t\t\t')
    file.write('Ims21\t\t\t\tRes12\t\t\t\tIms12\t\t\t\tRes22\t\t\t\tIms22\n')
    file.write('!\t\t----\t\t\t\t-----\t\t\t\t-----\t\t\t\t-----\t\t\t\t-----')
    file.write('\t\t\t\t-----\t\t\t\t-----\t\t\t\t----- \t\t\t\t-----\n')
    for frec in range(init_f, end_f, int(((end_f/init_f)/100)*init_f)):
        file.write('\t' + '{0:.10f}'.format(frec/freq_div) + '\t\t')
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
                file.write('{0:.10f}'.format(re(temp_mat[j, i])) + '\t\t')
                file.write('{0:.10f}'.format(im(temp_mat[j, i])) + '\t\t')
        file.write('\n')
    file.close()
    print('Done')


f = symbols('f')
mat1 = Matrix([[12.566370616*I*f/(62.83185308*I*f + 20.0), -6.283185308*I*f/(62.83185308*I*f + 20.0)], [-6.283185308*I*f/(62.83185308*I*f + 20.0), (6.283185308*I*f + 1)/(62.83185308*I*f + 20.0)]])

touchstone(mat1, 1, 10, 50)
