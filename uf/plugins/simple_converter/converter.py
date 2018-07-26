from subprocess import Popen, CalledProcessError, check_output, DEVNULL

from uf.plugins.simple_converter.ffmpeg_writer import FFMPEG_VideoWriter
from uf.plugins.base_plugin import BasePlugin


class plugin(BasePlugin):
    def __init__(self, processor):
        super().__init__(processor)
        self.name = 'ConverterStreamableSameSize'

    def on_video_received(self, data):
        # print(data)
        self.convert_file(data)

    def convert_file(self, file_path):
        # info = ffmpeg_parse_infos(file_path)
        args = 'ffmpeg -y -i {input} -c:v libvpx-vp9 -crf 32 -b:v 0 -deadline realtime -cpu-used -8 output.webm'.format(
            input=file_path).split()
        # args = 'ffmpeg -y -i {input} -codec:v libtheora -qscale:v 4 -codec:a libvorbis -qscale:a 5 output.ogv'.format(input=file_path).split()

        # reader = FFMPEG_VideoReader(file_path, info)
        # writer = FFMPEG_VideoWriter('output.webm', info['video_size'], info['video_fps'], 'libvpx-vp9')
        # duration = info['video_nframes']
        # while reader.pos < duration:
        #     print(reader.pos, duration)
        #     frame = reader.read_frame()
        #     writer.write_frame(frame)
        # call(args, stdout=PIPE, stderr=PIPE, stdin=DEVNULL, universal_newlines=True)
        try:
            res = check_output(args)
            print(res)
        except CalledProcessError as err:
            exit(err.returncode)
