#!/usr/bin/env python
import sys
import os
import random
import subprocess
from select import select
import errno

EINTR = getattr(errno, 'EINTR', 4)

already_traversed = set(['.', '..'])
singles = ['bindings1', 'bindings2', 'bindings3', 'bindings4',
           'functions1', 'functions2', 'functions3',
           'if-then-else1', 'if-then-else2', 'if-then-else3',
           'loops1', 'loops2', 'loops3', 'loops4', 'loops5',
           'objects1', 'objects2', 'objects3', 'objects4',
           'operators1', 'operators2', 'operators2', 'operators3',
           'sequence1', 'sequence2']

done = ['bindings1', 'bindings2', 'bindings3', 'bindings4',
           'functions1', 'functions2', 'functions3',
           'if-then-else1', 'if-then-else2', 'if-then-else3',
           'loops1', 'loops2', 'loops3', 'loops4', 'loops5',
           'objects1', 'objects2', 'objects3', 'objects4',
           'operators1', 'operators2', 'operators2', 'operators3',
           'sequence1', 'sequence2']

needed = [interp for interp in singles if interp not in done]


RANDOMS = False


def get_bugs(out):
    bugs = []
    out = out.split("Differences in")
    for chunk in out[:-1]:
        bugs.append(chunk.split("\n")[-2][:-1])

    return bugs


def print_bugs(out, filename=""):
    bugs = get_bugs(out)
    print bugs[0]
    for bug in bugs[1:]:
        print " " * (len(filename) + 2),
        print bug

    for bug in bugs:
        if bug in singles and not bug in done:
            print "\a\a\a\a\a\a\a\a\a\a\a ******* got one!!"
            # if filename != "":
            #     print shell_output(
            #         "cat /Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random/%s" % filename)
            # print "\a\a\a\a\a\a\a\a\a\a\a ******* killall pytyhon from another terminal!!"
            # print shell_output(
            #     "cat /Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random/*.psl")
            # exit(123)


def sprint(string):
    print string
    # with open("/Users/joe/dev/cs-brown-173/assignments/1/joe-test-suitesall_output.txt", "ab") as optf:
    #     optf.write(string)


def shell_output(cmd, verbose=False):
    if verbose:
        sprint("$" + cmd)
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True)

    outbuf = ""
    while proc.poll() is None:
        available_readers = select([proc.stdout, proc.stderr],
                                   [], [], 2.0)[0]
        for r in available_readers:
            try:
                # We use os.read() because file.read() "may call
                # the underlying C function fread() more than once
                # in an effort to acquire as close to 'size' bytes
                # as possible", which means it waits for data
                # unless you do read(1). This way we buffer
                # opportunistically but only read what's already
                # available.
                data = os.read(r.fileno(), 4096)
            except Exception as e:
                if e.args[0] == EINTR:
                    continue
                raise
            if not data:
                break
            outbuf += data
            if verbose:
                sys.stdout.write(data)
                sys.stdout.flush()

    if proc.returncode:
        if not verbose:
            sprint(outbuf)
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    return outbuf


def interperet(path, verbose=False):
    if verbose:
        sprint("    =====start=====  " + path + "  =====start=====")
    shell_output(""
        "/Users/joe/dev/cs-brown-173/assignments/1/osx-dist/bin/assignment1-osx"
        " --interp < {0} 1> {0}.expected 2> {0}.error".format(path), verbose)
    if verbose:
        sprint("    =====end=======  " + path + "  =====end=======")
    # for filename in [path + ".expected", path + ".error"]:
    #     if os.stat(filename).st_size == 0:
    #         shell_output("rm %s" % filename)


def psls_in_dir(directory):
    return [f for f in os.listdir(directory) if (True
        and os.path.isfile(directory + "/" + f)
        and f.endswith(".psl"))]


def procdir(directory, verbose=False):
    global already_traversed
    shell_output("rm -f %s/*.expected" % directory)
    shell_output("rm -f %s/*.error" % directory)
    for f in os.listdir(directory):
        absf = os.path.join(directory, f)
        if os.path.isdir(absf) and absf not in already_traversed:
            already_traversed.add(absf)
            procdir(absf, verbose)
        elif absf.endswith(".psl"):
            interperet(absf, verbose)


