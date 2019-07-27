import sys
import argparse
import os

from gromppery_client import submit_work


def process_command_line(argv):
    '''Parse the command line and do a first-pass on processing them into a
    format appropriate for the rest of the script.'''

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Upload a bundle of files to the gromppery as a '
                    'Submission (usually a finished simulation).')

    ftypes = ['xtc', 'cpt', 'gro', 'log', 'edr', 'tpr']
    for ftype in ftypes:
        parser.add_argument(
            "--%s" % ftype, required=True,
            help="The GROMACS %s file to upload to the gromppery." % ftype)

    parser.add_argument(
        "--gromppery", required=True,
        help="The URL and port where the gromppery can be found.")
    parser.add_argument(
        "--protein", required=True,
        help="Upload the simulation to this project name.")
    parser.add_argument(
        "--hostname", default=None,
        help="Override the current hostname when indicating the host "
             "that ran the simulation.")

    args = parser.parse_args(argv[1:])

    for ftype in ftypes:
        assert os.path.isfile(getattr(args, ftype))

    return args


def main(argv=None):
    '''Run the driver script for this module. This code only runs if we're
    being run as a script. Otherwise, it's silent and just exposes methods.'''
    args = process_command_line(argv)

    submit_work(
        gromppery=args.gromppery,
        tag=args.protein,
        files={ftype: getattr(args, ftype) for ftype in
                ['xtc', 'cpt', 'gro', 'log', 'edr', 'tpr']}
        )

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
