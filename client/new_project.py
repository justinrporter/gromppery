import os
import sys
import argparse
import requests
import tempfile
import shutil


def process_command_line(argv):
    '''Parse the command line and do a first-pass on processing them into a
    format appropriate for the rest of the script.'''

    parser = argparse.ArgumentParser(formatter_class=argparse.
                                     ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--top", required=True,
        help="Topology file to submit.")
    parser.add_argument(
        "--mdp", required=True,
        help="MDP file to submit.")
    parser.add_argument(
        "--gro", required=True,
        help="Conformation file to submit.")

    parser.add_argument(
        "-n", "--project-name", required=True,
        help="The name to give the project.")

    parser.add_argument(
        "--gromppery", required=True,
        help="The location (including port) for the gromppery.")

    args = parser.parse_args(argv[1:])

    assert os.path.isfile(args.top)
    assert os.path.isfile(args.gro)
    assert os.path.isfile(args.mdp)

    return args


def main(argv=None):
    args = process_command_line(argv)

    with tempfile.TemporaryDirectory() as tmpdirname:

        files = {}
        for filetype in ['top', 'gro', 'mdp']:
            new_filename = os.path.join(
                tmpdirname, args.project_name+'.'+filetype)
            shutil.copy(
                getattr(args, filetype),
                new_filename)
            files[filetype] = open(new_filename, 'rb')

        r = requests.post(
            args.gromppery+'/api/tprs/',
            files=files,
            data={'name': args.project_name})

    if r.status_code != 201:
        print('Failed to submit project!')
        print("Response was code {code} with content {content}.".format(
            code=r.status_code, content=r.content))
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
