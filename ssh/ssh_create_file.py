import argparse
import getpass
import logging
import sys

import paramiko


def define_logger():
    logger = logging.getLogger("SSHCreateFile")
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def define_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", action="store", dest="host")
    parser.add_argument("--user", action="store", default=getpass.getuser(), dest="user")
    parser.add_argument("--password", action="store", default=None, dest="password")
    return parser


argparser = define_arg_parser()
logger = define_logger()


def main(argv):
    arguments = argparser.parse_args(argv)
    server = arguments.host
    username = arguments.user
    password = arguments.password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh.exec_command("echo 'TEST_ME' > foo.txt")
    std_in, std_out, std_err = ssh.exec_command("ls")
    logger.info("Files in {}:~/ are: {}".format(server, [f for f in std_out.readlines()]))

    ssh.close()


if __name__ == "__main__":
    main(sys.argv[1:])
