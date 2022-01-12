# -*- coding: gb18030 -*-
#
# $Id: SpellPose.py,v 1.10 2008-07-15 06:54:32 kebiao Exp $

"""
SpellPose类。
"""

from bwdebug import *
from Function import Functor
import BigWorld
import Language
import random
import Define
from gbref import rds
import csdefine
import csconst
import skills as Skill

class SpellPose:

	def __init__( self ):
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def intonate( self, speller, skillID, functor ):
		"""
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		@return	正常调用了functor  返回True，否则返回False
		播放吟唱动作
		"""
		if speller is None: return
		if not speller.inWorld: return

		speller.loopAction = ""
		spellerModel = speller.getModel()
		type = speller.getWeaponType()
		vehicleType = 0
		if speller.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			vehicleType = speller.vehicleType
		if hasattr( speller, "stopMove"):
			speller.stopMove()

		# 随机起始动作
		intonateNames = rds.spellEffect.getStartAction( skillID, type, vehicleType )
		if len( intonateNames ) == 0: return False
		intonateName = random.choice( intonateNames )
		loopsNames = rds.spellEffect.getLoopAction( skillID, type, vehicleType )
		# 没有循环动作，播放起始动作先
		if len( loopsNames ) == 0:
			speller.playActions( [intonateName] )
			return True
		loopsName = random.choice( loopsNames )
		speller.playActions( [intonateName, loopsName] )
		speller.loopAction = loopsName
		return True

	def cast( self, speller, skillID, targetObject ):
		"""
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		@type	skillID 	: skillID
		@param	skillID 	: 技能ID
		播放施展动作
		"""
		if speller is None: return
		if not speller.inWorld: return

		type = speller.getWeaponType()
		vehicleType = 0
		if speller.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			vehicleType = speller.vehicleType
		#增加 如果玩家在飞行骑宠上将不播放动作
		if vehicleType == Define.VEHICLE_MODEL_STAND:
			return False
		castsNames = rds.spellEffect.getCastAction( skillID, type, vehicleType )
		if len( castsNames ) == 0: return False
			
		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			if speller.nAttackOrder >= len( castsNames ):
				speller.nAttackOrder = 0
			castsName = castsNames[speller.nAttackOrder]
			speller.nAttackOrder += 1
		else:
			castsName = random.choice( castsNames )
		#如果有吟唱动作，动作应该已经预先播放了
		#重复播放一个动作前一个动作会算完成播放了
		sk = Skill.getSkill( skillID )
		if speller == BigWorld.player() and sk.isHomingSkill() :
			speller.homingAction = castsName
		if not sk.isNotRotate:	# 需要动作完成后转向
			speller.rotateTarget = targetObject
			speller.rotateAction = castsName
		if hasattr( speller, "stopMove"): speller.stopMove()
		if hasattr( speller,"isLoadModel" ) and speller.isLoadModel :
			speller.delayActionNames = [castsName] 
		else:
			speller.playActions( [castsName] )
		return True

	def buffCast( self, speller, skillID ):
		"""
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		@type	skillID 	: skillID
		@param	skillID 	: 技能ID
		播放BUFF施展动作
		"""
		type = speller.getWeaponType()
		vehicleType = 0
		if speller.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			vehicleType = speller.vehicleType

		castsNames = rds.spellEffect.getCastAction( skillID, type, vehicleType )
		if len( castsNames ) == 0: return False

		speller.playActions( castsNames )   # buff组合动作

		speller.buffAction[skillID] = castsNames

	def buffEnd( self, speller, skillID ):
		"""
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		@type	skillID 	: skillID
		@param	skillID 	: 技能ID
		停止BUFF施展动作
		"""
		if speller is None: return
		if not speller.inWorld: return
		model = speller.getModel()
		if model is None: return

		data = speller.buffAction
		if skillID not in data: return
		actionNames = data.pop( skillID )
		for actionName in actionNames:
			rds.actionMgr.stopAction( model, actionName )

		for actionName in data.itervalues():
			speller.playActions( actionName )
			break

	def hit( self, skillID, target ):
		"""
		播放受击动作
		"""
		if target is None: return
		
		if target.actionStateMgr( Define.COMMON_BE_HIT ):
			weaponType = target.getWeaponType()
			vehicleType = 0
			if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				vehicleType = target.vehicleType
			actionNames = rds.spellEffect.getHitAction( skillID, weaponType, vehicleType )
			
			target.playActions( actionNames )

	def interrupt( self, speller ):
		"""
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		姿态中止。
		"""
		if speller is None: return
		if not speller.inWorld: return
		speller.stopActions()

	def onStartActionEnd( self, speller ):
		"""
		起手动作播放完毕的通知
		如果还有下一动作播放，那么在播放前可以设置当前的动作播放状态

		@type	speller 	: entity
		@param	speller 	: 动作施放者
		"""
		pass


