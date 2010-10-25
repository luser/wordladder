__all__ = ["load_json", "dump_json"]

try:
  # appengine ships django
  from django.utils.simplejson import dumps as dump_json, loads as load_json
except ImportError:
  try:
    # python 2.6, simplejson as json
    from json import dumps as dump_json, loads as load_json
  except ImportError:
    # simplejson module
    from simplejson import dumps as dump_json, loads as load_json

