import os


class Root:
    def __init__(self, root, file_type):
        self.root = root
        self.path, self.file_name = os.path.split(root)
        self.file_type = file_type