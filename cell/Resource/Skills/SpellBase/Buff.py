# -*- coding: gb18030 -*-
#
# $Id: Buff.py,v 1.26 2008-08-13 07:20:45 kebiao Exp $

"""
攻击技能类。
"""

from bwdebug import *
from Skill import Skill
from EffectState import EffectState
import BigWorld
import RequireDefine
import csconst
import csstatus
import csdefine
import time
import random

RESIST_VALUE_MIN = 0.05
RESIST_VALUE_MAX = 0.95

def checkResistNone( caster, receiver ):
	return False

def getDaoHengEffect( caster, receiver ):
	daohengEffect = pow( caster.getDaoheng() / receiver.getDaoheng(), 2 )
	if daohengEffect > 1.0:
		daohengEffect = 1.0
		
	return daohengEffect

def checkResistYuanLi( caster, receiver ):
	# 检查元力的抵抗（ 眩晕、昏睡、变形 ）
	if receiver.resist_yuanli == -1:
		return True
		
	buff_hit = getDaoHengEffect( caster, receiver ) - receiver.resist_yuanli
	if buff_hit < RESIST_VALUE_MIN:
		buff_hit = RESIST_VALUE_MIN
		
	if buff_hit > RESIST_VALUE_MAX:
		buff_hit = RESIST_VALUE_MAX
		
	return random.random() > buff_hit

def checkResistLingLi( caster, receiver ):
	# 检查灵力的抵抗（ 定身、减速、沉默 ）
	if receiver.resist_lingli == -1:
		return True
		
	buff_hit = getDaoHengEffect( caster, receiver ) - receiver.resist_lingli
	if buff_hit < RESIST_VALUE_MIN:
		buff_hit = RESIST_VALUE_MIN
		
	if buff_hit > RESIST_VALUE_MAX:
		buff_hit = RESIST_VALUE_MAX
		
	return random.random() > buff_hit

def checkResistTipoLi( caster, receiver ):
	# 检查体魄的抵抗（ 混乱 ）
	if receiver.resist_tipo == -1:
		return True
		
	buff_hit = getDaoHengEffect( caster, receiver ) - receiver.resist_tipo
	if buff_hit < RESIST_VALUE_MIN:
		buff_hit = RESIST_VALUE_MIN
		
	if buff_hit > RESIST_VALUE_MAX:
		buff_hit = RESIST_VALUE_MAX
		
	return random.random() > buff_hit
	
