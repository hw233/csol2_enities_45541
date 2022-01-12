# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.12 2008-08-06 06:11:18 kebiao Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from event.EventCenter import *
import ItemTypeEnum
import csstatus
from Function import Functor
import Math



class Spell_311413( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self.dist = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		self.multiple = 1	#冲锋技能专用，self.multiple为寻路距离/直线距离的倍数

		Spell.init( self, dict )
		
		if dict[ "param1" ] == "":return
		else:self.multiple = float ( dict[ "param1" ] )
		

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
		if target is None:return
		if  hasattr( caster, "vehicleDBID" ) and caster.vehicleDBID:
			return csstatus.SKILL_CANT_USE_ON_VEHICLE
	 	
		#冲锋拐弯的问题
		path_distance = caster.disToPos( target.getObject().position )
		if path_distance > ( Math.Vector3().distTo( caster.position - target.getObject().position ) * self.multiple ): 
			return csstatus.SKILL_NO_PATH   #战斗频道提示 没有可行进路线
		return Spell.useableCheck( self, caster, target )

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		# 对于其他的玩家来说 是没有moveTo的 其他玩家的移动是由他们的客户端通知服务器改变的
		if caster.id == BigWorld.player().id:
			def moveOver( success ):
				caster.onAssaultEnd()						# 原名为：onMovetoProtect，现重命名为 onAssaultEnd( hyw -- 09.01.12 )
				if success:
					# 由于瞬间移动有时候会造成卡 影响快捷栏变色失败 所以这里需要调用消息更新一下
					fireEvent( "EVT_ON_ROLE_MP_CHANGED", caster.MP, caster.MP_Max )
				else:
					DEBUG_MSG( "player move is failed." )
			
			#防止重叠的现象，于是就冲到离目标一段距离的地方，做一个类似的碰撞
			temp_position = None
			dis_pos = 0
			targetEntity = targetObject.getObject()
			dis_pos = caster.distanceBB( caster ) + targetEntity.distanceBB( targetEntity ) #释放者与施展对象BoundingBox的距离
			target_position = targetObject.getObjectPosition()
			caster_position = caster.position
			dir_position = Math.Vector3(target_position - caster_position)
			dir_position.normalise()
			temp_position = target_position + dis_pos * dir_position 
			
			caster.onAssaultStart()							# 原名为：onMovetoProtect，现重命名为 onAssaultStart( hyw -- 09.01.12 )
			caster.moveTo( temp_position, moveOver )


#
# $Log: not supported by cvs2svn $
# Revision 1.11  2008/05/27 08:48:48  kebiao
# 修正了冲锋
#
# Revision 1.9  2008/05/22 06:43:34  kebiao
# no message
#
# Revision 1.8  2008/05/20 03:47:06  kebiao
# no message
#
# Revision 1.7  2008/05/20 02:46:11  kebiao
# 修正冲锋在卡的情况下没有移动到目标身边问题
#
# Revision 1.6  2008/04/30 03:46:16  kebiao
# 增加快捷栏变色处理
#
# Revision 1.5  2008/02/03 06:44:07  kebiao
# 对于其他的玩家来说 是没有moveTo的 其他玩家的移动是由他们的客户端通知服务器改变的
#
# Revision 1.4  2008/01/05 03:47:30  kebiao
# 调整技能结构，目录结构
#
# Revision 1.3  2008/01/03 07:33:06  kebiao
# 调整技能相关接口
#
# Revision 1.2  2007/12/29 04:18:38  kebiao
# add:getFlySpeed
#
# Revision 1.1  2007/12/29 03:37:38  kebiao
# 增加冲锋支持
#
# Revision 1.11  2007/12/14 01:22:42  kebiao
# 将延迟计算增加0.05的误差
#
# Revision 1.10  2007/06/14 10:44:53  huangyongwei
# 整理了全局定义
#
# Revision 1.9  2007/03/22 09:38:58  phw
# method added: getIcon(), 重载了底层函数，实现统一功能
#
# Revision 1.8  2007/03/17 04:26:40  phw
# method added: isNormalAttack()
#
# Revision 1.7  2007/03/17 02:42:44  phw
# 去掉一些不需要的模块引用
#
# Revision 1.6  2007/01/11 07:23:08  kebiao
# 重新调整攻击间隔仍然由此模块判断
#
# Revision 1.5  2007/01/06 04:27:48  kebiao
# 去除攻击间隔判断，改由上层attack.py在攻击的时候判断
#
# Revision 1.4  2006/10/16 09:44:47  phw
# no message
#
# Revision 1.3  2006/07/06 09:35:54  phw
# 删除原来的自动攻击代码，改由role统一实现
#
# Revision 1.2  2006/06/08 09:25:15  phw
# 取消调试信息
#
# Revision 1.1  2006/06/07 05:53:09  phw
# no message
#
#