"""
Library for dealing with avatars
"""
from cStringIO import StringIO
from hashlib import md5
import os
import sys

try:
    from PIL import Image as PILImageLibHokey
    Image = PILImageLibHokey
except ImportError:
    try:
        import Image as PILImageLibPokey
        Image = PILImageLibPokey
    except ImportError, e:
        print >> sys.stderr, 'You need to install the Python Imaging Library. Get it at http://www.pythonware.com/products/pil/ .'
        raise e

import uploader

# Size definition for avatars
THUMBNAIL_SIZE = (50, 50)
NORMAL_SIZE = (100, 100)

# Some maximum defaults..
MAX_SIZE = (2000, 2000)

# Max file size
MAX_FILE_SIZE = 4200000

# The suffix of each avatar
#
# XXX - The resized images should've been named by size :(
#
AVATAR_THUMBNAIL = "thumbnail"
AVATAR_NORMAL = "normal"
AVATAR_ORIG = "original"
AVATAR_SIZES = {
    AVATAR_NORMAL: NORMAL_SIZE,
    AVATAR_THUMBNAIL: THUMBNAIL_SIZE,
}

# Image types..
# IMAGE_TYPE_JPEG = "JPEG"
# IMAGE_OPTIONS = dict(quality=90)

IMAGE_TYPE = 'PNG'
IMAGE_OPTIONS = dict(optimize=True)

class InvalidImageException(Exception):
    def __init__(self, key, message):
        self.key = key
        self.message = message

def validate_upload(img_file):
    """
    Validate an incoming file
    """
    try:
        img = Image.open(img_file)
    except:
        raise InvalidImageException('image_type', "File must be a valid image")

    # Make sure the avatar has the correct proportions
    if img.size[0] > MAX_SIZE[0] or img.size[1] > MAX_SIZE[1]:
        msg = "File must be less than or equal to %sx%s pixels" % (MAX_SIZE[0], MAX_SIZE[1])
        raise InvalidImageException('image_size', msg)

    return img

def save_and_upload(img, img_path, img_type):
    img.save(img_path, img_type, **IMAGE_OPTIONS)
    # HACK #2652 - /full/path/avatardir/fn -> community/avatar/fn
    path = os.path.join(
        'community',
        os.path.basename(os.path.dirname(img_path)))
    uploader.upload_files(
        os.path.basename(img_path),
        open(img_path, 'rb').read(),
        path)
    # hack to return a path for the url
    return os.path.join('/', path, os.path.basename(img_path))

def get_image_hash(img, img_type=IMAGE_TYPE):
    sio = StringIO()
    img.save(sio, img_type, **IMAGE_OPTIONS)
    return md5(sio.getvalue()).hexdigest()

def create_upload(img, img_id, image_path, img_type=IMAGE_TYPE, create_thumbnail=True):
    """
    Takes a python image (http://www.pythonware.com/library/pil/handbook/image.htm) and creates the appropriate
    avatars for the site.
    """

    # Convert paletted images (GIF files) to RGB
    if img.mode == 'P':
        img = img.convert("RGB")

    img_id = '%s_%s' % (img_id, get_image_hash(img, img_type))
    width, height = img.size

    # Check if the original images exist.. If they do blow them away
    full_img_id = "%s_%dx%d.%s" % (img_id, width, height, img_type.lower())
    img_path = os.path.join(image_path, full_img_id)
    url = save_and_upload(img, img_path, img_type)

    for flavor in AVATAR_NORMAL, AVATAR_THUMBNAIL:
        _, _, copy_img_id = get_upload_image_url(url, flavor).rpartition('/')
        copy_path = os.path.join(image_path, copy_img_id)
        copy = img.copy()
        copy.thumbnail(AVATAR_SIZES[flavor], Image.ANTIALIAS)
        save_and_upload(copy, copy_path, img_type)

    return url

def avatar_info(url):
    dirname, _, fname = url.rpartition('/')
    base, _, ftype = fname.rpartition('.')
    aliasfhash, _, res_or_original = base.rpartition('_')
    alias, _, fhash = aliasfhash.rpartition('_')
    if res_or_original == 'original':
        res = None
    else:
        res = res_or_original
    return dict(
        file_type=ftype,
        dirname=dirname,
        res=res,
        alias=alias,
        file_hash=fhash,
    )

def get_upload_image_url(base_url, size=AVATAR_NORMAL):
    if base_url is None:
        return None
    elif size == AVATAR_ORIG:
        return base_url

    info = avatar_info(base_url)
    if info['res']:
        info['res'] = '%dx%d' % AVATAR_SIZES[size]
    else:
        info['res'] = size
    return '%(dirname)s/%(alias)s_%(file_hash)s_%(res)s.%(file_type)s' % info
