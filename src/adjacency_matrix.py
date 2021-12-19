class AdjacencyMatrix():
    def __init__(self, adjacencyList, label=""):
        self.matrix = []
        self.label = label
        # create an empty matrix
        for i in range(len(adjacencyList.keys())):
            self.matrix.append([0] * (len(adjacencyList.keys())))
        for key in adjacencyList.keys():
            for value in adjacencyList[key]:
                self[key][value] = 1
    def __str__(self):
        # return self.__repr__() is another possibility that just print the list of list
        # see python doc about difference between __str__ and __repr__
        # label first line
        string = self.label + "\t"
        for i in range(len(self.matrix)):
            string += str(i) + "\t"
        string += "\n"
        # for each matrix line :
        for row in range(len(self.matrix)):
            string += str(row) + "\t"
            for column in range(len(self.matrix)):
                string += str(self[row][column]) + "\t"
            string += "\n"
        return string

    def __repr__(self):
        return self.matrix

    def __getitem__(self, index):
        """ Allow to access matrix element using matrix[index][index] syntax """
        return self.matrix.__getitem__(index)

    def __setitem__(self, index, item):
        """ Allow to set matrix element using matrix[index][index] = value syntax """
        return self.matrix.__setitem__(index, item)

    def areAdjacent(self, i, j):
        return self[i][j] == 1