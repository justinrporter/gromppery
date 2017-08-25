import sys
import argparse

from .gromppery_client import submit_work


def process_command_line(argv):
    '''Parse the command line and do a first-pass on processing them into a
    format appropriate for the rest of the script.'''

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Upload a bundle of files to the gromppery as a '
                    'Submission (usually a finished simulation).')

    for ftype in ['xtc', 'cpt', 'gro', 'log', 'edr', 'tpr']:
        parser.add_argument(
            "--%s" % ftype, required=True,
            help="The GROMACS %s file to upload to the gromppery." % ftype)

    parser.add_argument(
        "--gromppery", required=True,
        help="The URL and port where the gromppery can be found.")
    parser.add_argument(
        "--protein", required=True,
        help="Always choose this protein from the gromppery.")
    parser.add_argument(
        "--hostname", default=None,
        help="Override the current hostname when indicating the host "
             "that ran the simulation.")

    args = parser.parse_args(argv[1:])

    return args


def main(argv=None):
    '''Run the driver script for this module. This code only runs if we're
    being run as a script. Otherwise, it's silent and just exposes methods.'''
    args = process_command_line(argv)

    submit_work(
        gromppery=args.gromppery,
        tag=args.protein,
        files={[getattr(args, ftype) for ftype in
                ['xtc', 'cpt', 'gro', 'log', 'edr', 'tpr']]}
        )


    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
