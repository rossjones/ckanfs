from ckanapi import RemoteCKAN

from stat import S_IFDIR, S_IFREG
from time import time
from os import getuid, getgid, path

from datetime import datetime
import dateparser
import requests
import requests_cache

requests_cache.install_cache("thecache")


class Factory:
    def __init__(self, host):
        self.host = host

    def build_proxy(self, path):
        parts = path.split("/")[1:]
        part_count = len(parts)

        if part_count == 1:
            if parts[0] == "":
                return CatalogProxy(self.host)
            else:
                return OrgProxy(self.host, parts[0])
        elif part_count == 2:
            return DatasetProxy(self.host, parts[1])
        elif part_count == 3:
            return ResourceProxy(self.host, parts[1], parts[2])

        return ""


class Proxy:
    def __init__(self, host):
        self.uid = getuid()
        self.gid = getgid()
        self.ckan = RemoteCKAN(host)

    def default_attributes_folder(self):
        return dict(
            st_mode=(S_IFDIR | 0o700), st_nlink=2, st_gid=self.gid, st_uid=self.uid,
        )

    def names(self):
        return []


class CatalogProxy(Proxy):
    def __init__(self, host):
        super(CatalogProxy, self).__init__(host)

    def attributes(self):
        return {
            **self.default_attributes_folder(),
            **{"st_atime": float(time()), "st_mtime": float(time()), "st_size": 0},
        }

    def names(self):
        org_names = self.ckan.action.organization_list(
            all_fields=False, include_dataset_count=False
        )
        return [org for org in org_names]


class OrgProxy(Proxy):
    def __init__(self, host, organisation_name):
        self.organisation_name = organisation_name
        super(OrgProxy, self).__init__(host)

    def attributes(self):
        return {
            **self.default_attributes_folder(),
            **{"st_atime": float(time()), "st_mtime": float(time()), "st_size": 0},
        }

    def names(self):
        owner = self.ckan.action.organization_show(
            id=self.organisation_name, include_datasets=True
        )
        return [pkg["name"] for pkg in owner["packages"]]


class DatasetProxy(Proxy):
    def __init__(self, host, dataset_name):
        super(DatasetProxy, self).__init__(host)

        self.dataset_name = dataset_name

    def attributes(self):
        return {
            **self.default_attributes_folder(),
            **{"st_atime": float(time()), "st_mtime": float(time()), "st_size": 0},
        }

    def names(self):
        dataset = self.ckan.action.package_show(id=self.dataset_name)
        return [_find_resource_name(r) for r in dataset["resources"]]


def _find_resource_name(resource):
    fullname = resource["url"].split("/")[-1]
    name, ext = path.splitext(fullname)
    if not ext:
        name = name + "." + resource["format"].lower()
    else:
        name = fullname
    return name


class ResourceProxy(Proxy):
    def __init__(self, host, dataset_name, resource_name):
        self.resource_name = resource_name
        super(ResourceProxy, self).__init__(host)

        self.resource_dict = {}
        dataset = self.ckan.action.package_show(id=dataset_name)
        for resource in dataset["resources"]:
            name = _find_resource_name(resource)
            if name == resource_name:
                self.resource_dict = resource
                break

    def attributes(self):
        return {
            **self.default_attributes_folder(),
            **{
                "st_mode": (S_IFREG | 0o700),
                "st_atime": float(time()),
                "st_mtime": float(self.last_modified()),
                "st_size": self.size(),
            },
        }

    def last_modified(self):
        if not self.resource_dict:
            return time()

        dt = self.resource_dict['last_modified']
        if not dt:
            dt = self.resource_dict['created']

        date = dateparser.parse(dt)
        return datetime.timestamp(date)

    def size(self):
        if not self.resource_dict:
            return 0

        r = requests.get(self.resource_dict['url'])
        if r.status_code != 200:
            return 0
        return int(r.headers.get('content-length', 0))


    def data(self, offset, size):
        # This is going to get called many times and
        # so we are very dependent on the caching of
        # the request.  Would be nicer to know whether
        # range headers were supported.
        r = requests.get(self.resource_dict['url'])
        if r.status_code != 200:
            return b''

        return r.content[offset:offset+size]

    def names(self):
        raise "Should not be called"

