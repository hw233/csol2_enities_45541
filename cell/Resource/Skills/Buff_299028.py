# -*- coding:gb18030 -*-


from Buff_Normal import Buff_Normal

class Buff_299028( Buff_Normal ):
	"""
	玩家小精灵换装buff，此buff专用于把小精灵换装数据挂载于玩家身上
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.modelNum = ""			# 改变到的目标模型
		self.modelScale = 1.0		# 改变到的目标模型缩放倍数
		self.oldModelNum = ""		# 旧的小精灵模型
		self.oldModelScale = 1.0	# 旧的小精灵模型缩放倍数
		
	def init( self, data ):
		"""
		Param1 的配置格式类似: gw123;1.0
		Param2 的配置格式类似: gw123;1.0
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
			