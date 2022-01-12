# -*- coding: gb18030 -*-
#
# 2009-2-3 宋佩芳
#

import csdefine
import csstatus
from SpellBase import SystemSpell

class Spell_122159018( SystemSpell ):
	"""
	离开日光浴限制区时施放此技能
	现在改为----离开指定区域回收变身纸牌
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		self._removeBuffIDs = []
		buffIDs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split( "|" )
		for e in buffIDs:
			self._removeBuffIDs.append( int( e ) )

		# 需要的物品ID数组(60101013|60101014|60101015|60101016|60101017|60101018|60101019|60101020)
		self._reqireItems = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split( '|' )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		# 必须是玩家类型或者宠物类型或者镖车（保镖）类型的实体才有触发
		"""
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) ):
			return

		currSunBathAreaCount = receiver.queryTemp( "sun_bath_area_count", 0 ) - 1
		receiver.setTemp( "sun_bath_area_count", currSunBathAreaCount )
		if currSunBathAreaCount <= 0:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				receiver.statusMessage( csstatus.ROLE_LEAVE_SUN_BATH_MAP )
			for spellBuffID in self._removeBuffIDs:	# 删除角色所有日光浴buff
				receiver.removeAllBuffByBuffID( spellBuffID, [csdefine.BUFF_INTERRUPT_NONE] )
		"""
		return	# 暂时return，因为对于这个问题，策划必然会还要改的，因此先不能删除触发器
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return
		if receiver.isReal() :
			for i in self._reqireItems:
				receiver.removeItemTotal( int(i), 1, csdefine.DELETE_ITEM_SYS_RECLAIM_ITEM )
				#item = receiver.findItemFromNKCK_( int(i) )	# 判断是否已经有纸牌了
				#if item != None:
				#	receiver.removeItem_( item.order )		# 移除掉玩家身上的纸牌
		else :
			receiver.receiveOnReal( -1, self )				# 施法者ID传个-1，表示没施法者