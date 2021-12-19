from src.adjacency_matrix import *


class Node:
    def __init__(self, index, lines, cords):
        self.index = index
        self.lines = lines
        self.cords = cords
        # print("id", self.index, "lines", self.lines, "cords", self.cords)
    @staticmethod
    def get_nodes(d):
        mat = AdjacencyMatrix(d)
        #print(mat.__repr__())
        lines = d.keys()
        skip = []
        n = [0]
        check = [0]
        invert = False
        nodes = []
        for i in lines:
            if i not in skip:
                check = [i]
                n = [i]
                for x in check:
                    for y in lines:
                        r = mat.areAdjacent(x, y)
                        if r:
                            if y not in n:
                                n.append(y)
                                check.append(y)
                    for y in lines:
                        r = mat.areAdjacent(y, x)
                        if r:
                            if y not in n:
                                n.append(y)
                                check.append(y)
                nodes.append(n)
                skip = skip + n
                # print(skip)
        dic_nodes = {}
        for i in range(len(nodes)):
            dic_nodes[i] = set(nodes[i])

        return dic_nodes





if __name__ == '__main__':
    d = {0: {0, 1}, 1: {0, 1}, 2: {2, 3, 7}, 3: {2, 3}, 4: {4, 5}, 5: {4, 5, 6}, 6: {5, 6}, 7: {2, 7}}
    d2 = {0: {0, 1, 5}, 1: {0, 1, 4, 5}, 2: {2, 3}, 3: {2, 3}, 4: {1, 4, 5}, 5: {0, 1, 4, 5}}
    Node.get_nodes(d2)
