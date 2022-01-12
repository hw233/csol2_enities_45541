# -*- coding: gb18030 -*-
#
# $Id: Buff.py,v 1.20 2008-08-06 06:11:09 kebiao Exp $

"""
Buff类。
"""
import BigWorld
from bwdebug import *
from SkillBase import SkillBase
import GUIFacade
from event.EventCenter import *
import csdefine
import csstatus
from gbref import rds
from Function import Functor

class Buff( SkillBase ):
	def __init__( self ):
		"""
		"""
		SkillBase.__init__( self )
		self._sourceSkillID = 0								# 源技能的ID (由源技能初始化)
		self._sourceSkillIdx = 0							# 该BUFF在源技能身上的位置(由源技能初始化)

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type  dict:			python 字典
		"""
		SkillBase.init( self, dict )

	def setSource( self, sourceSkillID, sourceIndex ):
		"""
		设置源技能信息
		"""
		self._sourceSkillID = sourceSkillID
		self._sourceSkillIdx = sourceIndex

	def getSourceSkillID( self ):
		"""
		获得源技能的ID
		"""
		return self._sourceSkillID

	def isBenign( self ):
		"""
		virtual method.
		判断效果是否为良性
		"""
		return self.getEffectState() == csdefine.SKILL_EFFECT_STATE_BENIGN

	def isMalignant( self ):
		"""
		virtual method.
		判断效果是否为恶性
		"""
		return self.getEffectState() == csdefine.SKILL_EFFECT_STATE_MALIGNANT

	def getEffectState( self ):
		return self._datas[ "EffectState" ]	# buff 的效果类型；1 良性；0 未定义（中性）；-1 恶性

	def getBuffType( self ):
		"""
		virtual method.
		获取该BUFF的类别
		"""
		if self._datas.has_key( "Type" ):
			return self._datas[ "Type" ]
		return csdefine.BUFF_TYPE_NONE			# BUFF类别

	def getID( self ):
		"""
		获取他的 技能ID
		"""
		return ( self._sourceSkillID * 100 ) + self._sourceSkillIdx + 1 #sourceIndex + 1 是因为BUFF程序ID实际是技能ID+BUFF所在的索引 如果不加1 那么skillID+0=skillID

	def getEffectID( self ):
		"""
		获取BUFF的效果ID
		"""
		return ( self._sourceSkillID/1000 * 100 ) + self._sourceSkillIdx + 1

	def getIcon( self ):
		"""
		重载buff的图标获得方法
		"""
		return rds.spellEffect.getIcon( self.getEffectID() * 1000 )

	def getType( self ):
		"""
		@return: 技能类型
		"""
		return csdefine.BASE_SKILL_TYPE_BUFF			# 技能类别 （强制为BUFF 因为BUFF实际也是技能系统中的一员，所以他们都有一个系列的Type分类）

	def getBuffID( self ):
		"""
		取得BUFF真正的编号 BUFFID (由于BUFFID使用了技能*N组成的ID 因此这个ID为真正的BUFFID)
		"""
		return self._datas[ "ID" ]

	def getPersistent( self ) :
		"""
		获取 buff 的持续时间
		hyw -- 2008.09.24
		"""
		return self._datas[ "Persistent" ]

	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		# self._buffID * 1000 的原因是为了方便光效读取那边不用大费周章
		# 转换这个ID，因为buff的光效配置和技能的是一样，但是技能有很多级别
		# 如：技能322718001 ，其中322718就是爆裂火球的ID
		# 后面001表示一级的。光效配置那边就是转换后以322718为技能的ID配置的
		# 所以 这里self._buffID * 1000，方便统一读取
		self.playEffect( caster, target )

	def playEffect( self, caster, target ):
		"""
		播放buff效果
		"""
		skillID = self.getEffectID() * 1000
		if hasattr( caster,"isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( rds.skillEffect.playBuffEffects, caster, target, skillID ) )
		else:
			rds.skillEffect.playBuffEffects( caster, target, skillID )
	
		# buff动作效果，一般体现在BUFF接受者身上
		self.pose.buffCast( target, skillID )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		skillID = self.getEffectID() * 1000
		rds.skillEffect.stopBuffEffects( caster, target, skillID )
		self.pose.buffEnd( target, skillID )

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#这里会出错误的原因是 在服务器上一个entity对另一个entity施法 服务器上是看的到施法者的
				#而客户端可能会因为某原因 如：网络延迟 而在本机没有更新到AOI中的那个施法者entity所以
				#会产生这种错误 written by kebiao.  2008.1.8
				casterID = 0

		# 回调伤害信息 不一定伤害到HP 可能是0 被闪躲了 但仍然算伤害
		target.onReceiveDamage( casterID, self, damageType, damage  )
		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage  )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		技能产生伤害时的动作效果等处理
		@param player:			玩家自己
		@type player:			Entity
		@param target:			Spell施放的目标Entity
		@type target:			Entity
		@param caster:			Buff施放者 可能为None
		@type castaer:			Entity
		@param damageType:		伤害类型
		@type damageType:		Integer
		@param damage:			伤害数值
		@type damage:			Integer
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return

		casterID = 0
		if caster:
			rds.skillEffect.playHitEffects( caster, target, self.getEffectID() * 1000 )
			casterID = caster.id
#
# $Log: not supported by cvs2svn $
# Revision 1.19  2008/08/06 06:09:49  qilan
# method modify：_SkillAE()更名为_skillAE()
#
# Revision 1.18  2008/08/06 03:31:08  kebiao
# 调整receiveDamage接口参数 skill.receiveSpell 去掉skillID
#
# Revision 1.17  2008/08/05 02:03:19  qilan
# 将函数_receiveDamageAE()改名为_SkillAE()
# 去掉系统信息相关的两个函数_receiveDamageSysInfo()/_receiveDamageFlyText()
# 注：伤害系统信息放到受法者的entity中
#
# Revision 1.16  2008/07/31 09:15:25  qilan
# 加入了角色受到Debuff伤害的数字跳出显示
#
# Revision 1.15  2008/07/21 03:04:22  huangyongwei
# caster.pcg_getOutPet(),
# 改为
# caster.pcg_getActPet(),
#
# Revision 1.14  2008/07/15 06:54:32  kebiao
# 技能参数统一使用section 因为python变量会产生大量的内存，Language.section
# 是C结构存储 将会降低内存消耗
#
# Revision 1.13  2008/07/09 01:33:35  kebiao
# 添加伤害回调函数
#
# Revision 1.12  2008/06/30 06:20:09  kebiao
# 修正    self._receiveDamageAE( player, target, caster, param1, param2, skillID )
# UnboundLocalError: local variable 'caster' referenced before assignment
#
# Revision 1.11  2008/05/30 03:06:16  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.10  2008/04/17 06:42:32  wangshufeng
# SKILL_EFFECT_STATE_BENIGN -> csdefine.SKILL_EFFECT_STATE_BENIGN
#
# Revision 1.9  2008/03/31 09:05:00  kebiao
# 修改receiveDamage和通知客户端接受某技能结果分开
# 技能通过receiveSpell通知客户端去表现，支持各技能不同的表现
#
# Revision 1.8  2008/03/18 07:52:11  kebiao
# 修正了宠物攻击的相关提示信息
#
# Revision 1.7  2008/02/25 09:27:27  kebiao
# 增加伤害反弹提示
#
# Revision 1.6  2008/02/22 02:57:34  kebiao
# 增加宠物攻击冒血显示
#
# Revision 1.5  2008/01/31 07:20:45  kebiao
# 增加战斗信息
#
# Revision 1.4  2008/01/25 10:08:43  yangkai
# 配置文件路径修改
#
# Revision 1.3  2008/01/24 07:37:00  kebiao
# modify buffid is 0
#
# Revision 1.2  2008/01/24 07:07:11  kebiao
# add method:getBuffID
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
#