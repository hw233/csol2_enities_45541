# -*- coding: gb18030 -*-

"""
变身buff，buff结束后改变为自由状态
"""
import csdefine
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_299018( Buff_Normal ):
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
		# 骑乘状态下变身，则自动回收骑宠
		if receiver.vehicle or getCurrVehicleID( receiver ):
			receiver.retractVehicle( receiver.id )
		
		receiver.setTemp( "body_changing_buff_id", self.getBuffID() )
		receiver.begin_body_changing( self._model, self._modelScale )
		Buff_Normal.doBegin( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		变身buff结束后，角色恢复自由状态
		"""
		if receiver.getState() == csdefine.ENTITY_STATE_CHANGING and not receiver.queryTemp( "body_changed_replace_buff", False ):	# 如果角色为变身状态
			receiver.end_body_changing( receiver.id, "" )
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

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		if receiver.getState() == csdefine.ENTITY_STATE_FREE:
			receiver.setTemp( "body_changing_buff_id", self.getBuffID() )
			receiver.begin_body_changing( self._model, self._modelScale )
		elif receiver.getState() == csdefine.ENTITY_STATE_PENDING:
			pass
		elif receiver.getState() != csdefine.ENTITY_STATE_CHANGING:
			receiver.end_body_changing( receiver.id, "" )
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
		