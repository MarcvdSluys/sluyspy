# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2026  Marc van der Sluys - Nikhef/Utrecht University - marc.vandersluys.nl
#   
#  This file is part of the sluyspy Python package:
#  Marc van der Sluys' personal Python modules.
#  See: https://github.com/MarcvdSluys/sluyspy
#   
#  This is free software: you can redistribute it and/or modify it under the terms of the European Union
#  Public Licence 1.2 (EUPL 1.2).  This software is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.  See the EU Public Licence for more details.  You should have received a copy of the European
#  Union Public Licence along with this code.  If not, see <https://www.eupl.eu/1.2/en/>.


"""System functions for the sluyspy package."""


from pathlib import Path as _Path
import re as _re
import sys as _sys
import socket as _socket
import time as _time
import subprocess as _subprocess



def exec_script_name():
    """Return the name of the currently executed Python script.
    
    Returns:
      (str):  The file name of the currently executed Python script.
    """
    
    return _Path(_sys.argv[0]).name


def host():
    """Return the current host name.
    
    Returns:
      (str):  The current host name.
    """
    
    return _socket.gethostname()


def homedir():
    """Return my home directory as a string without trailing slash.
    
    Returns:
      (str):  My home directory as a string without trailing slash.
    """
    
    return str(_Path.home())


def on_think():
    """Test whether I am on a host called think.
    
    Returns:
      (bool):  True when I am on a host called think, False otherwise.
    
    Note: this function is used to set env.host.
    """
    
    return host() == 'think'


def on_zotac():
    """Test whether I am on a host called zotac.
    
    Returns:
      (bool):  True when I am on a host called zotac, False otherwise.
    
    Note: this function is used to set env.host.
    """
    
    return host() == 'zotac'


def on_hwc():
    """Test whether I am on host hwc.
    
    Returns:
      (bool):  True when I am on host hwc, False otherwise.
    
    Note: this function is used to set env.host.
    """
    
    return _Path('/home/hemel/').is_dir()


def where_am_i():
    """Return on which of a hardcoded selection of hosts I am running, or Unknown.
    
    Returns:
      (str):  Code for the host: think, zotac or hwc.
    """
    
    host = 'Unknown'
    if on_think():
        host = 'think'
    elif on_zotac():
        host = 'zotac'
    elif on_hwc():
        host = 'hwc'
    
    return host


def temp_file_name(dir_name=None, base_name='.tmpfile', ext='tmp'):
    """Return a temporary file name, using the system clock, like "dir/file_YYYYMMDD-HHMMSS.mmmmmm.ext".
    
    Args:
      dir_name (str):   Name of the directory for the file to be in.  Use homedir if None.
      base_name (str):  Base name of the file.
      ext (str):        File extension.
    
    Returns:
      (str):  A temporary file name.
    
    Note:
      - microsecond accuracy should suffice; two subsequent calls on my laptop take ~15-20us.
    """
    
    import datetime as dt
    
    if dir_name is None:  dir_name = homedir()
    
    return dt.datetime.now().strftime(dir_name+'/'+base_name+'_%Y%m%d-%H%M%S.%f.'+ext)  # Date and time with microseconds
    

def tail_file(in_file, out_file, num_lines):
    """Use the tail command in a shell to quickly save the last N lines of a file in a new file.
    
    Args:
      in_file (str):    Name of the input file.
      out_file (str):   Name of the output file.
      num_lines (int):  Number of lines to save.
    """
    
    _subprocess.run(['tail -'+str(num_lines)+' '+in_file+' > '+out_file], stdout=_subprocess.PIPE,
                    shell=True, check=True).stdout.decode('utf-8')
    
    return


