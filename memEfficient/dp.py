from utils import stringgen
import numpy as np
import sys
import time
import psutil

MAPPING = {"A" : 0, "C" : 1, "G" : 2, "T" : 3, "_": "_"}
SCORE_MATRIX = np.array([[0,110,48,94],
                        [110,0,118,48],
                        [48,118,0,110],
                        [94,48,110,0]])
DELTA = 30

start_time = 0.0
end_time = 0.0
start_mem = 0.0
end_mem = 0.0

def process_memory(): 
    process = psutil.Process() 
    memory_info = process.memory_info() 
    memory_consumed = int(memory_info.rss/1024) 
    return memory_consumed 

def parse_string_to_indices(s):
    return np.array([MAPPING[c] for c in s])

def parse_indices_to_string(indices):
    reverse_mapping = {v: k for k, v in MAPPING.items()}
    return ''.join([reverse_mapping[i] for i in indices])

def vanillaMinEdit(s, t):
    global start_time, end_time, start_mem, end_mem

    s = parse_string_to_indices(s)
    t = parse_string_to_indices(t)

    start_time = time.time()
    start_mem = process_memory()

    work_table = np.zeros((len(s) + 1, len(t) + 1))

    for i in range(len(s) + 1):
        work_table[i][0] = i * DELTA
    for j in range(len(t) + 1):
        work_table[0][j] = j * DELTA

    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            work_table[i][j] = min(
                work_table[i-1][j-1] + SCORE_MATRIX[s[i-1]][t[j-1]],
                work_table[i-1][j] + DELTA,
                work_table[i][j-1] + DELTA
            )

    end_time = time.time()
    end_mem = process_memory()

    return work_table[len(s)][len(t)], work_table

def memEfficientMinEdit(s, t):
    s = parse_string_to_indices(s)
    t = parse_string_to_indices(t)

    work_table = np.zeros((2, len(t) + 1))

    for j in range(len(t) + 1):
        work_table[0][j] = j * DELTA


    for i in range(1, len(s) + 1):
        row_index = i % 2
        work_table[row_index][0] = i * DELTA
        prev_row_index = (i - 1) % 2
        for j in range(1, len(t) + 1):
            work_table[row_index][j] = min(
                work_table[prev_row_index][j-1] + SCORE_MATRIX[s[i-1]][t[j-1]],
                work_table[prev_row_index][j] + DELTA,
                work_table[row_index][j-1] + DELTA
            )
    return work_table[0][len(t)]

def backtrack(worktable, s, t):
    s = parse_string_to_indices(s)
    t = parse_string_to_indices(t)
    score = worktable[len(s)][len(t)]

    i = len(s)
    j = len(t)

    aligned_s = []
    aligned_t = []

    while i > 0 or j > 0:
        current_score = worktable[i][j]

        if i > 0 and j > 0 and current_score == worktable[i-1][j-1] + SCORE_MATRIX[s[i-1]][t[j-1]]:
            aligned_s += [s[i-1]]
            aligned_t += [t[j-1]]
            i -= 1
            j -= 1
        elif i > 0 and current_score == worktable[i-1][j] + DELTA:
            aligned_s += [s[i-1]]
            aligned_t += ['_']
            i -= 1
        else:
            aligned_s += ['_']
            aligned_t += [t[j-1]]
            j -= 1
    aligned_s.reverse()
    aligned_t.reverse()

    aligned_s = parse_indices_to_string(aligned_s)
    aligned_t = parse_indices_to_string(aligned_t)

    return score, ''.join(aligned_s), ''.join(aligned_t)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sequence_aligner.py <input_file> <output_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]


    s, t = stringgen(input_path)
    result, wt = vanillaMinEdit(s, t)
    # print("vanilla min edit : ", result)

    # result_mem_efficient = memEfficientMinEdit(s, t)
    # print("mem efficient min edit : ", result_mem_efficient)

    score, aligned_s, aligned_t = backtrack(wt, s, t)
    # print("Backtracked alignment score: ", score)
    # print("Aligned String S: ", aligned_s)
    # print("Aligned String T: ", aligned_t)

    time_taken = (end_time - start_time) * 1000 
    mem_taken = end_mem - start_mem

    try:
        with open(output_path, 'w') as writer:
            writer.write(f"{score}\n")
            writer.write(f"{aligned_s}\n")
            writer.write(f"{aligned_t}\n")
            writer.write(f"{time_taken}\n")
            writer.write(f"{mem_taken}")
    except IOError as e:
        print(f"Error writing output: {e}", file=sys.stderr)    


