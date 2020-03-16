#!/usr/bin/python

import os
import sys

from CoreFoundation import (
    CFPreferencesAppValueIsForced,
    CFPreferencesCopyAppValue,
    CFPreferencesCopyValue,
    kCFPreferencesAnyUser,
    kCFPreferencesAnyHost,
    kCFPreferencesCurrentUser,
    kCFPreferencesCurrentHost,
)


def get_type(value):
    """Returns type of pref value"""
    if value is None:
        return "null"
    type_name = type(value).__name__
    if type_name == "__NSCFDictionary":
        return "dictionary"
    if type_name == "__NSCFArray":
        return "array"
    if type_name in ("pyobjc_unicode", "__NSCFString"):
        return "string"
    if type_name in ("bool", "__NSCFBoolean"):
        return "boolean"
    if type_name == "__NSCFData":
        return "data"
    if type_name == "__NSDate":
        return "date"
    if type_name == "OC_PythonLong":
        return "integer"
    if type_name == "OC_PythonFloat":
        return "real"
    return type(value).__name__


def get_config_level(bundle_id, pref_name, value):
    """Returns a string indicating where the given preference is defined"""
    if value is None:
        return "not set"
    if CFPreferencesAppValueIsForced(pref_name, bundle_id):
        return "MANAGED"
    home_dir = os.path.expanduser("~")
    # define all the places we need to search, in priority order
    levels = [
        {
            "file": os.path.join(
                home_dir, "Library/Preferences/ByHost", bundle_id + ".xxxx.plist"
            ),
            "domain": bundle_id,
            "user": kCFPreferencesCurrentUser,
            "host": kCFPreferencesCurrentHost,
        },
        {
            "file": os.path.join(
                home_dir, "Library/Preferences/", bundle_id + ".plist"
            ),
            "domain": bundle_id,
            "user": kCFPreferencesCurrentUser,
            "host": kCFPreferencesAnyHost,
        },
        {
            "file": os.path.join(
                home_dir, "Library/Preferences/ByHost", ".GlobalPreferences.xxxx.plist"
            ),
            "domain": ".GlobalPreferences",
            "user": kCFPreferencesCurrentUser,
            "host": kCFPreferencesCurrentHost,
        },
        {
            "file": os.path.join(
                home_dir, "Library/Preferences", ".GlobalPreferences.plist"
            ),
            "domain": ".GlobalPreferences",
            "user": kCFPreferencesCurrentUser,
            "host": kCFPreferencesAnyHost,
        },
        {
            "file": os.path.join("/Library/Preferences", bundle_id + ".plist"),
            "domain": bundle_id,
            "user": kCFPreferencesAnyUser,
            "host": kCFPreferencesCurrentHost,
        },
        {
            "file": "/Library/Preferences/.GlobalPreferences.plist",
            "domain": ".GlobalPreferences",
            "user": kCFPreferencesAnyUser,
            "host": kCFPreferencesCurrentHost,
        },
    ]
    for level in levels:
        if value == CFPreferencesCopyValue(
            pref_name, level["domain"], level["user"], level["host"]
        ):
            return level["file"]
    if value == DEFAULT_PREFS.get(pref_name):
        return "default"
    return "unknown"


def get_pref_value(bundle_id, pref_name):
    """Returns the effective value of a preference"""
    return CFPreferencesCopyAppValue(pref_name, bundle_id)


def main():
    try:
        domain = sys.argv[1]
        key = sys.argv[2]
    except IndexError:
        print("Usage: %s <domain> <key>" % sys.argv[0], file=sys.stderr)
        sys.exit(-1)

    value = get_pref_value(domain, key)
    kind = get_type(value)
    where = get_config_level(domain, key, value)
    if not sys.argv[3] == "value":
        print("%s: %s" % (key, repr(value)))
        print("Type: %s" % kind)
        print("Defined: %s" % where)
    else:
        print("%s" % repr(value))


if __name__ == "__main__":
    main()
