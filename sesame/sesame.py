"""
Created on 2016-11-03

author: Cipher
"""

import sys
import time
import yaml
import string
import random
import base64
import os.path
import platform
import datetime
import argparse
import subprocess
from Crypto.PublicKey import RSA

################################################################################


def exec_cmd(argv, timeout=10):
    pipe = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # Set timeout.
    _start = datetime.datetime.now()
    _timeout_seconds = timeout
    while (pipe.poll() is None):
        _pass = datetime.datetime.now() - _start
        if _pass.total_seconds() > _timeout_seconds:
            pipe.terminate()
            raise Exception("Exception time out (%d seconds)" % _timeout_seconds)
        time.sleep(0.1)

    stdout, stderr = pipe.communicate()

    return pipe.returncode, stdout.strip(), stderr.strip()


def is_cmd_ok(ret, ignore_code=False):
    if not ret:
        return False

    if ignore_code:
        return True

    return ret[0] == 0


def _log(s):
    print >> sys.stdout, s


def _error(s):
    print >> sys.stderr, s


################################################################################

OS_DARWIN = "Darwin"
OS_LINUX = "Linux"

SUPPORTED_OS = (
    OS_DARWIN,
    OS_LINUX,
)

################################################################################


class OSAdapter(object):
    def __init__(self):
        self.os_platform = platform.system()

    def copy_to_clipboard(self, s):
        _cmd = ""
        if self.platform == OS_DARWIN:
            _cmd = 'echo "{pwd}" | tr -d "\n" | pbcopy'.format(pwd=s)
        # TODO to be tested
        elif self.platform == OS_LINUX:
            _cmd = 'echo "{pwd}" | tr -d "\n" | xclip -selection clipboard'.format(pwd=s)

        exec_cmd(_cmd)

    def get_authorization_cmd(self, user):
        if self.platform == OS_DARWIN:
            return "dscl /Local/Default -authonly {u}".format(u=user)
        elif self.platform == OS_LINUX:
            return "su - {u}".format(u=user)

        return None

################################################################################
# Configuration.


DEFAULT_USER = "root"

DEFAULT_PUBLIC_KEY = "~/.ssh/id_rsa.pub"
DEFAULT_PRIVATE_KEY = "~/.ssh/id_rsa"

BASE_DIR = "~/.sesame"
DEFAULT_PWD = os.path.join(BASE_DIR, "pwd")
DEFAULT_CONFIG = os.path.join(BASE_DIR, "config.yaml")


def _whoami():
    ret = exec_cmd("whoami")
    if is_cmd_ok(ret):
        return ret[1].strip()

    return DEFAULT_USER


def load_config(filepath=DEFAULT_CONFIG):
    global g_config

    if os.path.isfile(filepath):
        with open(filepath, "r") as f:
            try:
                ret = yaml.load(f.read())
            except:
                _error("load config [%s] failed" % filepath)
                return g_config

            g_config.update(ret)

    return g_config

################################################################################


RANDOM_PASSWORD_LENGTH = 16
FIELD_SEPERATOR = ":"


################################################################################


def encode_string(s, pub_key):
    with open(pub_key, "r") as f:
        key = RSA.importKey(f.read())

    _s = base64.b64encode(key.encrypt(s, 18)[0])
    return _s


def _authorization():
    global g_config

    usr = g_config["usr"]

    cmd = g_os_adapter.get_authorization_cmd(usr)
    try:
        ret = exec_cmd(cmd)
    except:
        sys.exit(-1)

    if ret[0] != 0:
        _error(ret[2])
        sys.exit(ret[0])


def decode_string(s, pri_key):
    _authorization()

    with open(pri_key, "r") as f:
        key = RSA.importKey(f.read())

    _s = key.decrypt(base64.b64decode(s))
    return _s


def random_generate_passwd():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(RANDOM_PASSWORD_LENGTH))


################################################################################


