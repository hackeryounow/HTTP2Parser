from h2p.frame import ErrorCodes


def bits_to_int(bytes):
	''' Convert an array of bits to an integer value '''
	res = 0
	for idx, bit in enumerate(bytes):
		res += (2 ** idx) * bit
	return res


def bytes_concat(payload):
	return b"".join(payload)


def bytes_to_error_code(byte):
	"""
	Convert a byte string or byte array to a error code in ErrorCodes
	:param byte: a byte string or byte array
	:return: a ErrorCode
	"""
	if type(byte).__name__ == 'tuple':
		byte = bytes_concat(byte)
	error_code_id = int.from_bytes(byte, byteorder='big')
	return ErrorCodes(error_code_id)
