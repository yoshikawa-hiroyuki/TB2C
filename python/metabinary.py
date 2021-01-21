#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import array
import json

class MetaBinary():
	
	def __init__(self):
		self.headerStr = "MetaBin:".encode('utf-8')

	def createMetaBinary(self, jsonDict, binary):
		if jsonDict == None or binary == None:
			return

		jsonStr = json.dumps(jsonDict).encode('utf-8')

		pos = 0
		headerLen = len(self.headerStr)
		jsonDictLen = len(jsonStr)
		binaryLen = len(binary)
		#print('size', (headerLen + 8 + jsonDictLen + binaryLen))

		buffer = bytearray(headerLen + 8 + jsonDictLen + binaryLen)
		struct.pack_into("8s", buffer, pos, self.headerStr)
		pos = pos + 8
		# version
		struct.pack_into("H", buffer, pos, 1)
		pos = pos + 4
		# metadata length
		struct.pack_into("H", buffer, pos, jsonDictLen)
		pos = pos + 4
		# metadata
		struct.pack_into(str(jsonDictLen) + 's', buffer, pos, jsonStr)
		pos = pos + jsonDictLen
		# binary
		if (binaryLen > 0):
			struct.pack_into(str(binaryLen) + 's', buffer, pos, binary)

		"""
		#test
		wf = open("test.out", "wb")
		wf.write(buffer)
		wf.close()
		"""
		return buffer
