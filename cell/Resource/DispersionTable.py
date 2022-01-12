# -*- coding: gb18030 -*-
#
# $Id: DispersionTable.py,v 1.2 2007-06-14 09:58:11 huangyongwei Exp $

"""
驱散法术配置表。
"""

from bwdebug import *
import Language

class DispersionTable:
	"""
	"""
	_instance = None

	def __init__( self, fileName = None ):
		assert DispersionTable._instance is None, "instance already exist in"

		self._datas = {}			# key(int), value(set())
		if fileName is not None:
			self.load( fileName )

	@staticmethod
	def instance():
		if DispersionTable._instance is None:
			DispersionTable._instance = DispersionTable()
		return DispersionTable._instance

	def load( self, fileName ):
		INFO_MSG( "loading %s ..." % fileName )
		section = Language.openConfigSection( fileName )
		if section is None:
			raise fileName, "open false."
			return

		self._datas = {}

		for sec in section.values():
			id = sec.asInt
			vs = set()
			for ss in sec.values():
				v = eval( ss.asString )
				vs.add( v )
			self._datas[id] = vs

	def __getitem__( self, id ):
		return self._datas[id]



# func
def instance():
	return DispersionTable.instance()
