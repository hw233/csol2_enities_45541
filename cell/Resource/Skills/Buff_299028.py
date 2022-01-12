# -*- coding:gb18030 -*-


from Buff_Normal import Buff_Normal

class Buff_299028( Buff_Normal ):
	"""
	���С���黻װbuff����buffר���ڰ�С���黻װ���ݹ������������
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.modelNum = ""			# �ı䵽��Ŀ��ģ��
		self.modelScale = 1.0		# �ı䵽��Ŀ��ģ�����ű���
		self.oldModelNum = ""		# �ɵ�С����ģ��
		self.oldModelScale = 1.0	# �ɵ�С����ģ�����ű���
		
	def init( self, data ):
		"""
		Param1 �����ø�ʽ����: gw123;1.0
		Param2 �����ø�ʽ����: gw123;1.0
		"""
		Buff_Normal.init( self, data )
		modelInfo = data["Param1"].split( ";" )
		self.modelNum = modelInfo[0]
		self.modelScale = float( modelInfo[1] )
		oldModelInfo = data["Param2"].split( ";" )
		self.oldModelNum = oldModelInfo[0]
		self.oldModelScale = float( oldModelInfo[1] )
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setTemp( "eidolonModelNum", ( self.modelNum, self.modelScale ) )
		eidolonCellCall = receiver.callEidolonCell()
		if eidolonCellCall:
			eidolonCellCall.changeModel( self.modelNum, self.modelScale )
			
	def doReload( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "eidolonModelNum", ( self.modelNum, self.modelScale ) )
		eidolonCellCall = receiver.callEidolonCell()
		if eidolonCellCall:
			eidolonCellCall.changeModel( self.modelNum, self.modelScale )
			
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "eidolonModelNum" )
		eidolonCellCall = receiver.callEidolonCell()
		if eidolonCellCall:
			eidolonCellCall.changeModel( self.oldModelNum, self.oldModelScale )
			