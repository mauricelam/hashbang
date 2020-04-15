import importlib
import importlib.abc
import sys
from js import loader
import json


sys.remote_path = ['pymodules.json']


class InternetPathFinder(importlib.abc.MetaPathFinder):

    def __init__(self):
        self.loaded_listings = set()
        self.package_listings = {}

    def load_package_list(self):
        for url in sys.remote_path:
            if url not in self.loaded_listings:
                listing, err = loader.open_url(url)
                if err is None:
                    listing = json.loads(listing)
                    listing.update(self.package_listings)
                    self.package_listings = listing
                self.loaded_listings.add(url)

    def find_spec(self, fullname, path, target=None):
        try:
            if path is None:
                if fullname not in self.package_listings:
                    self.load_package_list()
                if fullname in self.package_listings:
                    pkg_url = self.package_listings[fullname]
                    spec = importlib.machinery.ModuleSpec(
                        fullname,
                        InternetSourceFileLoader(pkg_url + '/__init__.py'),
                        is_package=True)
                    spec.submodule_search_locations = [pkg_url]
                    return spec
            else:
                path = path[0]
                filename = fullname.split('.')[-1]
                return importlib.machinery.ModuleSpec(
                    fullname,
                    InternetSourceFileLoader(f'{path}/{filename}.py'),
                    is_package=False)
        except JsException as e:
            print('Cannot fetch module.', e, file=sys.stderr)
        return None


class JsException(Exception):
    pass


class InternetSourceFileLoader(importlib.abc.SourceLoader):

    def __init__(self, url):
        self.url = url
        self.source_code, err = loader.open_url(url)
        if err is not None:
            raise JsException(str(err))

    def get_data(self, path):
        return self.source_code.encode('utf-8')

    def get_filename(self, fullname):
        return self.url


sys.meta_path.append(InternetPathFinder())
