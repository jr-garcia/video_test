from subprocess import CalledProcessError, check_output, list2cmdline

from uf.plugins.splitter.info_parser import ffmpeg_parse_infos
from ..base_plugin import BasePlugin


class plugin(BasePlugin):
    def __init__(self, processor):
        """
        Splits the input file into required streamable files
        :param processor:
        :type processor:
        """
        super().__init__(processor)
        self.name = 'Splitter'

    def on_video_received(self, data):
        # print(data)
        self.convert_file(data)

    def convert_file(self, file_path):
        def callFF(args):
            try:
                res = check_output(args.split() if isinstance(args, str) else args)
                print(res)
            except CalledProcessError as err:
                exit(err.returncode)

        VP9_DASH_PARAMS = "-tile-columns 4 -frame-parallel 1"

        info = ffmpeg_parse_infos(file_path)
        w, h = info['video_size']

        dest = self.processor.files_destination

        output_sizes = (
                        (160, 90, 250),
                        (320, 180, 500),
                        (640, 360, 750),
                        (640, 360, 1000),
                        (1280, 720, 1500)
                        )

        for width, height, bitrate in output_sizes:
            args = 'ffmpeg -y -i {input} -c:v libvpx-vp9 -s {w}x{h} -b:v {b}k -keyint_min 150 -g 150 {DASH_PARAMS} ' \
                   '-an ' \
                   '-f webm -dash 1 {dest}/video_{w}x{h}_{b}k.webm'.format(w=width, h=height, b=bitrate, input=file_path,
                                                                    DASH_PARAMS=VP9_DASH_PARAMS, dest=dest)

            callFF(args)

        args = 'ffmpeg -y -i {input} -c:a libvorbis -b:a 128k -vn -f webm -dash 1 {dest}/audio_128k.webm'.format(
                input=file_path, dest=dest)
        callFF(args)

        videos_string = ''
        map_count = 0
        for width, height, bitrate in output_sizes:
            videos_string += '-f webm_dash_manifest -i {}/video_{}x{}_{}k.webm '.format(dest, width, height, bitrate)
            map_count += 1

        map_string = ''
        for i in range(map_count + 1):
            map_string += '-map {} '.format(i)

        streams_string = 'streams=' + ','.join([str(i) for i in range(map_count)])

        args = 'ffmpeg -y ' \
               '{videos_string}' \
               '-f webm_dash_manifest -i {dest}/audio_128k.webm ' \
               '-c copy {map_string}' \
               '-f webm_dash_manifest ' \
               '-adaptation_sets id=0,{streams_string}^^^id=1,streams={map_count} ' \
               '{dest}/manifest.mpd'.format(videos_string=videos_string, map_string=map_string,
                                            streams_string=streams_string, map_count=map_count, dest=dest)

        args = args.split()
        for i in range(len(args)):
            if '^^^' in args[i]:
                args[i] = args[i].replace('^^^', ' ')
                break
                
        callFF(args)
