# -*- coding: utf_8 -*-
#

"""
实现服务器保存客户端操作记录

2010.04.12: writen by huangyongwei
"""

class OPRecorder :
	def __init__( self ) :
		self.__opUnRecords = {}					# { optype : 未被记录的 id }

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def opr_onRcvUnRecords( self, optype, unrecordids ) :
		"""
		defined method
		接收所有未被记录的记录 ID
		"""
		self.__opUnRecords[optype] = set( unrecordids )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def opr_saveRecord( self, optype, recordid ) :
		"""
		保存一条记录
		"""
		if recordid in self.__opUnRecords[optype] :
			reds = self.__opUnRecords[optype]
			if recordid in reds :
				reds.remove( recordid )
		self.base.opr_saveRecord( optype, recordid )

	def opr_getUnRecords( self, optype ) :
		"""
		获取指定类型的操作记录列表
		"""
		return self.__opUnRecords.get( optype, set() )