CHECK_DICT = {
	csdefine.RESIST_NONE	 : checkResistNone,
	csdefine.RESIST_YUANLI	 : checkResistYuanLi,
	csdefine.RESIST_LINGLI	 : checkResistLingLi,
	csdefine.RESIST_TIPO	 : checkResistTipoLi,
}
class Buff( Skill, EffectState ):
	"""
		技能的持续性效果
		所有"Buff"类均由"Buff_"开头
		注：此类为旧版中的Condition类
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill.__init__( self )
		EffectState.__init__( self )
		self._buffID = 0 									# BUFFID (由于BUFFID使用了技能*N组成的ID 因此这个ID为真正的BUFFID)
		self._sourceSkillID = 0								# 源技能的ID (由源技能初始化)
		self._sourceSkillIdx = 0							# 该BUFF在源技能身上的位置(由源技能初始化)
		self._level = 0										# BUFF等级
		self._save = False									# 是否保存
		self._isNotIcon = False								# 是否不显示buff图标
		self._persistent = 0								# 持续时间(单位：秒)，如果值 <= 0 则表示一直持续，由其它方式中断
		self._loopSpeed = 0									# 每次触发间隔(单位：秒/次)，如果为0则不触发直到结束。
		self._isAppendPrevious = False						# 是否对现有同类型的BUFF进行追加操作
		self._loopRequire = None							# buff循环时的消耗
		self._buffType = 0									# buff类别 (基础属性	物理攻击性表现属性	法术攻击表现属性	非攻击性表现属性	抗性)
		self._sourceType = 0								# buff小类 （来源类型）
		self._interruptCode = []							# 该BUFF允许这些标志码中断停止
		self._triggerInterruptCode = []						# 该BUFF触发这些标志码中断某些BUFF
		self._baseType = csdefine.BASE_SKILL_TYPE_BUFF		# buff类别
		self._stackable = 1									# 叠加数量
		self._isEffectDaoheng = 0							# 是否受道行的影响
		self._casterID = 0

	def init( self, dictDat ):
		"""
		读取技能配置
		@param dictDat: 配置数据
		@type  dictDat: python dict
		"""
		Skill.init( self, dictDat )
		EffectState.init( self, dictDat )
		self._buffID = self._id
		if dictDat.has_key( "isNotIcon" ) and dictDat["isNotIcon"] != 0:
			self._isNotIcon = True	# 为True表示不显示BUFF图标
		self._persistent = dictDat[ "Persistent" ]
		self._level = dictDat[ "Level" ]
		self._loopSpeed = dictDat[ "LoopSpeed" ]
		self._stackable = dictDat[ "Stackable" ]
		if dictDat.has_key( "Type" ):
			self._buffType = dictDat["Type"]

		self._interruptCode = dictDat[ "InterruptCode" ]
		self._triggerInterruptCode = dictDat[ "triggerInterruptCode" ]
		if dictDat.has_key( "isAppend" ):
			self._isAppendPrevious = bool( dictDat[ "isAppend" ] )
		if dictDat.has_key( "LoopRequire" ):
			self._loopRequire = RequireDefine.newInstance( dictDat["LoopRequire"] )		# 施放法术消耗的东西
			self._loopRequire.load( dictDat["LoopRequire"]["value"] )
		self._sourceType = dictDat[ "SourceType" ]
		
		self._resistEffect = csdefine.RESIST_NONE
		if dictDat.has_key( "ResistEffect" ):
			resistEffect = dictDat[ "ResistEffect" ]
			if isinstance( resistEffect, str ) and hasattr( csdefine, resistEffect ):
				self._resistEffect = getattr( csdefine, resistEffect )
				
		self.param3 = dictDat["Param3"]

	def getLevel( self ):
		"""
		"""
		return self._level

	def getSourceType( self ):
		"""
		获取buff小类 （来源类型）
		"""
		return self._sourceType

	def getBuffID( self ):
		"""
		取得BUFF真正的编号
		"""
		return self._buffID

	def getSourceSkillID( self ):
		"""
		获取buff的源技能ID
		"""
		return self._sourceSkillID

	def getSourceSkillIndex( self ):
		"""
		获取buff在源技能身上的索引位置
		"""
		return self._sourceSkillIdx

	def setSource( self, sourceSkillID, sourceIndex ):
		"""
		设置源技能信息
		"""
		self._id = ( sourceSkillID * 100 ) + sourceIndex + 1 #sourceIndex + 1 是因为BUFF程序ID实际是技能ID+BUFF所在的索引 如果不加1 那么skillID+0=skillID
		self._sourceSkillID = sourceSkillID
		self._sourceSkillIdx = sourceIndex

	def doTick( self, tick ):
		"""
		计算一次tick并检查，返回0表示允许doLoop，否则为tick计数。

		@param tick: 当前tick值
		@type  tick: integer
		@return: 新tick值
		@rtype:  integer
		"""
		if self._loopSpeed <= 0: return 1		# 永不触发
		return (tick + 1) % self._loopSpeed

	def isTimeout( self, timeVal ):
		"""
		virtual method.
		检查是否已超时

		@return: BOOL，如果condition的持续时间还没过则返回False，否则返回True
		@rtype:  BOOL
		"""
		if timeVal == 0: return False		# 无持续时间，永不过期
		return time.time() >= timeVal

	def isSave( self ):
		"""
		"""
		return self._save

	def isNotIcon( self ):
		"""
		是否不显示BUFF图标
		"""
		return self._isNotIcon

	def checkResist( self, caster, receiver ):
		"""
		检查BUFF效果是否被抵抗, True：被抵抗，False：没抵抗
		"""
		if receiver.resist_in_affected:
			return False
		
		if CHECK_DICT.has_key( self._resistEffect ):
			return CHECK_DICT[ self._resistEffect ]( caster, receiver )
		
		return False

	def calculateTime( self, caster ):
		"""
		virtual method.
		取得持续时间
		"""
		if self._persistent <= 0: return 0
		return time.time() + self._persistent

	def cancelBuff( self, reasons ):
		"""
		virtual method.
		取消一个BUFF
		@param reasons: 取消的原因
		@rtype  : bool
		"""
		for reason in reasons:
			if reason in self._interruptCode: # 如果该BUFF能够被该请求取消
				return True
		return False

	def onAddState( self, receiver, buffData, state ):
		"""
		该BUFF在attrBuffs中的状态被切换。
		@param buffData: BUFF
		@param state	:更改的状态
		@type state	:	integer
		"""
		if buffData[ "state" ] & ( csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ) == 0 and \
			state & csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND != 0:
			DEBUG_MSG( "buff %i is disable! changed state to: %i" % ( self.getID(), state ) )
			self.doEnd( receiver, buffData )

	def onRemoveState( self, receiver, buffData, state ):
		"""
		该BUFF在attrBuffs中的状态被切换。
		@param buffData: BUFF
		@param state	:更改的状态
		@type state	:	integer
		"""
		if buffData[ "state" ] & ( csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ) != 0 and \
			state & ( csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ) != 0:
			DEBUG_MSG( "buff %i is enable! changed state to: %i" % ( self.getID(), state ) )
			self.doBegin( receiver, buffData )

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者，None表示不存在
		@type  receiver: Entity
		"""
		if caster is not None:
			casterID = caster.id
		else:
			casterID = 0
		self._casterID = casterID
		
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		receiver.addBuff( self.getNewBuffData( caster, receiver ) )
	
	def getNewBuffData( self, caster, receiver ):
		newBuffData = {}
		newBuffData[ "skill" ] = self.getNewObj()
		newBuffData[ "persistent" ] = self.calculateTime( caster )
		newBuffData[ "currTick" ] = 0
		
		casterID = 0
		if caster is not None:
			casterID = caster.id
		newBuffData[ "caster" ] = casterID
		
		newBuffData[ "state" ] = 0
		newBuffData[ "index" ] = 0
		newBuffData[ "sourceType" ] = self.getSourceType()
		newBuffData[ "isNotIcon" ] = self.isNotIcon()
		return newBuffData

	def doAppend( self, receiver, buffIndex ):
		"""
		Virtual method.
		对一个或多个已经存在的同类型BUFF进行追加操作
		任务使用这个接口进行追加的操作必须继承这个接口的实现，目前不支持配置
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffIndex: 玩家身上同类型的BUFF所在attrbuffs的位置,BUFFDAT 可以通过 receiver.getBuff( buffIndex ) 获取
		"""
		buffdata = receiver.getBuff( buffIndex )
		buffdata["persistent"] += self._persistent
		receiver.client.onUpdateBuffData( buffIndex, buffdata )

	def triggerInterruptCode( self, receiver, buffData ):
		"""
		@triggerInterruptCode: buff触发中断码
		@receiver: 此buff的接受者
		@buffData: 此buff的关联字典数据结构
		"""
		
		rmb = []
		for idx, buff in enumerate( receiver.attrBuffs ):
			if buff["index"] != buffData[ "index" ] and buff["skill"].cancelBuff( self._triggerInterruptCode ):
				rmb.append( idx )

		rmb.reverse()	# 从后面往前删除
		for r in rmb:
			receiver.removeBuff( r, self._triggerInterruptCode )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		DEBUG_MSG( "%i: buff % i [%i] idx:%i begin." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )
		id = buffData["caster"]
		if BigWorld.entities.has_key( id ):
			self.receiveEnemy( BigWorld.entities[ id ] , receiver )
		self.triggerInterruptCode( receiver, buffData )

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
		DEBUG_MSG( "%i: buff % i [%i] idx:%i loop." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )

		if self._loopRequire:
			if self._loopRequire.validObject( receiver , self ) == csstatus.SKILL_GO_ON:
				self._loopRequire.pay( receiver , self )
			else:
				return False	# 消耗不足则失败
		return True

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		DEBUG_MSG( "%i: buff % i [%i] idx:%i reload." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )
		self.triggerInterruptCode( receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		DEBUG_MSG( "%i: buff % i [%i] idx:%i end." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )

	def getType( self ):
		"""
		返回技能类别
		"""
		return csdefine.BASE_SKILL_TYPE_BUFF

	def getBuffType( self ):
		"""
		返回BUFF类别
		"""
		return self._buffType

	def isBuffType( self, buffType ):
		"""
		virtual method.
		判断自己是否为某一类型
		"""
		return self._buffType == type

	def use( self, caster, target ):
		"""
		virtual method.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		ERROR_MSG( "I do not support this the function!" )

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
		ERROR_MSG( "I do not support this the function!" )
		return csstatus.SKILL_UNKNOW
#
