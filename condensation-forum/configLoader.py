"""
Manages retrieval of configuration information at runtime.

Keys are used to retrieve values. If a local config file is found, the key is
pulled as a JSON object from that file. If the file does not exist, the key is
pulled from an environment variable.
"""

import os
import json
import sys

class ConfigLoader(object):

    localConfig = None

    def __init__(self, localConfigFile = None):
        """
        Creates a configuration loader with a given config file to source from.

        localConfigFile is the path to the config file
        """
        if localConfigFile != None:
            try:
                tempString = ""
                with open(localConfigFile, 'r') as myfile:
                    tempString = myfile.read().replace('\n', '')
                self.localConfig = json.loads(tempString)
            except:
                self.localConfig = None

    def get(self, key):
        """
        Fetches a value matching a given key. The highest priority return is the value stored in a config file. If
        there is no config file, the value is queried from the OS as an environment variable.
        """
        someVariable = None
        try:
            someVariable = self.localConfig[key]
        except:
            try:
                someVariable = os.environ[key]
            except:
                return None

        return someVariable
