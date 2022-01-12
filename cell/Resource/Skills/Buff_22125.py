# -*- coding: gb18030 -*-

"""
变身buff，buff结束后改变为自由状态
"""
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_22125( Buff_Normal ):
	"""
	变身buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._modelScale = 1.0			# 变身模型缩放比例
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._model = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 								# 技能对应的模型编号
		self._modelScale = float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0.0 ) 					# 变身后模型缩放比例
		
	def doBegin( self, receiver, buffData ):
		# 通知更换变身模型
		print "=======>>>>>>skills self.getBuffID() = ", self.getBuffID()
		receiver.setTemp( "body_changing_buff_id", self.getBuffID() )
		
		# 骑乘下马
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.currentModelNumber = self._model
			receiver.currentModelScale = self._modelScale
		else:
			receiver.setTemp("oldModelNumber", receiver.modelNumber )
			receiver.setTemp("oldModelScale", receiver.modelScale )
			receiver.modelNumber = self._model
			receiver.modelScale = self._modelScale
		
		Buff_Normal.doBegin( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		变身buff结束后，角色恢复自由状态
		"""
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if not receiver.queryTemp( "body_changed_replace_buff", False ):	# 如果角色为变身状态
				receiver.currentModelNumber = ""
		else:
			receiver.modelNumber = receiver.queryTemp( "oldModelNumber" )
			receiver.modelScale = receiver.queryTemp( "oldModelScale" )
		receiver.removeTemp( "body_changed_replace_buff" )
		receiver.removeTemp( "body_changing_buff_id" )
		Buff_Normal.doEnd( self, receiver, buffData )
	
	def _replaceLowLvBuff( self, caster, receiver, newBuff, buffs ):
		"""
		Buff 的 替换子流程  从buffs中替换最低级别的BUFF
		@param receiver: 受击者
		@type  receiver: Entity
		@param newBuff: 新BUFF的数据
		@type  newBuff: BUFF
		@param buffs: 准备用来判断的buff索引列表
		"""
		receiver.setTemp( "body_changed_replace_buff", True )
		Buff_Normal._replaceLowLvBuff( self, caster, receiver, newBuff, buffs )
