import sys
import os
import argparse
import json
import datetime
import random
import subprocess
import hashlib
import itertools
import platform

import requests


def process_command_line(argv):
    '''Parse the command line and do a first-pass on processing them into a
    format appropriate for the rest of the script.'''

    parser = argparse.ArgumentParser(formatter_class=argparse.
                                     ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--gromppery", required=True,
        help="The URL and port where the gromppery can be found.")
    parser.add_argument(
        "--scratch", required=True,
        help="The directory to attach to and work in.")
    parser.add_argument(
        "--nt", type=int, help="--nt to pass to gmx mdrun")
    parser.add_argument(
        "--protein", default=None,
        help="Always choose this protein from the gromppery.")
    parser.add_argument(
        "--iterations", default=None, type=int,
        help="Terminate after simulating this number of trajectories.")

    args = parser.parse_args(argv[1:])

    if args.iterations is None:
        args.iterations = itertools.count()
    else:
        args.iterations = range(args.iterations)

    return args


def get_tpr_manifest(gromppery):
    '''Connect to the gromppery and get the manifest of availiable tpr
    tags.
    '''

    url = '/'.join([gromppery, 'tprs.json'])

    tag_list = json.loads(requests.get(url).content.decode('utf-8'))

    return tag_list


def get_work(gromppery, tag):
    '''Connect to the gromppery and download a the specified tpr.
    '''

    url = '/'.join([gromppery, 'tprs', tag+'.tpr'])
    r = requests.get(url)

    assert r.status_code == 200, \
        "Status on get_work to %s was %s" % (url, r.status_code)

    return r.content


def simulate(tpr_fname, nt=None):

    base_name = tpr_fname.rstrip('.tpr')

    files = {
        'xtc': base_name+'.xtc',
        'edr': base_name+'.edr',
        'log': base_name+'.log',
        'cpt': base_name+'.cpt',
        'gro': base_name+'.gro',
        'tpr': tpr_fname
    }

    mdrun_call = map(str, [
        'gmx', 'mdrun',
        '-s', files['tpr'],
        '-x', files['xtc'],
        '-e', files['edr'],
        '-g', files['log'],
        '-cpo', files['cpt'],
        '-c', files['gro'],
        '-v'])

    if nt is not None:
        mdrun_call.extend(['-nt', nt])

    p = subprocess.check_output(mdrun_call)

    # p.wait()
    # if p.poll() != 0:
    #     std, err = p.communicate()

    return files


def submit_work(gromppery, tag, files, hostname=None):
    """Submit a (presumably finished) simulation to the gromppery.

    Parameters
    ----------
    gromppery: str
        URL where the gromppery is found. Usually of the form
        [IPADDR]:[PORT] or http(s)://[DOMAIN]:[PORT].
    tag: str
        Name of the project to which the work unit should be submitted.
    hostname: str, default=None
        Name of this host under which to submit the finished simulation.
        If none, hostname will automatically be determined by
        platform.node().
    files: dict
        Dictionary of paths to files that will be uploaded. Requires
        keys: ['xtc', 'cpt', 'gro', 'log', 'edr', 'tpr'].
    """

    url = '/'.join([gromppery, 'tprs', tag, 'submit/'])
    print(url)

    r = requests.post(
        url,
        data={'hostname': platform.node() if hostname is None else hostname},
        files={t: open(files[t], 'rb') for t
               in ['xtc', 'cpt', 'gro', 'log', 'edr', 'tpr']})

    # assert r.status_code == 201, r
    try:
        r.raise_for_status()
    except:
        with open('tmp.html', 'wb') as f:
            f.write(r.content)
        raise


def work(gromppery, scratch, protein=None):
    '''The main logic of the program. Downloads, runs and submits a
    random tpr from the gromppery.
    '''

    if protein is None:
        tag = random.choice(get_tpr_manifest(gromppery))
    else:
        tag = protein

    tprname = os.path.join(scratch, tag+'.tpr')
    with open(tprname, 'wb') as f:
        f.write(get_work(gromppery, tag))

    workfiles = simulate(f.name)
    submit_work(gromppery, tag, workfiles)


def main(argv=None):
    args = process_command_line(argv)

    for i in args.iterations:
        dirtries = 10
        for i in range(dirtries):
            md5 = hashlib.md5(str(datetime.datetime.now().timestamp()) \
                .encode('utf-8')).hexdigest()[0:4]
            dirname = os.path.join(
                args.scratch,
                str(datetime.datetime.now().date()) + '-' + md5)

            try:
                os.mkdir(dirname)
            except FileExistsError as e:
                if i < dirtries:
                    continue
                else:
                    raise e
            else:
                break

        work(args.gromppery, dirname, args.protein)
        print("Finished", dirname)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