if __name__ == '__main__':
    curdir = "."
    tmpdirname = None
    single = None
    onetest = False
    if len(sys.argv) > 1:
        curdir = sys.argv[1]
    if curdir.endswith("random"):
        RANDOMS = True
    if len(sys.argv) > 2:
        single = sys.argv[2]
    if os.path.isfile(curdir) and curdir.endswith(".psl"):
        # sprint(shell_output("cat %s" % (curdir)))
        filename = curdir
        tmpdirname = "%s/tmpplsdirs/.%s" % (os.environ['HOME'], str(random.randint(1000000, 9999999)))
        shell_output("mkdir %s" % tmpdirname)
        shell_output("cp %s %s" % (filename, tmpdirname))
        procdir(tmpdirname)
        psls = psls_in_dir(tmpdirname)
        curdir = tmpdirname
        onetest = True
    else:
        procdir(curdir)
        psls = psls_in_dir(curdir)

    if single is not None:
        sprint("===========================")
        sprint(shell_output(""
                "/Users/joe/dev/cs-brown-173/assignments/1/osx-dist/bin/assignment1-osx"
                " --single %s %s" % (single, curdir)))
        sprint("===========================")
    else:
        report = shell_output(""
                "/Users/joe/dev/cs-brown-173/assignments/1/osx-dist/bin/assignment1-osx"
                " --report %s" % curdir
                )
        print report
        if "false" not in report:
            print "\a\a\a\a\awinner"
            exit(123)

        out = shell_output(""
                "/Users/joe/dev/cs-brown-173/assignments/1/osx-dist/bin/assignment1-osx"
                " --test-interps %s" % curdir
                )

        if not onetest:
            if RANDOMS:
                # try:
                #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                #     print shell_output("ls %s" % curdir)
                #     print shell_output(""
                #         "cat %s/*.error" % curdir)
                #     print shell_output(""
                #         "cat %s/*.psl" % curdir)
                #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!"

                # except:
                #     pass
                print "(" + ", ".join(psls) + ")"
                for f in psls:
                    shell_output("cp %s/%s* %s" % (
                        "/Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random",
                        f,
                        "/Users/joe/dev/cs-brown-173/assignments/1/moar_randoms",
                        ))
                    if f not in out:
                        # shell_output("rm %s/%s*" % (
                        #     "/Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random",
                        #     f,
                        #     ))
                        shell_output("mv %s/%s* %s" % (
                            "/Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random",
                            f,
                            "/Users/joe/dev/cs-brown-173/assignments/1/failed_randoms",
                            ))
                    else:
                        print f, ":",
                        print_bugs(out, f)

                        shell_output("mv %s/%s* %s" % (
                            "/Users/joe/dev/cs-brown-173/assignments/1/joe-test-suites/random",
                            f,
                            "/Users/joe/dev/cs-brown-173/assignments/1/success_randoms",
                            ))
            else:
                sprint(out)
        else:
            # if not any(["Differences in %s" % d in out for d in needed]):
            if not "Differences" in out:
                if True or not RANDOMS:
                    sprint("No bugs")
                    sprint(shell_output(""
                        "/Users/joe/dev/cs-brown-173/assignments/1/osx-dist/bin/assignment1-osx"
                        " --interp < %s" % os.path.join(curdir, filename)))
            else:

                print_bugs(out)
                lines = out.split("\n")

                in_single = None
                for i, line in enumerate(lines):
                    if line.endswith(':') and line[:-1] in singles:
                        in_single = line[:-1]
                    if "Differences in" in line:
                        interpereter = lines[i - 1].split(" ")[-1][:-1]
                        if interpereter not in done:
                            sprint((("*" * 100) + "\n") * 4)
                            sprint("YES!!! I NEEDED " + interpereter)
                            sprint((("*" * 100) + "\n") * 4)
                            sprint("\a" * 20)
                        sprint("+" + "-" * 100)
                        subout = shell_output(""
                                "/Users/joe/dev/cs-brown-173/assignments/1/osx-dist/bin/assignment1-osx"
                                " --single %s %s" % (in_single, curdir))
                        suboutlines = subout.split("\n")
                        sprint("| " + suboutlines[0])
                        printing = False
                        for subline in suboutlines:
                            if "=== Expected stdout ===" in subline:
                                printing = True
                            if subline.startswith("You found bugs in"):
                                printing = False
                            if printing:
                                sprint("| " + subline)

    # if tmpdirname is not None:
    #     shell_output("rm %s/*.*" % tmpdirname)
    #     shell_output("rmdir %s" % tmpdirname)
