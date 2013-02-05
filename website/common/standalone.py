from __future__ import with_statement

import os
import contextlib

from mochiads_lib import http_model
from mochiads_lib import cfg
import mochiads_lib.helpers

def __exported_functionality__():
    # placate pyflakes
    return [
        mochiads_lib,
        http_model,
    ]

def main():
    import sys
    import glob
    from mochiads_lib import flip_clients
    for fn in glob.glob(os.path.dirname(flip_clients.__file__) + '/*.py'):
        client_name = os.path.splitext(os.path.basename(fn))[0]
        __import__('mochiads_lib.flip_clients.' + client_name)
        globals()[client_name + '_client'] = getattr(
            getattr(
                __import__('mochiads_lib.flip_clients.' + client_name),
                'flip_clients'
            ),
            client_name
        )
    from IPython.Shell import IPShellEmbed
    if sys.argv[1:]:
        cfg.set_flavor(sys.argv[1])
    cfg.set_appname('mochiads_lib')
    cfg.get_config()
    ipshell = IPShellEmbed()
    with contextlib.nested(cfg.context_environ(), cfg.cleanup_context()):
        ipshell()

if __name__ == '__main__':
    main()