def get_site_user_passwds(pwd_file):
    with open(pwd_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            r = line.split(FIELD_SEPERATOR)
            if len(r) != 3:
                continue

            s, u, p = (i.strip() for i in r)

            yield (s, u, p)

    return


def is_site_user_exist(pwd_file, site, username):
    for s, u, p in get_site_user_passwds(pwd_file):
        if s == site and u == username:
            return True

    return False


def get_p(pwd_file, site, username, pri_key):
    for s, u, p in get_site_user_passwds(pwd_file):
        if s == site and u == username:
            return decode_string(p, pri_key)

    return None


def add_p(pwd_file, site, username, pub_key, passwd=None):
    _authorization()

    if is_site_user_exist(pwd_file, site, username):
        _log("Password for [%s:%s] already registered" % (site, username))
        return None

    if not passwd:
        passwd = random_generate_passwd()

    passwd_s = encode_string(passwd, pub_key)

    with open(pwd_file, "a") as f:
        _s = " " + FIELD_SEPERATOR + " "
        f.write("\n" + _s.join((site.ljust(40), username.ljust(40), passwd_s)))

    return passwd


def rm_p(site, username, pwd_file, force):
    new_lines = []
    with open(pwd_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                new_lines.append(line)
                continue

            r = line.split(FIELD_SEPERATOR)
            if len(r) != 3:
                continue

            s, u, p = (i.strip() for i in r)

            if site == s and username == u:
                if not args.force:
                    new_lines.append("# " + line)
                else:
                    _authorization()
            else:
                new_lines.append(line)

    with open(pwd_file, "w") as f:
        f.write("\n".join(new_lines))

    return


def list_p(pwd_file):
    for s, u, p in get_site_user_passwds(pwd_file):
        print s.ljust(40), ":", u.ljust(40)


################################################################################

SUB_CMD_ENCODE = "E"
SUB_CMD_DECODE = "D"
SUB_CMD_ADD = "A"
SUB_CMD_RM = "R"
SUB_CMD_LIST = "L"
SUB_CMD_OPEN = "O"


def _check_file_exist(files):
    for f in files:
        if not os.path.isfile(f):
            _error("File [%s] not found or invalid" % f)
            sys.exit(-1)

    return


def main(args):
    global g_config
    global g_os_adapter

    _public_key = g_config["public_key"]
    _private_key = g_config["private_key"]
    _pwd_file = g_config["pwd"]

    if args.sub_cmd == SUB_CMD_ENCODE:
        _check_file_exist([_public_key])

        _s = encode_string(args.string, _public_key)

        _log(_s)
    elif args.sub_cmd == SUB_CMD_DECODE:
        _check_file_exist([_private_key])

        _s = decode_string(args.string, _private_key)

        _log(_s)
    elif args.sub_cmd == SUB_CMD_ADD:
        _check_file_exist([_pwd_file, _public_key])

        # TODO try to create new file

        _s = add_p(_pwd_file, args.site, args.username, _public_key, passwd=args.password)

        g_os_adapter.copy_to_clipboard(s=_s)
    elif args.sub_cmd == SUB_CMD_RM:
        _check_file_exist([_pwd_file])

        rm_p(args.site, args.username, _pwd_file, args.force)
    elif args.sub_cmd == SUB_CMD_LIST:
        _check_file_exist([_pwd_file])

        list_p(_pwd_file)
    elif args.sub_cmd == SUB_CMD_OPEN:
        _check_file_exist([_pwd_file])

        _s = get_p(_pwd_file, args.site, args.username, _private_key)

        if not _s:
            _error("Password for [%s:%s] not found" % (args.site, args.username))

        g_os_adapter.copy_to_clipboard(s=_s)

        if args.show:
            _log(_s)
        _log("Already copyed into system clipboard.")

    return


################################################################################

if __name__ == "__main__":
    g_os_adapter = OSAdapter()

    if g_os_adapter.platform not in SUPPORTED_OS:
        _log("Current OS platform [%s] not supported" % g_os_adapter.platform)
        sys.exit(1)

    parser = argparse.ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="sub_cmd")

    """
        Common options:
            -p --pwd
            -P --public-key/--private-key
    """

    # TODO add -U --update

    e_parser = sub_parsers.add_parser(SUB_CMD_ENCODE, help="Encode")
    e_parser.add_argument("string", help="""string to encode""")
    e_parser.add_argument("-P", "--public-key", default=DEFAULT_PUBLIC_KEY, dest="public_key")
    e_parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, dest="config")

    d_parser = sub_parsers.add_parser(SUB_CMD_DECODE, help="Decode")
    d_parser.add_argument("string", help="""string to decode""")
    d_parser.add_argument("-P", "--private-key", default=DEFAULT_PRIVATE_KEY, dest="private_key")
    d_parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, dest="config")

    s_parser = sub_parsers.add_parser(SUB_CMD_ADD, help="Add")
    s_parser.add_argument("site")
    s_parser.add_argument("username")
    s_parser.add_argument("-W", "--pwdword", dest="password")
    s_parser.add_argument("-p", "--pwd", default=DEFAULT_PWD, dest="pwd_file")
    s_parser.add_argument("-P", "--public_key", default=DEFAULT_PUBLIC_KEY, dest="public_key")
    s_parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, dest="config")

    s_parser = sub_parsers.add_parser(SUB_CMD_RM, help="Remove")
    s_parser.add_argument("site")
    s_parser.add_argument("username")
    s_parser.add_argument("-p", "--pwd", default=DEFAULT_PWD, dest="pwd_file")
    s_parser.add_argument("-f", "--force", action="store_true", dest="force", default=False)
    s_parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, dest="config")

    s_parser = sub_parsers.add_parser(SUB_CMD_LIST, help="List")
    s_parser.add_argument("-p", "--pwd", default=DEFAULT_PWD, dest="pwd_file")
    s_parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, dest="config")

    s_parser = sub_parsers.add_parser(SUB_CMD_OPEN, help="Open")
    s_parser.add_argument("site")
    s_parser.add_argument("username")
    s_parser.add_argument("-p", "--pwd", default=DEFAULT_PWD, dest="pwd_file")
    s_parser.add_argument("-P", "--private-key", default=DEFAULT_PRIVATE_KEY, dest="private_key")
    s_parser.add_argument("-s", "--show", action="store_true", default=False, dest="show")
    s_parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, dest="config")

    args = parser.parse_args()

    g_config = {
        "usr": _whoami(),
        "public_key": DEFAULT_PUBLIC_KEY,
        "private_key": DEFAULT_PRIVATE_KEY,
        "pwd": DEFAULT_PWD,
    }

    load_config(os.path.expanduser(args.config))

    if hasattr(args, "private_key"):
        g_config["private_key"] = args.private_key
    if hasattr(args, "public_key"):
        g_config["public_key"] = args.public_key
    if hasattr(args, "pwd_file"):
        g_config["pwd"] = args.pwd_file

    for k in ["public_key", "private_key", "pwd"]:
        g_config[k] = os.path.expanduser(g_config[k])

    main(args)

################################################################################
