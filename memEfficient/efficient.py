import sys
import time
import psutil
import numpy as np

def stringgen(input_path):
    with open(input_path, "r") as f:
        data = f.readlines()

    s = data[0].strip()
    for i in range(1, len(data)):
        try:
            ni = int(data[i].strip())
            s = s[:ni+1]+ s + s[ni+1:]
        except:
            break
    
    t = data[i].strip()
    for j in range(i+1, len(data)):
        nj = int(data[j].strip())
        t = t[:nj+1]+ t + t[nj+1:]


    return s, t

# --- 1. CONFIGURATION (Matched to dp.py) ---
MAPPING = {"A": 0, "C": 1, "G": 2, "T": 3, "_": 4}
# Note: Added 4 for gaps, though mostly handled by logic
SCORE_MATRIX = np.array([
    [0, 110, 48, 94],
    [110, 0, 118, 48],
    [48, 118, 0, 110],
    [94, 48, 110, 0]
])
DELTA = 30

# --- 2. HELPERS (Adapted from dp.py) ---
def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss / 1024)
    return memory_consumed

def parse_string_to_indices(s):
    """Converts string 'ACGT' to numpy array [0, 1, 2, 3]"""
    return np.array([MAPPING[c] for c in s])

def parse_indices_to_string(indices):
    """Converts numpy array back to 'ACGT' string"""
    reverse_mapping = {v: k for k, v in MAPPING.items()}
    return ''.join([reverse_mapping[i] for i in indices])

# --- 3. ALGORITHM CORE ---

def get_dp_row(s_indices, t_indices):
    """
    Calculates only the last row of the DP table.
    Space: O(min(m, n))
    This is similar to your partner's memEfficientMinEdit but returns the whole row.
    """
    m = len(s_indices)
    n = len(t_indices)
    
    # Initialize previous row (Row 0)
    # prev_row[j] = j * DELTA
    prev_row = np.arange(n + 1) * DELTA
    curr_row = np.zeros(n + 1)

    for i in range(1, m + 1):
        curr_row[0] = i * DELTA
        for j in range(1, n + 1):
            cost_match = SCORE_MATRIX[s_indices[i-1]][t_indices[j-1]]
            
            # Standard recurrence: min(diagonal, up, left)
            curr_row[j] = min(
                prev_row[j-1] + cost_match, # Match/Mismatch
                prev_row[j] + DELTA,        # Gap in T
                curr_row[j-1] + DELTA       # Gap in S
            )
        
        # Update prev_row to be the current row for the next iteration
        # using np.copy to avoid reference issues
        prev_row = np.copy(curr_row)
        
    return prev_row

def hirschberg_recursive(s_indices, t_indices):
    """
    Recursive Divide and Conquer Algorithm.
    """
    m = len(s_indices)
    n = len(t_indices)

    # --- BASE CASE ---
    # If the problem is small, solve with standard alignment
    if m <= 2 or n <= 2:
        return basic_align_small(s_indices, t_indices)

    # --- DIVIDE ---
    mid = m // 2

    # 1. Score of Left Half (Forward)
    #    Align S[0..mid] vs T
    score_left = get_dp_row(s_indices[:mid], t_indices)

    # 2. Score of Right Half (Backward)
    #    Align S[mid..end] vs T (both reversed)
    score_right = get_dp_row(s_indices[mid:][::-1], t_indices[::-1])

    # 3. Find Optimal Split Point
    #    We sum the left score and the reversed right score.
    #    Note: score_right is from the perspective of the end, so we reverse it to match indices.
    split_index = np.argmin(score_left + score_right[::-1])

    # --- CONQUER ---
    # Recursively solve the two sub-problems
    res_left = hirschberg_recursive(s_indices[:mid], t_indices[:split_index])
    res_right = hirschberg_recursive(s_indices[mid:], t_indices[split_index:])

    # Combine results: (cost sum, string1 concat, string2 concat)
    return (
        res_left[0] + res_right[0],
        res_left[1] + res_right[1],
        res_left[2] + res_right[2]
    )

def basic_align_small(s_indices, t_indices):
    """
    Standard DP for small base cases in recursion.
    Returns (cost, aligned_s, aligned_t)
    """
    m = len(s_indices)
    n = len(t_indices)
    dp = np.zeros((m + 1, n + 1))

    # Init
    for i in range(m + 1): dp[i][0] = i * DELTA
    for j in range(n + 1): dp[0][j] = j * DELTA

    # Fill
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = min(
                dp[i-1][j-1] + SCORE_MATRIX[s_indices[i-1]][t_indices[j-1]],
                dp[i-1][j] + DELTA,
                dp[i][j-1] + DELTA
            )
    
    # Backtrack
    align_s = []
    align_t = []
    i, j = m, n
    while i > 0 or j > 0:
        curr = dp[i][j]
        if i > 0 and j > 0 and curr == dp[i-1][j-1] + SCORE_MATRIX[s_indices[i-1]][t_indices[j-1]]:
            align_s.append(s_indices[i-1])
            align_t.append(t_indices[j-1])
            i -= 1; j -= 1
        elif i > 0 and curr == dp[i-1][j] + DELTA:
            align_s.append(s_indices[i-1])
            align_t.append(MAPPING["_"]) # Gap
            i -= 1
        else:
            align_s.append(MAPPING["_"]) # Gap
            align_t.append(t_indices[j-1])
            j -= 1
            
    return (dp[m][n], align_s[::-1], align_t[::-1])

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 efficient.py <input_file> <output_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # 1. Generate Input Strings (Using shared utils)
    s_str, t_str = stringgen(input_path)
    
    # 2. Convert to Indices (Matches partner's efficiency)
    s_indices = parse_string_to_indices(s_str)
    t_indices = parse_string_to_indices(t_str)

    # 3. Start Tracking
    process = psutil.Process()
    start_time = time.time()
    start_mem = process_memory() # Initial memory

    # 4. Run Memory Efficient Algorithm
    final_cost, align_s_indices, align_t_indices = hirschberg_recursive(s_indices, t_indices)

    # 5. End Tracking
    end_time = time.time()
    end_mem = process_memory() # Peak memory check
    
    # 6. Convert result back to strings
    # Note: If the base cases returned lists of indices, we might need to flatten or join them.
    # The recursive function concatenates lists, so align_s_indices is a list of ints.
    final_s = parse_indices_to_string(align_s_indices)
    final_t = parse_indices_to_string(align_t_indices)

    time_taken = (end_time - start_time) * 1000
    mem_taken = end_mem - start_mem

    # 7. Write Output
    try:
        with open(output_path, 'w') as writer:
            writer.write(f"{int(final_cost)}\n")
            writer.write(f"{final_s}\n")
            writer.write(f"{final_t}\n")
            writer.write(f"{time_taken}\n")
            writer.write(f"{mem_taken}\n")
    except IOError as e:
        print(f"Error writing output: {e}", file=sys.stderr)
