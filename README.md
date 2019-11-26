
# CKANfs

CKAN as a filesystem. Not a particularly great idea... but fun.

I wanted to know what it would be like if you could mount a CKAN instance into
a local folder, /tmp/ckan in the examples below.

Once mounted, each organisation in CKAN shows up as a folder, within which are
shown each dataset as another folder.  Each dataset then contains one file entry
for each resource, the contents of which _should_ be the contents of the resource's
URL.

Currently this relies on the requests_cache library to avoid making too many requests
to the CKAN instance. Particularly when reading resource (urls), getting the dataset/resource
and remote URL happens several times so needs optimising to remember state.


## Install CKANfs

This needs a lot of cleaning up, and for now, is a bit of a manual task.


### Prerequisites

On OSX, you will need to install [OSXFuse](https://osxfuse.github.io/) which you can
download or install via Homebrew.

### Manual installation

1. `git clone git@github.com:rossjones/ckanfs.git`
2. Make a virtualenv using your preferred method
3. `python setup.py develop`


## Running CKANfs

```
mkdir /tmp/ckan
ckanfs https://myckanhost /tmp/ckan
```

If it gets in a tizz, you may need for force unmount the folder, which is either
`umount -f /tmp/ckan` or `diskutil unmount /tmp/ckan` depending on your OS.