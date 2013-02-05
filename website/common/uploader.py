import os
import random
import urllib2
import mimetypes
import mimetools
import logging
from hashlib import md5

from mochiads_lib import cfg
from mochiads_lib.util import coerce_image, get_filesize
from mochiads_lib.validators import VALID_RESOLUTION

log = logging.getLogger(__name__)

#URL = 'http://mochiads.com/app/upload_image'
#URL = 'http://127.0.0.1:8901/app/upload_image'

MAX_UPLOAD_SIZE = 640 * 1024
MAX_SCREENSHOT_SIZE = 3 * 1024 * 1024
MAX_GAME_UPLOAD_SIZE = 30 * 1024 * 1024
MAX_AD_SIZE =  1200 * 1024
MAX_VIDEO_AD_SIZE = 5 * 1024 * 1024
MAX_TEASER_RES=("100", "100")

def get_srvurl(url):
    if url is None:
        url = 'app/upload_image'

    base_url = random.choice(cfg.get_config_urls('makebanner'))
    return base_url + url

def upload_files(filename, data, path, srvurl=None):
    srvurl = get_srvurl(srvurl)
    res = post_multipart(srvurl,
        fields=[('path', utf8(path))],
        files=[('file_upload', utf8(filename), data)])
    pairs = []
    for line in res.splitlines():
        filesize, url = line.split(' ', 1)
        pairs.append((int(filesize), url))
    return pairs

def thumbnail_size(width, height, max_width=None, max_height=None):
    if not max_width and not max_height:
        raise AttributeError('You must supply a max_width or a max_height')
    ratio = width / float(height)
    if max_height and height > max_height:
        thumb_height = max_height
        thumb_width = thumb_height * ratio
    elif max_width and width > max_width:
        thumb_width = max_width
        thumb_height = thumb_width / ratio
    else:
        thumb_width = width
        thumb_height = height
    return tuple(map(round, [thumb_width, thumb_height]))

def upload_thumbnail(filename, data, size, path, srvurl=None):
    srvurl = get_srvurl(srvurl)
    res = post_multipart(srvurl,
        files=[('file_upload', utf8(filename), data)],
        fields=[('path', utf8(path)), ('size', '%dx%d' % (size))])
    return res

def hash_path(filename, data, prefix, max_segments=5, segment_size=3):
    digest = md5(filename + '\x00' + prefix + '\x00')
    digest.update(data)
    hexdigest = digest.hexdigest()
    segments = [prefix.rstrip('/')]
    for i in xrange(max_segments):
        chunk, hexdigest = hexdigest[:segment_size], hexdigest[segment_size:]
        segments.append(chunk)
        if not hexdigest:
            break
    if hexdigest:
        segments.append(hexdigest)
    path = '/'.join(segments)
    return path

def get_thumbnail_upload(field, path, size=(100, 100), max_size=MAX_UPLOAD_SIZE):
    """
    TODO: What does this do?
    """
    if field is None or isinstance(field, basestring):
        return None
    f = field.file
    if get_filesize(f) > max_size:
        return None
    try:
        url = upload_thumbnail(field.filename,
            f.read(), size=size, path=path)
    except IOError:
        return None
    return url.replace('cdn', 'thumbs', 1)

def get_image_upload(field, path, max_size=MAX_UPLOAD_SIZE):
    if field is None or isinstance(field, basestring):
        return None
    f = field.file
    if get_filesize(f) > max_size:
        return None
    try:
        srvurl = get_srvurl(None)
        url = post_multipart(srvurl,
            files=[('file_upload', field.filename, f.read())],
            fields=[('path', path)])
    except IOError:
        return None
    return url.split(' ')[1].replace('cdn', 'thumbs', 1)

def get_upload(field, original=False, max_size=MAX_UPLOAD_SIZE, add_actions=True):
    """
    TODO: Document
    """
    if field is None or isinstance(field, basestring):
        return None
    f = field.file
    if get_filesize(f) > max_size:
        return None
    try:
        resolution, url = upload_image(field.filename,
            f.read(), original=original, add_actions=add_actions)
    except IOError:
        return None
    return resolution, url.replace('http://s3.', 'http://cdn.')

