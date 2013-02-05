"""Git hooks (server-side) for Mochi repositories.

Currently contains a post-receive hook for doing a POST to the local mochisvn
instance.  The format of this POST is JSON and is nearly identical to the
github post-receive webook: http://help.github.com/post-receive-hooks/

Clone this repository somewhere and then ln -s the scripts into the
hooks dir of a bare repo.

More detail in https://trac.mochimedia.net/ticket/13343

$ echo OLDREV NEWREV REF | HOOK_DEBUG=1 ./post-receive

"""
import os
import sys
import re
import subprocess
import time
import urllib2
from email.utils import parseaddr
import pprint
import json

POST_URL = 'http://127.0.0.1:8910/git'
REPO_URL = 'ssh://192.168.0.106'
REPO_BASE = '/data/git/crown.git'
UNITTEST = False

def git_call(argv, _memo={}):
    """Call git in a subprocess and return the stdout. Memoized,
    so calls with the same arguments are cheap.

    """
    memokey = tuple(argv)

    rval = _memo.get(memokey)
    if rval is None:
        p = subprocess.Popen(['git'] + argv, stdout=subprocess.PIPE)
        rval = p.communicate()[0]
        _memo[memokey] = rval
    return rval


ALLBALLS = re.compile(r'^0+$')
def list_commits(oldrev, newrev, ref):
    """List of commits from oldrev to newrev with respect to ref.

    """
    if ALLBALLS.match(newrev):
        # Delete
        return []
    elif ALLBALLS.match(oldrev):
        # New branch
        return list_commits_new_branch(newrev, ref)
    else:
        # Merge or branch progress
        return get_unique_commits('%s..%s' % (oldrev, newrev), ref)


def mark_branch_root(commit):
    """Return a commit dict that is marked with a branch_root and
    if refs is empty use [name] as refs. This ensures that it will
    get picked up by mochisvn as a merge.

    """
    return dict(
        commit,
        refs=commit['refs'] or [commit['name']],
        branch_root=True,
    )


def get_unique_commits(revspec, ref):
    """Find all commits in revspec that are only reachable from ref

    """
    # Get the list of existing refs, not including the new ref.
    heads = git_call(["for-each-ref", "--format=%(refname)", "refs/heads/"]).splitlines()
    if ref in heads:
        # Only refs/tags and refs/remotes would typically fail the existence check
        heads.remove(ref)

    #heads = map(lambda x:' --not ' + x, heads)
    revs = git_call(["rev-list", revspec, '--not'] + heads + ['--']).splitlines()
    # annotate the revisions with all the info we need.
    return map(get_commit, revs)


def list_commits_new_branch(newrev, ref):
    """Find all commits since the branch point (ie, all commits not
    reachable via any other ref).

    """
    # Get annotated commits only reachable via the new ref @newrev.
    revs = get_unique_commits(newrev, ref)

    # Determine the parent revs of this branch and include them in the
    # list of revisions so mochisvn can display where the branch came
    # from. This is a little bit of a hack. A better approach might be
    # to include the information as a separate field in the JSON we send
    # to mochisvn, instead of listing the branch point as a commit in
    # the commit list. But this is simple and easy, so meh.
    if not revs:
        # empty branch. branch point is newrev.
        parents = [newrev]
    else:
        # otherwise, the parents of the first rev in the branch. note
        # this can be empty.
        parents = revs[-1]['parents']

    parent_info = [mark_branch_root(get_commit(rev)) for rev in parents]
    revs.extend(parent_info)
    return revs


AUTHOR_RE = re.compile(r'^(.*?) (\d+) (\+|-)(\d\d)(\d\d)$')
def parse_author(value):
    author, timestamp, tzsign, tzhh, tzmm = AUTHOR_RE.match(value).groups()
    ts = '%04d-%02d-%02dT%02d:%02d:%02dZ' % time.gmtime(int(timestamp))[:6]
    return dict(
        author=dict(zip(('name', 'email'), parseaddr(author))),
        modified=ts,
    )


def repo_name(repo_dir):
    if repo_dir.endswith('/.git'):
        repo_dir = repo_dir[:-5]
    elif repo_dir.endswith('.git'):
        repo_dir = repo_dir[:-4]
    if repo_dir.startswith(REPO_BASE):
        return repo_dir[len(REPO_BASE):]
    else:
        return os.path.basename(repo_dir)