#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/07/08 09:20:09  yangkai
# 修正了 光效配置加载方式
#
# Revision 1.8  2008/06/27 07:47:03  phw
# method modified: cast(), "cancelSeek" --> "stopMove"
#
# Revision 1.7  2008/04/12 02:13:09  yangkai
# no message
#
# Revision 1.6  2008/03/28 03:56:33  yangkai
# no message
#
# Revision 1.5  2008/03/25 03:36:42  yangkai
# no message
#
# Revision 1.4  2008/03/11 04:07:53  yangkai
# 修正受击动作播放规则
#
# Revision 1.3  2008/01/25 10:08:43  yangkai
# 配置文件路径修改
#
# Revision 1.2  2008/01/23 03:14:50  yangkai
# 修正动作停止出现的Bug
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
# Revision 1.29  2008/01/02 01:47:57  yangkai
# 注释调试代码
#
# Revision 1.28  2007/12/29 09:33:16  yangkai
# 调整动作播放
#
# Revision 1.27  2007/12/22 08:36:13  yangkai
# 添加对无动作的处理
#
# Revision 1.26  2007/12/22 07:35:06  yangkai
# 调整技能动作初始化代码
# 调整动作播放代码
#
# Revision 1.25  2007/12/06 11:49:06  lilian
# added self._action attribute for player action with action rules
#
# Revision 1.24  2007/11/01 03:24:02  kebiao
# 去掉持续时间
#
# Revision 1.23  2007/10/26 08:52:03  huangyongwei
# 将 Functor 从 utils 中移到 common/Function 中
#
# Revision 1.22  2007/09/21 03:27:58  yangkai
# no message
#
# Revision 1.21  2007/09/12 08:42:14  yangkai
# 修正了动作播放，修正没有循环动作可能出现断层的问题
# 添加动作播放时不能移动
#
# Revision 1.20  2007/08/28 09:58:49  yangkai
# no message
#
# Revision 1.19  2007/05/18 10:03:02  yangkai
# 重新设计动作播放
# 移除动作对 “client/spellpose.xml”的依赖
#
# Revision 1.18  2007/05/05 08:21:19  phw
# whrandom -> random
#
# Revision 1.17  2007/03/09 02:42:33  yangkai
# 修正攻击的时候停止移动
#
# Revision 1.16  2007/03/08 04:15:31  yangkai
# no message
#
# Revision 1.15  2007/03/07 15:21:46  yangkai
# 去除 self.allowmove = false 放在spellpose.py中判断
#
# Revision 1.14  2007/03/07 02:47:56  yangkai
# 修正：施放普通攻击或技能时候，施展完cast动作才能移动
#
# Revision 1.13  2007/01/06 09:43:22  yangkai
# 应狼人的要求，我改....
# 技能找不到动作，啥也不做
#
# Revision 1.12  2007/01/05 12:09:56  lilian
# 修改下面的代码以消除吃 drug时有攻击动作的播放
# > 		#return _g_spellPoses["NormalAttack"]
#
# > 		# 消除使用drug时出现普通技能攻击动作
#
# > 		pass
#
# Revision 1.11  2007/01/04 04:07:05  yangkai
# 添加了对找不到动作的处理。
#
# Revision 1.10  2007/01/03 07:38:48  lilian
# 去掉找不到action引起异常的判断
#
# Revision 1.9  2006/12/02 08:00:59  lilian
# no message
#
# Revision 1.8  2006/12/02 07:16:37  lilian
# 添加 如果找不到action再加一遍caps、再找一次动作
#
# Revision 1.7  2006/11/25 08:22:37  lilian
# 修改光效播放(包括yangkai和lilian修改的所有代码)
#
# Revision 1.6  2006/08/14 07:10:02  wanhaipeng
# Dont raise exception while cant find intonate action.
#
# Revision 1.5  2006/05/26 10:25:15  phw
# no message
#
# Revision 1.4  2006/05/26 08:41:29  wanhaipeng
# Intonate动作可能也没有。
#
# Revision 1.3  2006/05/26 07:31:16  wanhaipeng
# 改了一行程序都有错。。。。。。
#
# Revision 1.2  2006/05/26 07:16:33  wanhaipeng
# interrupt时判断spellAction是否存在.
#
# Revision 1.1  2006/05/26 03:16:59  wanhaipeng
# 新的客户端Skill实现。
#
#