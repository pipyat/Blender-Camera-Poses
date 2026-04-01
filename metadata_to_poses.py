import ast

def parse_calibration_file(file_path):
    location = None
    orientation_matrix = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("location:"):
                # Extract the part after "location: "
                loc_str = line.split("location:")[1].strip()
                location = ast.literal_eval(loc_str)
            elif line.startswith("orientation_matrix:"):
                # Extract the matrix string across multiple lines
                matrix_lines = []
                # The first line contains "[[ ... ],"
                matrix_lines.append(line.split("orientation_matrix:")[1].strip())
                while not matrix_lines[-1].endswith("]]"):
                    next_line = f.readline().strip()
                    matrix_lines.append(next_line)
                # Join all lines and evaluate
                matrix_str = " ".join(matrix_lines)
                #print(matrix_str)
                orientation_matrix = ast.literal_eval(matrix_str)

    return np.asarray(location), np.asarray(orientation_matrix)
