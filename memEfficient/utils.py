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