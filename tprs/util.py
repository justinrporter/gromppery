import os
import subprocess
import tempfile
import logging
import re

logger = logging.getLogger(__name__)


GROUP_REGEX_STR = 'Group[ ]*(?P<group_number>[0-9])+ "(?P<group_name>[\w-]+)"'


def subset_tpr(tpr_data, group):

    with tempfile.NamedTemporaryFile(suffix='.tpr') as whole_tpr:
        whole_tpr.write(tpr_data)
        whole_tpr.flush()

        with tempfile.NamedTemporaryFile(suffix='.tpr') as partial_tpr:
            partial_tpr_name = partial_tpr.name

        args = [
            'gmx', 'convert-tpr',
            '-s', whole_tpr.name,
            '-o', partial_tpr_name]

        p = subprocess.Popen(
            args, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output, _ = p.communicate(group.encode('ascii'))

        if p.returncode != 0:
            print(output.decode('ascii'))
            raise subprocess.CalledProcessError(
                p.returncode, args, output=output)

        try:
            with open(partial_tpr_name, 'rb') as f:
                group_tpr = f.read()
        finally:
            os.remove(partial_tpr_name)

    return group_tpr


def align(xtc_file, tpr_data, group):

    with tempfile.NamedTemporaryFile(suffix='.tpr') as tpr:
        tpr.write(tpr_data)
        tpr.flush()

        with tempfile.NamedTemporaryFile(suffix='.xtc') as xtc_out:
            xtc_out_name = xtc_out.name

        args = [
            'gmx', 'trjconv',
            '-f', xtc_file,
            '-s', tpr.name,
            '-o', xtc_out_name,
            '-pbc', 'nojump'
        ]

        logger.info("Align cmd: args")
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate(group.encode('ascii'))

        if not os.path.isfile(xtc_out_name):
            raise RuntimeError(
                "\n".join(out.decode('ascii').splitlines()[25:]))

        try:
            with open(xtc_out_name, 'rb') as f:
                xtc_data = f.read()
        except:
            print(out.decode('ascii'))
            raise
        finally:
            if os.path.isfile(xtc_out_name):
                os.remove(xtc_out_name)

    return xtc_data


def make_pdb(xtc_data, tpr_data, group='System', pbc='nojump'):
    """Build a PDB file without periodic boundary conditions out of an
    XTC and TPR.
    """

    try:
        # write the binary data to files for GMX to read
        tpr = tempfile.NamedTemporaryFile(suffix='.tpr')
        tpr.write(tpr_data)
        tpr.flush()

        xtc = tempfile.NamedTemporaryFile(suffix='.xtc')
        xtc.write(xtc_data)
        xtc.flush()

        # get a temp file name for the output pdb
        pdb_out = tempfile.NamedTemporaryFile(suffix='.pdb')
        pdb_out_name = pdb_out.name
        pdb_out.close()

        args = [
            'gmx', 'trjconv',
            '-f', xtc.name,
            '-s', tpr.name,
            '-o', pdb_out_name,
            '-e', '1',
            '-pbc', pbc
        ]

        p = subprocess.Popen(
            args, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        out, _ = p.communicate(group.encode('ascii'))
    finally:
        xtc.close()
        tpr.close()

    try:
        with open(pdb_out_name, 'rb') as f:
            pdb_data = f.read()
    except:
        print(out.decode('ascii'))
        raise
    finally:
        if os.path.isfile(pdb_out_name):
            os.remove(pdb_out_name)

    return pdb_data


def get_tpr_groups(tpr_data):

    with tempfile.NamedTemporaryFile(suffix='.tpr') as tpr:
        tpr.write(tpr_data)
        tpr.flush()

        args = [
            'gmx', 'select',
            '-s', tpr.name,
        ]

        p = subprocess.Popen(args, stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)

        try:
            output, error = p.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            # gmx select always waits for input, so we terminate it
            # using the timeout parameter of run, but that means we have
            # to catch a TimeoutExpired exception here.
            p.kill()
            output, error = p.communicate()

        groups = re.findall(GROUP_REGEX_STR, error.decode('latin'))

    return list(zip(*groups))[1]