def head_tail_file(in_file, out_file, num_lines, num_head=1):
    """Use the tail command in a shell to quickly save the last N lines of a file in a new file.
    
    Args:
      in_file (str):    Name of the input file.
      out_file (str):   Name of the output file.
      num_lines (int):  Number of (data) lines to save after the header.
      num_head (int):   Number of header lines to save (optional; defaults to 1).
    """
    
    _subprocess.run(['head -'+str(num_lines)+' '+in_file+' > '+out_file], stdout=_subprocess.PIPE,
                    shell=True, check=True).stdout.decode('utf-8')
    
    _subprocess.run(['tail -'+str(num_lines)+' '+in_file+' >> '+out_file], stdout=_subprocess.PIPE,
                    shell=True, check=True).stdout.decode('utf-8')
    
    return


def string_in_file(infile, string):
    """Check whether a file contains a string.
    
    Args:
      infile (str):  Name of the file.
      string (str):  Match string.
    
    Returns:
      (bool):  True if the file contains the string, False otherwise
    
    Note: fast small files (<~1Mb) and/or few calls (<~100);
          - up to 4-6x faster than string_in_file_grep() for a single call.
    """
    
    with open(infile) as f:
        if string in f.read():
            return True
        else:
            return False
    
    return None


def string_in_file_grep(infile, string):
    """Use the grep command in a shell to quickly check whether a file contains a string.
    
    Args:
      infile (str):  Name of the file.
      string (str):  Match string.
    
    Returns:
      (bool):  True if the file contains the string, False otherwise
    
    Note: fast for large files (>~1Mb) and/or multiple calls (>~100).
    """
    
    try:
        _subprocess.run(['grep -c '+string+' '+infile], stdout=_subprocess.PIPE,
                        shell=True, check=True).stdout.decode('utf-8')
        # Check=false: do not raise an error if string is not found (but return 0)
        result = True  # result = int(count) > 0
        
    except _subprocess.CalledProcessError as e:
        result = None
        if e.returncode == 1:  # Exit status: 0: line found, 1: no line found, 2: error
            # count = e.output.decode('utf-8')
            # result = int(count) > 0
            result = False
        else:
            import sluyspy.cli as scli
            scli.warn('string_in_file(): an error occurred when calling grep')
            result = None
    
    return result


def sleep(time, verbosity=0):
    """Call time.sleep and exit graciously upon keyboard interrupt (Ctrl-C).
    
    Args:
      time (float):     Sleep time in seconds.
      verbosity (int):  Output verbosity (optional; defaults to 0).
    
    Returns:
      (int):  status: 0: uninterrupted, 1: interrupted.
    """
    
    try:
        _time.sleep(time)            # Sleep for time seconds
    except KeyboardInterrupt:
        if verbosity == 1: print(' - Received keyboard interrupt, aborting.')                  # " - " to create some space after "^C"
        if verbosity > 1:  print(' - Received keyboard interrupt whilst sleeping, aborting.')  # " - " to create some space after "^C"
        return 1
    
    return 0


def run_status(command):
    """Run a command and return the status/exit code.
    
    Args:
      command (str):  command to run.
    
    Returns:
      (int):  status/exit code.
    """
    
    result = _subprocess.run([command], stdout=_subprocess.PIPE, stderr=_subprocess.PIPE, shell=True)
    
    return result.returncode


def run_output(command):
    """Run a command and return the standard output.
    
    Args:
      command (str):  command to run.
    
    Returns:
      (str):  standard output.
    """
    
    result = _subprocess.run([command], stdout=_subprocess.PIPE, stderr=_subprocess.PIPE, shell=True).stdout.decode('utf-8')
    
    return result.strip()


def at_schedule(command, when, queue='a', verbosity=0):
    """Schedule a command to be executed by at(1) at the specified time.
    
    Args:
      command (str):    Command line to schedule; passed to at via stdin, so no shell is involved.
      when (str):       Time specification as accepted by at(1), e.g. 'now + 5 minutes', '14:30', 'tomorrow'.
      queue (str):      at queue to submit the job to (optional; defaults to 'a').
      verbosity (int):  Output verbosity (optional; defaults to 0 = silent).
    
    Returns:
      (int):  Job number assigned by at, to be used with atrm(1) or at -c; None when scheduling failed.
    """
    
    result = _subprocess.run(['at', '-q', queue, when], input=command.encode('utf-8'),
                             stdout=_subprocess.PIPE, stderr=_subprocess.PIPE)
    
    if result.returncode != 0:
        import sluyspy.cli as scli
        scli.warn('at_schedule(): at returned exit code '+str(result.returncode)+': '
                  +result.stderr.decode('utf-8').strip())
        return None
    
    # at writes "job <N> at <date>" to stderr:
    match = _re.search(r'job (\d+) at', result.stderr.decode('utf-8'))
    job = int(match.group(1)) if match else None
    
    if verbosity > 0: print('Scheduled job', job, 'for', when, ':', command)
    
    return job


