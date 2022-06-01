from typing import List, Tuple
import pandas as pd
import argparse
from datetime import datetime

import os
import tempfile
# from src.logger import *


def generate_dat(df: pd.DataFrame, tmp: tempfile.TemporaryDirectory):
    dat_path = os.path.join(tmp, "data.dat")
    out_str = " ".join(df.columns) + "\n"
    card = df.apply(pd.Series.nunique)
    out_str += " ".join([str(card[col]) for col in df.columns]) + "\n"
    for index, row in df.iterrows():
        out_str += " ".join([str(row[col]) for col in df.columns]) + "\n"
    with open(dat_path, "w") as f:
        f.write(out_str)


def parent_set_iden(tmp: tempfile.TemporaryDirectory):
    # java -jar blip.jar scorer.is -d data/child-5000.dat -j data/child-5000.jkl -t 10 -b 0
    dat_path = os.path.join(tmp, f"data.dat")
    jkl_path = os.path.join(tmp, f"parent_set.jkl")

    os.system(
        f"java -Xmx200G -jar blip.jar scorer.is -d {dat_path} -j {jkl_path} -t {TIMEOUT1} -b 0")

    if not os.path.exists(jkl_path):
        print("failed")


def general_struc_opt(tmp: tempfile.TemporaryDirectory):
    # java -jar blip.jar solver.winasobs.adv -smp ent -d data/child-5000.dat -j data/child-5000.jkl -r data/child.wa.res -t 10 -b 0

    dat_path = os.path.join(tmp, f"data.dat")
    jkl_path = os.path.join(tmp, f"parent_set.jkl")
    res_path = os.path.join(tmp, f"graph.res")

    os.system(
        f"java -Xmx200G -jar blip.jar solver.winasobs.adv -smp ent  -d {dat_path} -j {jkl_path} -r {res_path} -t {TIMEOUT2} -b 0")

    if not os.path.exists(res_path):
        print("failed")


def parse_res_file(col_names: List[str], tmp: tempfile.TemporaryDirectory) -> List[Tuple[str, str]]:
    res_path = os.path.join(tmp, f"graph.res")
    with open(res_path) as f:
        lines = [l.strip() for l in f.readlines()
                 if not l.startswith("Score") and l.strip() != ""]
    skeleton = []
    for line in lines:
        if "(" not in line:
            continue
        child = col_names[int(line.split(":")[0].strip())]
        start_idx = line.index("(") + 1
        end_idx = line.index(")")
        parent_raw = line[start_idx: end_idx].split(",")
        for p in parent_raw:
            parent = col_names[int(p)]
            skeleton.append((child, parent))
    return skeleton


def skeleton_learning(args, df: pd.DataFrame, is_small: bool = False) -> List[Tuple[str, str]]:
    global TIMEOUT1, TIMEOUT2
    if is_small:
        TIMEOUT1 = 300
        TIMEOUT2 = 60
    else:
        TIMEOUT1 = 1000  # important
        TIMEOUT2 = 1500
    # with tempfile.TemporaryDirectory() as tmp:
    #     # logging.info("LEARNING SKELETON [BLIP]")
    #     generate_dat(df, tmp)
    #     parent_set_iden(tmp)
    #     general_struc_opt(tmp)
    #     skl = parse_res_file(df.columns, tmp)

    tmp=os.path.join(os.getcwd(), 'data', args.tmp_out)
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    generate_dat(df, tmp)
    parent_set_iden(tmp)
    general_struc_opt(tmp)
    skl = parse_res_file(df.columns, tmp)
    return skl


if __name__ == "__main__":
    start_time = datetime.now()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", "-d", type=str, default="blip.csv")
    parser.add_argument("--est_out", "-e", type=str, default="blip_est.txt")
    parser.add_argument("--tmp_out", "-t", type=str, default="tmp_data")
    args = parser.parse_args()

    df = pd.read_csv(args.dataset, sep=",")
    skl = skeleton_learning(args, df)
    # write skl to text
    with open(args.est_out, "w") as f:
        for s in skl:
            f.write(f"{s[1]} -> {s[0]};\n")

    # print("original :")
    # print(skl)
    print("Done!")
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