def upload_game_swf(field, game_slug, max_size=MAX_GAME_UPLOAD_SIZE):
    """
    TODO: Document
    """
    if field is None or isinstance(field, basestring):
        return None
    f = field.file
    filesize = get_filesize(f)
    if filesize > max_size:
        log.info('upload_field max_size exceeded (%d > %d) for %r',
                 filesize, max_size, f.filename)
        return None
    path = game_slug
    try:
        urls = upload_files(field.filename, f.read(), path=path)
    except IOError:
        return None
    return urls

def get_field_data(field, max_size=MAX_GAME_UPLOAD_SIZE):
    if field is None or isinstance(field, basestring):
        return ""
    f = field.file
    filesize = get_filesize(f)
    if filesize > max_size:
        log.info('get_game_upload %d > %d for %r', filesize, max_size, f.filename)
        return None
    return f.read()

def upload_image(filename, data, original=False, srvurl=None, add_actions=True):
    """
    Upload an image to mochiads.com and return the SWF None, or raise IOError
    if the image was not accepted by the server.

    Returns (size, url) where size is a 'WIDTHxHEIGHT' string.
    """
    srvurl = get_srvurl(srvurl)
    res = post_multipart(srvurl,
                         files=[('file_upload', filename, data)],
                         fields=[('add_actions', str(add_actions))])
    size, url = res.split(' ', 1)
    if original:
        origext = os.path.splitext(filename)[1]
        url = os.path.splitext(url)[0] + origext
    return size, url

def find_game_swf(files, swf_url):
    """
    TODO: Document
    """
    swfs = []
    for size, fn in files:
        if os.path.splitext(fn)[-1].lower() == '.swf':
            swfs.append(fn)
    if swf_url:
        bn = os.path.basename(swf_url)
        for fn in swfs:
            if os.path.basename(fn) == bn:
                return fn
    if swfs:
        def keyfn(fn):
            return os.path.splitext(os.path.basename(fn).lower())[-1]
        swfs.sort(key=keyfn)
        return swfs[0]
    return None

def upload_raw_file(filename, data, path):
    srvurl = get_srvurl("app/upload_raw_file")
    res = post_multipart(srvurl, files=[('file_upload', filename, data)], fields=[('path', path)])
    pairs = []
    for line in res.splitlines():
        filesize, url = line.split(' ', 1)
        pairs.append((int(filesize), url))
    return pairs

def upload_video_ad(field, ad_tag, max_size=MAX_VIDEO_AD_SIZE):
    f = field.file
    if get_filesize(f) > max_size:
        return None
    return upload_raw_file(field.filename, f.read(), 'v/%s' % (ad_tag,))

def utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    return s

def post_multipart(url, fields=(), files=()):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    headers = {'Content-Type': content_type,
               'Content-Length': str(len(body))}
    r = urllib2.Request(url, body, headers)
    return urllib2.urlopen(r).read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        key, value = utf8(key), utf8(value)
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        key, filename, value = utf8(key), utf8(filename), utf8(value)
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, safe(filename)))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def safe(s):
    # XXX: Escape more?
    return s.replace('\\', '\\\\').replace('"', '\\"')

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def upload_ad_creative(image, max_size=MAX_AD_SIZE):
    resolution = ''
    errors = set()
    image = coerce_image(image)
    if image is None or isinstance(image, basestring):
        errors.add('image')

    f = image.file
    if get_filesize(f) > max_size:
        errors.add('image_size')

    image_upload = get_upload(image, max_size=max_size)
    if image_upload:
        resolution, swf_url = image_upload
    else:
        errors.add('image')

    if errors:
        return errors, None

    if resolution:
        rmatch = VALID_RESOLUTION.match(resolution)
        width, height = rmatch.groups()

    return errors, (swf_url, width, height)


def upload_teaser(teaser, max_resolution=MAX_TEASER_RES):
    errors = set()
    teaser_url = None
    teaser = coerce_image(teaser)
    teaser_upload = get_upload(teaser, add_actions=False)
    if teaser_upload:
        teaser_res, teaser_url = teaser_upload

        rmatch = VALID_RESOLUTION.match(teaser_res)
        width, height = rmatch.groups()
        if (width, height) != max_resolution:
            errors.add('teaser_size')
    else:
        errors.add('teaser')

    return errors, teaser_url



def main():
    import sys
    for fn in sys.argv[1:]:
        f = file(fn, 'rb')
        d = f.read()
        f.close()
        res = upload_image(fn, d)
        print res


if __name__ == '__main__':
    main()
