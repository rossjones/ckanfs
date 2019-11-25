
# CKANfs

CKAN as a filesystem. Not a particularly great idea...


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