def repo_url(repo_dir):
    return REPO_URL + repo_dir


def parse_commit(s, name):
    info = {'parents': [], 'name': name.strip()}
    right = s

    # headers
    while right:
        left, _, right = right.partition('\n')
        if not left:
            break
        key, _, value = left.partition(' ')
        if key == 'commit':
            commitid, _, branchspec = value.partition(' ')
            info['id'] = commitid
            info['refs'] = branchspec[1:-1].split(', ') if branchspec else []
        elif key == 'author':
            info.update(parse_author(value))
        elif key == 'tree':
            info['tree'] = value
        elif key == 'parent':
            info['parents'].append(value)

    # commit message
    message = []
    while right:
        left, _, right = right.partition('\n')
        if not left.startswith('    '):
            break
        message.append(left[4:])
    info['message'] = '\n'.join(message)

    # --name-status
    code_names = dict(
        A='added',
        C='copied',
        D='deleted',
        M='modified',
        R='renamed',
        T='type_changed',
        U='unmerged',
        X='unknown',
        B='broken_pairing',
    )

    codes = dict((k, []) for k in code_names.iterkeys())
    while right:
        left, _, right = right.partition('\n')
        if not left:
            break
        code, _, fn = left.partition('\t')
        try:
            codes[code].append(fn)
        except KeyError:
            print >>sys.stderr, 'Unknown --name-status: %r' % (left,)
    for k, v in codes.iteritems():
        info[code_names[k]] = v
    global UNITTEST
    if info.get('name', '') in ['dev', 'master']:
        UNITTEST = True
    return info


def get_commit(rev):
    return parse_commit(
        git_call(['log', '-1', '--name-status',
                  '--format=raw', '--decorate=full', rev]),
        git_call(['name-rev', '--always', '--name-only', rev]))


def all_revs(lst, oldrev, newrev):
    """Return a dict of {revision: data} for all revisions in the commit list
    plus their parents.

    """
    revset = set(rev for rev in (oldrev, newrev) if not ALLBALLS.match(rev))
    revdct = {}
    for v in lst:
        revdct[v['id']] = v
        revset.update(v['parents'])
    for rev in revset:
        if rev in revdct:
            continue
        revdct[rev] = get_commit(rev)
    return revdct


def receive_dict(repo_dir, oldrev, newrev, refname):
    commits = list_commits(oldrev, newrev, refname)
    return dict(
        before=oldrev,
        after=newrev,
        ref=refname,
        repository=dict(
            name=repo_name(repo_dir),
            url=repo_url(repo_dir),
            path=repo_dir,
        ),
        user=os.environ.get('USER'),
        commits=[commit['id'] for commit in commits],
        commit_dict=all_revs(commits, oldrev, newrev),
    )


def post_json(dct):
    if os.environ.get('HOOK_DEBUG'):
        #print json.dumps(dct, indent=' ' * 4, sort_keys=True)
        return
    else:
        req = urllib2.Request(
            POST_URL,
            json.dumps(dct),
            {'Content-Type': 'application/json'})
        return urllib2.urlopen(req).read()


def main():
    repo_dir = os.getcwd()
    for line in sys.stdin:
        oldrev, newrev, refname = line.rstrip().split()
        post_json(receive_dict(repo_dir, oldrev, newrev, refname))


def run_unittest():
    subprocess.Popen(['python', 'test.py'], stdin=subprocess.PIPE, cwd='/home/dongyi/code/hades/')

def update_code():
    os.chdir('/home/dongyi/code/hades/')
    os.unsetenv('GIT_DIR')
    #os.system('env -i git pull')
    #git_call(['pull', 'origin', 'dev'])
    p = subprocess.Popen(['git', 'pull', 'origin', 'dev'], stdin=subprocess.PIPE, cwd='/home/dongyi/code/hades/')
    global UNITTEST
    if UNITTEST:
        run_unittest()
    #p.stdin.write('dongyi\n')
    #p = subprocess.Popen(['make', 'html'], cwd='/home/dongyi/code/hades/doc')

if __name__ == '__main__':
    main()
    update_code()


