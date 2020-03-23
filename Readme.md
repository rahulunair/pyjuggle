# Python concurrency

Now that everyone is talking about and using `async/await` and
event loops everywhere, I thought I would go to the basics (well,
not to the fundamentals, but practical basics) and write a small
program to download a bunch of text files and process the strings.

## The program

Fetch 3 ebooks from project gutenberg site and do some elemental
processing on the content.

```python

def download(url: str) -> str:
    """download and decode content from a url."""
    page = requests.get(url)
    name = url.split("/")[-1]
    return page.content.decode("utf-8"), f"texts/{name}"

def save(content: str, fname: str = None):
    """save content to file with name."""
    with open(fname, "w") as fh:
        fh.write(content)

def process(string: list) -> list:
    """cpu bound tasks"""
    ...
    ...
    return string

def main():
    urls = [
        "https://www.gutenberg.org/cache/epub/376/pg376.txt",
        "https://www.gutenberg.org/files/84/84-0.txt",
        "https://www.gutenberg.org/cache/epub/844/pg844.txt",
    ]

    # call download

    # call save

    #call string process
```
 The full source code is on github [pyjuggle](https://github.com/rahulunair/pyjuggle).

## Python and concurrency

Let's get this straight, concurrency and parallelism are not the same,
concurrency means, running multiple programs as though they are running
at the same time, where as parallelism is running the programs truly in
parallel in multiple cores of your machine.

The interesting aspect of Python (Ruby and few others) is that there is
something called the global interpreter lock (GIL), that is part of the
cpython implementation, where only one Python object can have access to
the interpreter at one time. This means that, we cannot run two threads
of execution parallely in Python but are time sliced. You can read more 
about the GIL [here](https://wiki.python.org/moin/GlobalInterpreterLock).

Threads come handy though when there is a lot of IO involved or when
there are subprocess calls, where the interpreter is handing-off to
another subsystem, and a new thread of execution can start, while the
previous thread waits for a response.

When we need to real multi-core parallel tasks in Python, mulitprocessing
library comes to our favour, it essentially spins up multiple number
of Python interpreters and works on orthogal exlusive chunks of data, good
for CPU bound tasks.

## When to use what?

Although, there are exceptions, I would say when IO or subprocess call or when the interpreter is giving of control to another sub-system use threads.

The approach I use is to using `concurrent.futures` module and doing something like:

```python
from concurrent.futures import ThreadPoolExecutor as tpe

    # call download method concurrently
    with tpe(max_workers=3) as exe:
        results = exe.map(download, urls)
```

Here, maximum of 4 threads will be spun up, each time sliced, and
will start download the `urls`. One thing to note here is that,
depending upon the amount of data, here the `urls` threaded code
could be slow or not showing significant performance improvement
when compared to one without threading.

The same approach can be used to save the files, create a threadpool and
save the downloaded content

```python
from concurrent.futures import ThreadPoolExecutor as tpe
    ...
    ...
    # call save method concurrently
    with tpe(max_workers=3) as exe:
        exe.map(save, results)
    ...
    ...
```

Finally we come across, a CPU bound task, which has to tokenize the saved
files, here if we use threading, although there could be some speedup
than serial, it is advicable to use multiprocessing, in some cases, threading
could actually slow down the program if the program is mostly CPU bound.

An example of using a multiprocess executor is:

```python
from concurrent.futures import ProcessPoolExecutor as ppe

    # call process method parallely
    with ppe(max_workers=4) as exe:
        exe.map(process, open("./all.txt").readlines())
```
Here we are mapping process method with chunks of data from the file and
to 4 processes, one thing to note here is that the amount of work 
distributed to the processes is not controlled by the programmer.

## The end






