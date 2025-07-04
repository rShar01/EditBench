import numpy as np

INPUT_FILE_PATH = './example_in.txt'

def main():
    lines = parse_input_file()
    print("Input lines:", lines)
    # Remove any empty lines that might be present
    lines = [line for line in lines if line.strip()]
    
    # Split each line by three spaces and convert each element to an integer
    cols = [list(map(int, line.split("   "))) for line in lines]
    # Transpose the list so that we have two lists corresponding to the two columns
    cols = np.array(cols).T
    
    # Instead of repeatedly finding and popping the minimum, sort both columns first.
    # Pairing the smallest with the smallest minimizes the sum of absolute differences.
    sorted_list_1 = sorted(cols[0])
    sorted_list_2 = sorted(cols[1])
    
    # Compute the total absolute difference between corresponding elements.
    total_difference = sum(abs(a - b) for a, b in zip(sorted_list_1, sorted_list_2))
    print(total_difference)

def parse_input_file():
    with open(INPUT_FILE_PATH, 'r') as f:
        lines = f.read().split("\n")
    return lines

if __name__ == "__main__":
    main()
