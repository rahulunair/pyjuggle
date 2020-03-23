"""example of when to use threads vs processes in Python."""
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import os
import glob
import random
import re
import shutil
import sys

import requests

from timer import timer

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def save(content: str, fname: str = None):
    """save content to file with name."""
    try:
        with open(fname, "w") as fh:
            fh.write(content)
    except FileExistsError as e:
        eprint(f"file already exists. {e}")

def download(url: str = None) -> None:
    """download text files and save it.
    params:
    url: str - http url
    """
    page = requests.get(url)
    name = url.split("/")[-1]
    return page.content.decode("utf-8"), f"texts/{name}"

def string_preprocess(string: list) -> list:
    """preprocess list of strings."""
    p_list = []
    for word in string:
        p_list.append(word_preprocess(word))
    return string

def word_preprocess(word: str) -> str:
    """remove all non ascii characters."""
    word = word.lower()
    word = word.strip()
    return only_ascii(word)

def only_ascii(word: str = None) -> str:
    return "".join(filter(str.isascii, word))

@timer
def tokenize(fname: str = "texts/all.txt") -> list:
    """open file fname and tokenize"""
    tokens = []
    with ProcessPoolExecutor(max_workers=4) as exe:
        tokens.extend(exe.map(string_preprocess, open(fname, "r").readlines()))
    return tokens

def combine_files(file: str=None, tofile: str="all.txt"):
    """read folder and write to tofile all found txt files."""
    with open(tofile, "a") as tf:
        with open(f"{file}", "r") as ff:
            tf.write(ff.read())
    return tofile

def distance(word1: str, word2: str) -> int:
    """calculate distance between two words based on ascii order."""
    len1, len2 = len(word1), len(word2)
    dist = 0.0
    if len1 == 0 and len2 == 0:
        return 0
    elif len1 == 0 and len2 != 0:
        return len2
    elif len2 == 0 and len1 != 0:
        return len1
    else:  # two distinct non zero words
        for w1, w2 in zip(word1, word2):
            dist = abs(ord(w1) - ord(w2))
        return dist / max(ord(w1), ord(w2))


def cleanup(folder):
    shutil.rmtree(folder)
    os.mkdir(folder)


@timer
def io_tasks(urls: list) -> str:
    """
    io intentensive tasks
    download contents of urls, save individual files
    and combine all the files.
    params:
    urls : list of urls 
    return:
    name of the big file
    """
    to_file = "all.txt"
    for u in urls:
        content, fname = download(u)
        save(content, fname)    
    combine_files("./texts", to_file)
    return to_file


@timer
def concurrent_io_tasks(urls: list) -> str:
    """
    io intentensive tasks
    download contents of urls, save individual files
    and combine all the files.
    params:
    urls : list of urls 
    return:
    name of the big file
    """
    to_file = "all.txt"
    with ThreadPoolExecutor(max_workers=20) as exe:
        results = exe.map(download, urls)
        exe.map(save, results)    

    files = glob.glob("texts/*.txt")
    for file in files:
        combine_files(file, to_file)
    return to_file

def main():
    urls = [
        "https://www.gutenberg.org/cache/epub/376/pg376.txt",
        "https://www.gutenberg.org/files/84/84-0.txt",
        "https://www.gutenberg.org/cache/epub/844/pg844.txt",
        "https://www.gutenberg.org/files/43/43-0.txt",
        "https://www.gutenberg.org/files/1080/1080-0.txt",
        "https://www.gutenberg.org/cache/epub/17855/pg17855.txt",
        "https://www.gutenberg.org/cache/epub/23700/pg23700.txt",
        "https://www.gutenberg.org/cache/epub/1635/pg1635.txt",
        "https://www.gutenberg.org/cache/epub/19392/pg19392.txt",
        "https://www.gutenberg.org/cache/epub/25525/pg25525.txt"
    ]

    # io intensive
    #big_file = io_tasks(urls)
    big_file = concurrent_io_tasks(urls)
    # compute intensive
    # create 2 random tokens list
    a_tokens = tokenize(big_file)
    b_tokens = a_tokens.copy()
    random.shuffle(a_tokens)
    random.shuffle(b_tokens)

    # measure distances between tokens list
    #for word1, word2 in zip(a_tokens, b_tokens):
    #    distance(word1, word2)

    with ProcessPoolExecutor(max_workers=4) as exe:
        exe.map(distance, zip(a_tokens, b_tokens))
    print("done!")
    # remove downloaded contents
    cleanup("./texts")


if __name__ == "__main__":
    main()
