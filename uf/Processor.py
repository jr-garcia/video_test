from importlib import import_module
from os import path, listdir

from warnings import warn


def import_plugins(plugins_path, processor):
    plugins = []
    plugin_folders = listdir(plugins_path)
    for element_name in plugin_folders:
        full_path = path.join(plugins_path, element_name)
        if path.isdir(full_path):
            for file in listdir(full_path):
                if file == 'converter.py':
                    plugin = import_module('uf.plugins.{}.converter'.format(element_name)).plugin(processor)
                    plugins.append(plugin)
                    break

    return plugins


class VideoProcessor(object):
    def __init__(self, plugins_list, files_destination='.'):
        self.plugins_list = plugins_list
        self.files_destination = files_destination
        self.all_plugins = {}
        self.plugins = {}

        if not isinstance(plugins_list, (list, tuple)):
            raise TypeError('\'plugins_list\'must be of type \'list\'')

        plugins_path = path.join(path.dirname(__file__), 'plugins')
        plugins = import_plugins(plugins_path, self)

        for plugin in plugins:
            plugin_name = plugin.name.lower()
            self.all_plugins[plugin_name] = plugin
            if plugin_name in self.plugins_list:
                self.plugins[plugin_name] = plugin

        if len(self.plugins) == 0:
            warn('no plugins are active. Add one before processing a file.')

    def call_plugins(self, data):
        for plugin in self.plugins.values():
            plugin.before_video_processing(data)
            plugin.on_video_received(data)
            plugin.after_video_processed(data)

    def process_file(self, file_path):
        self.call_plugins(path.abspath(file_path))
