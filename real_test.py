from uf.Processor import VideoProcessor

pr = VideoProcessor(('splitter',), 'static')

pr.process_file('./videos/bunny/bunny.webm')
