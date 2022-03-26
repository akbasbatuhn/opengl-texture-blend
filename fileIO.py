
from vector import *

class FileIO:

    @staticmethod
    def read_file(fileName) -> (tuple):
        faces = []  # it will returned
        vertices = []  # it will returned
        text_coords = []
        vector_normals = []

        name_list = fileName.split(".")
        name = name_list[0]

        try:
            f = open(fileName)
            for line in f:
                if line[:2] == "v ":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)
                    index3 = line.find(" ", index2 + 1)

                    vertex = (float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1]))
                    vertex = (round(vertex[0], 2), round(vertex[1], 2), round(vertex[2], 2))
                    new_vertex = Point3f(vertex[0], vertex[1], vertex[2])
                    vertices.append(new_vertex)

                elif line[:2] == "vt":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)

                    textr = (float(line[index1:index2]), float(line[index2:-1]))
                    text_coords.append(textr)

                elif line[:2] == "vn":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)
                    index3 = line.find(" ", index2 + 1)

                    norml = (Point3f(float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1])))
                    vector_normals.append(norml)

                elif line[0] == "f":
                    temp = []

                    string = line.split(" ")
                    for i in range(len(string)):
                        if string[i] != "f":
                            temp_list = string[i].split("/")
                            temp_int = [int(num) - 1 for num in temp_list]
                            temp.append(temp_int)

                    faces.append(temp)
            f.close()

        except IOError:
            print(".obj file not found.")

        result = (name, vertices, faces, text_coords, vector_normals)
        return result

    @staticmethod
    def read_shader_file(file_name):
        try:
            f = open(file_name)
            temp_str = f.read()
            f.close()
            return temp_str
        except IOError:
            print("File not exist!")

