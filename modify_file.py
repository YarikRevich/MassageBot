import os
import sys


def main(path_to_file, chosen_line, text, params):
    
    with open(path_to_file, "r") as file:
        
        all_lines = file.readlines()
        new_lines = []
        for index, line in enumerate(all_lines):
            if index == chosen_line:
                if "-h" in params:
                    separated_line = line.split("\t")
                    del separated_line[1]
                    separated_line.append(f"{text}\n")
                    new_line = "\t".join(separated_line)
                    new_lines.append(f"{line}{new_line}")
                else:
                    new_lines.append(f"{line}{text}\n")
            else:
                new_lines.append(line)
        
        with open(path_to_file, "w") as file:
            file.write("")
            
        with open(path_to_file, "a") as file:
            for line in new_lines:
                file.write(line)
    

if __name__ == "__main__":
    try:
        path = sys.argv[sys.argv.index("--file")+1]
    except (ValueError, IndexError):
        sys.exit("You have to pass path to file")
    try:
        chosen_index = int(sys.argv[sys.argv.index("--index")+1])
    except (ValueError, IndexError):
        sys.exit("You have to write chosen line for replacement")
    try:
        text = sys.argv[sys.argv.index("--text")+1]
    except (ValueError, IndexError):
        sys.exit("You have to pass text for replacement")
    params = []
    if "-h" in sys.argv:
        params.append("-h")
    main(path, chosen_index, text, params)