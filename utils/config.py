import os
try:
    from configparser import ConfigParser, MissingSectionHeaderError, NoOptionError, NoSectionError  # Python 3.
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser, MissingSectionHeaderError, NoOptionError, NoSectionError  # Python 2.

from msg import exit_with_error_msg


class ConfigParserLazy(object):
    def __init__(self, path=None):
        self.path = path
        self._config_parser = None

    def _get_config_parser(self):
        if not self.path:
            # Then get config.ini.
            dirpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            self.path = os.path.join(dirpath, 'config.ini')
        config_parser = ConfigParser()
        try:
            config_parser.read(self.path)
        except MissingSectionHeaderError:
            exit_with_error_msg('{}\'s content is not in the right format'.format(self.path))
        return config_parser

    def get(self, section, name, is_bool=False):
        # Lazily loading the config file.
        if not self._config_parser:
            self._config_parser = self._get_config_parser()

        try:
            if is_bool:
                return self._config_parser.getboolean(section, name)
            return self._get_item(section, name)
        except (NoOptionError, NoSectionError, KeyError):
            exit_with_error_msg('Attribute "[{}] {}" missing in {}'.format(section, name, self.path))

    def _get_item(self, section, name):
        try:
            return self._config_parser[section][name]  # Python 3.
        except AttributeError:
            return self._config_parser.get(section, name)  # Python 2.

    def __getattr__(self, item):
        # Lazily loading the config file.
        if not self._config_parser:
            self._config_parser = self._get_config_parser()

        return getattr(self._config_parser, item)


config = ConfigParserLazy()
