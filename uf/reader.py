from os import path


class VideoReader(object):
    def __init__(self, video_path):
        self.video_path = video_path

        if not path.exists(video_path):
            raise FileNotFoundError(video_path)
        else:
            self.video_info = getVideoInfo(video_path)


def getVideoInfo(file_path):
    infos = ffmpeg_parse_infos(file_path)
    return infos
