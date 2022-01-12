# -*- coding: gb18030 -*-
#
# $Id: SpellPose.py,v 1.10 2008-07-15 06:54:32 kebiao Exp $

"""
SpellPose�ࡣ
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
		@param	speller 	: ����ʩ����
		@return	����������functor  ����True�����򷵻�False
		������������
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

		# �����ʼ����
		intonateNames = rds.spellEffect.getStartAction( skillID, type, vehicleType )
		if len( intonateNames ) == 0: return False
		intonateName = random.choice( intonateNames )
		loopsNames = rds.spellEffect.getLoopAction( skillID, type, vehicleType )
		# û��ѭ��������������ʼ������
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
		@param	speller 	: ����ʩ����
		@type	skillID 	: skillID
		@param	skillID 	: ����ID
		����ʩչ����
		"""
		if speller is None: return
		if not speller.inWorld: return

		type = speller.getWeaponType()
		vehicleType = 0
		if speller.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			vehicleType = speller.vehicleType
		#���� �������ڷ�������Ͻ������Ŷ���
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
		#�������������������Ӧ���Ѿ�Ԥ�Ȳ�����
		#�ظ�����һ������ǰһ������������ɲ�����
		sk = Skill.getSkill( skillID )
		if speller == BigWorld.player() and sk.isHomingSkill() :
			speller.homingAction = castsName
		if not sk.isNotRotate:	# ��Ҫ������ɺ�ת��
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
		@param	speller 	: ����ʩ����
		@type	skillID 	: skillID
		@param	skillID 	: ����ID
		����BUFFʩչ����
		"""
		type = speller.getWeaponType()
		vehicleType = 0
		if speller.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			vehicleType = speller.vehicleType

		castsNames = rds.spellEffect.getCastAction( skillID, type, vehicleType )
		if len( castsNames ) == 0: return False

		speller.playActions( castsNames )   # buff��϶���

		speller.buffAction[skillID] = castsNames

	def buffEnd( self, speller, skillID ):
		"""
		@type	speller 	: entity
		@param	speller 	: ����ʩ����
		@type	skillID 	: skillID
		@param	skillID 	: ����ID
		ֹͣBUFFʩչ����
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
		�����ܻ�����
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
		@param	speller 	: ����ʩ����
		��̬��ֹ��
		"""
		if speller is None: return
		if not speller.inWorld: return
		speller.stopActions()

	def onStartActionEnd( self, speller ):
		"""
		���ֶ���������ϵ�֪ͨ
		���������һ�������ţ���ô�ڲ���ǰ�������õ�ǰ�Ķ�������״̬

		@type	speller 	: entity
		@param	speller 	: ����ʩ����
		"""
		pass


#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/07/08 09:20:09  yangkai
# ������ ��Ч���ü��ط�ʽ
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
# �����ܻ��������Ź���
#
# Revision 1.3  2008/01/25 10:08:43  yangkai
# �����ļ�·���޸�
#
# Revision 1.2  2008/01/23 03:14:50  yangkai
# ��������ֹͣ���ֵ�Bug
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
# Revision 1.29  2008/01/02 01:47:57  yangkai
# ע�͵��Դ���
#
# Revision 1.28  2007/12/29 09:33:16  yangkai
# ������������
#
# Revision 1.27  2007/12/22 08:36:13  yangkai
# ��Ӷ��޶����Ĵ���
#
# Revision 1.26  2007/12/22 07:35:06  yangkai
# �������ܶ�����ʼ������
# �����������Ŵ���
#
# Revision 1.25  2007/12/06 11:49:06  lilian
# added self._action attribute for player action with action rules
#
# Revision 1.24  2007/11/01 03:24:02  kebiao
# ȥ������ʱ��
#
# Revision 1.23  2007/10/26 08:52:03  huangyongwei
# �� Functor �� utils ���Ƶ� common/Function ��
#
# Revision 1.22  2007/09/21 03:27:58  yangkai
# no message
#
# Revision 1.21  2007/09/12 08:42:14  yangkai
# �����˶������ţ�����û��ѭ���������ܳ��ֶϲ������
# ��Ӷ�������ʱ�����ƶ�
#
# Revision 1.20  2007/08/28 09:58:49  yangkai
# no message
#
# Revision 1.19  2007/05/18 10:03:02  yangkai
# ������ƶ�������
# �Ƴ������� ��client/spellpose.xml��������
#
# Revision 1.18  2007/05/05 08:21:19  phw
# whrandom -> random
#
# Revision 1.17  2007/03/09 02:42:33  yangkai
# ����������ʱ��ֹͣ�ƶ�
#
# Revision 1.16  2007/03/08 04:15:31  yangkai
# no message
#
# Revision 1.15  2007/03/07 15:21:46  yangkai
# ȥ�� self.allowmove = false ����spellpose.py���ж�
#
# Revision 1.14  2007/03/07 02:47:56  yangkai
# ������ʩ����ͨ��������ʱ��ʩչ��cast���������ƶ�
#
# Revision 1.13  2007/01/06 09:43:22  yangkai
# Ӧ���˵�Ҫ���Ҹ�....
# �����Ҳ���������ɶҲ����
#
# Revision 1.12  2007/01/05 12:09:56  lilian
# �޸�����Ĵ����������� drugʱ�й��������Ĳ���
# > 		#return _g_spellPoses["NormalAttack"]
#
# > 		# ����ʹ��drugʱ������ͨ���ܹ�������
#
# > 		pass
#
# Revision 1.11  2007/01/04 04:07:05  yangkai
# ����˶��Ҳ��������Ĵ���
#
# Revision 1.10  2007/01/03 07:38:48  lilian
# ȥ���Ҳ���action�����쳣���ж�
#
# Revision 1.9  2006/12/02 08:00:59  lilian
# no message
#
# Revision 1.8  2006/12/02 07:16:37  lilian
# ��� ����Ҳ���action�ټ�һ��caps������һ�ζ���
#
# Revision 1.7  2006/11/25 08:22:37  lilian
# �޸Ĺ�Ч����(����yangkai��lilian�޸ĵ����д���)
#
# Revision 1.6  2006/08/14 07:10:02  wanhaipeng
# Dont raise exception while cant find intonate action.
#
# Revision 1.5  2006/05/26 10:25:15  phw
# no message
#
# Revision 1.4  2006/05/26 08:41:29  wanhaipeng
# Intonate��������Ҳû�С�
#
# Revision 1.3  2006/05/26 07:31:16  wanhaipeng
# ����һ�г����д�����������
#
# Revision 1.2  2006/05/26 07:16:33  wanhaipeng
# interruptʱ�ж�spellAction�Ƿ����.
#
# Revision 1.1  2006/05/26 03:16:59  wanhaipeng
# �µĿͻ���Skillʵ�֡�
#
#