import pickle
import glob
import shutil

def dict_append(dict, dict1):
    for i, j in dict.items():
        dict[i] += dict1[i]
    return dict

main = {"pickle": [], "encodings": [], 'names': []}

print("[INFO] merging encodings...")

for i in glob.glob("../dataset/pickles/*.pickle"):
    data = pickle.loads(open(i, "rb").read())
    data['pickle'] = [i]
    dict_append(main,data)


print("[INFO] encodings merged.")
f = open("encodings.pickle", "wb")
f.write(pickle.dumps(main))
f.close()
