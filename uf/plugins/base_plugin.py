class BasePlugin(object):
    def __init__(self, processor):
        self.processor = processor
        self.name = 'Base Plugin'

    def before_video_processing(self, data):
        pass

    def on_video_received(self, data):
        pass

    def after_video_processed(self, data):
        pass

    def __repr__(self):
        return self.name