def at_queue(verbosity=0):
    """List the jobs in the at(1) queue.
    
    Args:
      verbosity (int):  Output verbosity (optional; defaults to 0 = silent).
    
    Returns:
      (pd.DataFrame):  DataFrame with one row per queued job and columns:
    
      - job (int):       Job number, to be used with atrm(1) or at -c.
      - dtm (datetime):  Date and time at which the job will run.
      - queue (str):     Queue letter.
      - user (str):      User who submitted the job.
    
      Returns an empty DataFrame when the queue is empty, None on error.
    """
    
    import pandas as _pd
    
    result = _subprocess.run(['atq'], stdout=_subprocess.PIPE, stderr=_subprocess.PIPE)
    
    if result.returncode != 0:
        import sluyspy.cli as scli
        scli.warn('at_queue(): atq returned exit code '+str(result.returncode)+': '
                  +result.stderr.decode('utf-8').strip())
        return None
    
    # atq output per line: "<job>\t<asctime date> <queue> <user>", e.g. "15\tSat Oct 31 16:05:00 2026 a sluys":
    jobs = []
    for line in result.stdout.decode('utf-8').strip().splitlines():
        if line:
            job, rest = line.split('\t', 1)
            dtm, queue, user = rest.rsplit(maxsplit=2)
            jobs.append((int(job), dtm, queue, user))
    
    df = _pd.DataFrame(jobs, columns=['job', 'dtm', 'queue', 'user'])
    if len(df) > 0:
        df['dtm'] = _pd.to_datetime(df['dtm'])
        df = df.sort_values('job').reset_index(drop=True)  # Sort by job number; reset index to 0..n-1
    
    if verbosity > 0: print(df)
    
    return df


def at_remove(jobs, verbosity=0):
    """Remove job(s) from the at(1) queue using atrm(1).
    
    Args:
      jobs (int, list, pd.Series):  Job number(s) to remove, as returned by at_schedule() or listed in
                                    at_queue() (e.g. the at_queue().job column).
      verbosity (int):   Output verbosity (optional; defaults to 0 = silent).
    
    Returns:
      (int):  Exit code of atrm: 0 when all jobs were removed, non-zero otherwise.
    """
    
    if isinstance(jobs, int): jobs = [jobs]
    
    result = _subprocess.run(['atrm'] + [str(job) for job in jobs],
                             stdout=_subprocess.PIPE, stderr=_subprocess.PIPE)
    
    if result.returncode != 0:
        import sluyspy.cli as scli
        scli.warn('at_remove(): atrm returned exit code '+str(result.returncode)+': '
                  +result.stderr.decode('utf-8').strip())
    elif verbosity > 0: print('Removed at job(s):', ', '.join(str(job) for job in jobs))
    
    return result.returncode


def at_remove_all_jobs(verbosity=0):
    """Remove all/any job(s) from the at(1) queue using atrm(1).
    
    Args:
      verbosity (int):   Output verbosity (optional; defaults to 0 = silent).
    
    Returns:
      (int):  Exit code of atrm: 0 when all jobs were removed, non-zero otherwise.
    """
    
    df = at_queue()
    if df is None: return 1  # atq failed; at_queue() has already warned
    
    rc = 0
    if len(df) > 0:
        rc = at_remove(df.job, verbosity=verbosity)
    elif verbosity > 0:
        print('at_remove_all_jobs(): No jobs found, nothing to remove')
    
    return rc
