# -*- coding: utf_8 -*-
#

"""
ʵ�ַ���������ͻ��˲�����¼

2010.04.12: writen by huangyongwei
"""

class OPRecorder :
	def __init__( self ) :
		self.__opUnRecords = {}					# { optype : δ����¼�� id }

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def opr_onRcvUnRecords( self, optype, unrecordids ) :
		"""
		defined method
		��������δ����¼�ļ�¼ ID
		"""
		self.__opUnRecords[optype] = set( unrecordids )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def opr_saveRecord( self, optype, recordid ) :
		"""
		����һ����¼
		"""
		if recordid in self.__opUnRecords[optype] :
			reds = self.__opUnRecords[optype]
			if recordid in reds :
				reds.remove( recordid )
		self.base.opr_saveRecord( optype, recordid )

	def opr_getUnRecords( self, optype ) :
		"""
		��ȡָ�����͵Ĳ�����¼�б�
		"""
		return self.__opUnRecords.get( optype, set() )
