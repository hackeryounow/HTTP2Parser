import struct

from h2p.frame import Frame, Parser
from h2p.stream import Stream


class HTTP2Parser(object):
	''' Defines the Parser object '''
	def __init__(self, data=None, debug=False):
		self.data = data
		self.streams = dict()
		self.debug = debug
		self.parser = Parser()

	def get_bytes(self, length):
		res = self.data[:length]
		self.data = self.data[length:]
		return res

	def reset(self, debug=None):
		self.streams = {}
		self.data = None
		if debug:
			self.debug = debug

	def parse_frame(self):
		''' Parse an HTTP/2 frame '''
		bin_frame_header = self.get_bytes(9)
		frame_header = Frame.parse_header(bin_frame_header)
		frame_body = struct.unpack(
			'c' * frame_header['length'],
			self.get_bytes(frame_header['length'])
		)

		# Create the frame object
		frame = Frame(frame_header, frame_body, self.parser)

		# Create (and) or get the Stream object
		if frame_header['stream'] not in self.streams:
			self.streams[frame_header['stream']] = Stream(frame_header['stream'])
		stream = self.streams[frame_header['stream']]

		stream.add_frame(frame)

		if self.debug:
			frame.print_info()

	def parse_data(self, data=None):
		""" Parse raw http packets """
		if data:
			self.data = data
		idx = 0
		while len(self.data) > 0:
			if self.data.startswith(b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'):
				magic = self.get_bytes(24)
			else:
				self.parse_frame()
				print()
			idx += 1


