# -*- coding: utf-8 -*-
import time

from tqdm import tqdm

from com_lib.file_functions import open_csv
from com_lib.file_functions import save_json
from com_lib.reg_functions.patterns import pattern_between
from com_lib.reg_functions.patterns import pattern_between_two_char


def run_ascii():
    char_list = []
    char_list_csv = open_csv("ascii2.csv")

    for c in char_list_csv:
        char = c["Symbol"]
        if char.isprintable() == True:
            char_list.append(char)

    err_list = []
    count = 0

    for l in tqdm(char_list, desc="left char", leave=False, ascii=True):
        for r in tqdm(char_list, desc="right char", leave=False, ascii=True):
            for s in tqdm(char_list, desc="split char", leave=False, ascii=True):
                """# time.sleep(.001)"""
                loop_char = [l, r]
                if s not in loop_char:
                    text = f"{s}{l}found one{r}{s}{s}{l}found two{r}"
                    data = pattern_between(text, l, r, s)
                    count += 1

                    if "Error" in data:
                        err_list.append(data)

    return err_list, char_list, count


def run_ascii_two():
    char_list = []
    char_list_csv = open_csv("ascii2.csv")

    for c in char_list_csv:
        char = c["Symbol"]
        if char.isprintable() == True:
            char_list.append(char)

    err_list = []
    count = 0

    for l in tqdm(char_list, desc="left char", leave=False, ascii=True):
        for r in tqdm(char_list, desc="right char", leave=False, ascii=True):

            text = f"{l}found one{r} {l}found two{r}"
            data = pattern_between_two_char(text, l, r)

            if "Error" in data:
                err_list.append(data)

    return err_list, char_list, count


if __name__ == "__main__":
    t0 = time.time()
    err_list, char_list, count = run_ascii_two()
    t1 = time.time() - t0
    combinations = len(char_list) * len(char_list)
    print(
        f"process took {t1:.2f} seconds with {combinations:,} combinations and a count cycle of {count:,}"
    )

    if len(err_list) != 0:
        save_json("err.json", err_list)
    else:
        print("there were no errors")
