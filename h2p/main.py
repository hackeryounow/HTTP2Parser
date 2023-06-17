from h2p.parser import HTTP2Parser

def main(filename):
	with open(filename, 'rb') as file:
		data = file.read()

	h2_parser = HTTP2Parser(data, True)
	h2_parser.parse_data()

if __name__ == '__main__':
	main('http2_raw.txt')