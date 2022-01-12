# -*- coding: gb18030 -*-

"""
ʩ����λ

$Id: SpellUnit.py,v 1.27 2008-08-06 06:11:52 kebiao Exp $
"""

import BigWorld
from bwdebug import *
import skills
import GUIFacade
import Define
import csconst
import csdefine
import csstatus
import SkillTargetObjImpl
import event.EventCenter as ECenter
from ActionRule import ActionRule
from gbref import rds
from Function import Functor
from ItemsFactory import BuffItem

class SpellUnit:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.attrBuffs = []			# all buffs and duffs
		self.attrBuffItems = []
		self.triggerSkillDict = {}		#���ڼ�¼��ҿͻ��˴�����������add by wuxo
		self.actionRule = ActionRule()
		self.beHomingCasterID = 0  #��ǰ���ڱ�˭����
		self.actionCount = 0	   #���Ŷ������ô���

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		player = BigWorld.player()
		if self == player or self == player.pcg_getActPet():			# ����Լ��ķŵ���������ͳһ��ʼ��( hyw -- 2008.06.09 )
			return
		self.cell.requestBuffs()

	def leaveWorld( self ) :
		"""
		it will be called, when character leave world
		"""
		pass

	def useSpell( self, skillID, target ):
		"""
		ʹ�ü���
		"""
		self.interuptPendingBuff()
		for pid in BigWorld.player().triggerSkillDict:
			if BigWorld.player().triggerSkillDict[pid] == skillID:
				skillID = pid
				break
		if self.hasSpaceSkill( skillID ):
			self.cell.useSpaceSpell( skillID, target )
		else:
			self.cell.useSpell( skillID, target )

	def interuptPendingBuff( self ):
		"""
		������������Ƴ�δ��buff
		"""
		for buffData in self.attrBuffs:
			if buffData[ "skill" ].getID() == csconst.PENDING_BUFF_ID:
				self.requestRemoveBuff( buffData[ "index" ] )

	# ----------------------------------------------------------------
	# about skill
	# ----------------------------------------------------------------
	def spellInterrupted( self, skillID, reason ):
		"""
		Define method.
		�����ж�

		@type reason: INT
		"""
		INFO_MSG( "%i: spell %i interrupted by %i" % ( self.id, skillID, reason ) )
		try:
			spell = skills.getSkill( skillID )
		except KeyError:
			WARNING_MSG( "%i: skill %i not found." % ( self.id, skillID ) )
			return

		spell.interrupt( self, reason )


	def intonate( self, skillID, intonateTime,targetObject ):
		"""
		Define method.
		��������

		@type skillID: INT
		"""
		INFO_MSG( "%i: intonate %i, time:%i" % ( self.id, skillID, intonateTime ) )
		spell = skills.getSkill( skillID )
		spell.intonate( self, intonateTime,targetObject )

	def castSpell( self, skillID, targetObject ):
		"""
		Define method.
		��ʽʩ�ŷ�����������ʩ��������

		@type skillID: INT
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		spell = skills.getSkill( skillID )
		spell.cast( self, targetObject )

	def receiveSpell( self, casterID, skillID, damageType, damage ):
		"""
		Define method.
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		if skillID != 0:
			spell = skills.getSkill( skillID )
			spell.receiveSpell( self, casterID, damageType, damage )

	def onEndSpellMove(self, casterID):
		if BigWorld.entities.has_key( casterID ):
			caster = BigWorld.entities[ casterID ]
			rds.skillEffect.stopMovingEffects( caster )
	# ----------------------------------------------------------------
	# ��������
	# ----------------------------------------------------------------
	def onStartHomingSpell( self, persistent ):
		"""
		define method.
		��ʼ��������
		"""
		pass

	def onFiniHomingSpell( self ):
		"""
		������������
		"""
		pass

	def onTriggerSpell(self, parentSkillID,skillID):
		"""
		��������������add by wuxo 2012-2-8
		"""
		self.triggerSkillDict[parentSkillID] = skillID
		ECenter.fireEvent( "EVT_ON_SKILL_TRIGGER_SPELL", parentSkillID, skillID )
	# ----------------------------------------------------------------
	# ��λ��ʩ��
	# ----------------------------------------------------------------
	def onSpellToPosition( self, skill ):
		"""
		virtual method.
		�յ�һ����λ��ʩ��������
		"""
		pass
		#ECenter.fireEvent( "EVT_ON_SHOW_SUPERADDTION_BOX" )

	# ----------------------------------------------------------------
	# about buffer
	# ----------------------------------------------------------------
	def onAddBuff( self, buffData ):
		"""
		Define method.
		����һ��buff�������ڻ��һ��buffʱ��֪ͨ��

		@param buffData: see also alias.xml <BUFF>
		@type  buffData: BUFF
		"""
		self._addBuff( buffData )

		if self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
			return

		if buffData["isNotIcon"]: return

		# ���buffʱ��Ҫ��ʾ
		if BigWorld.player().id == self.id :
			self.statusMessage( csstatus.ACCOUNT_STATE_REV_BUFF, buffData["skill"].getName() )
		else:
			if buffData["caster"] == BigWorld.player().id:
				BigWorld.player().statusMessage( csstatus.ACCOUNT_STATE_ADD_BUFF_TO, self.getName(), buffData["skill"].getName() )

	def onReceiveBuff( self, buffData ):
		"""
		Define method.
		�ӷ���������һ��buff�����ڽ����ڱ�����enterWorldʱ�����������Է���buff�б�

		@param buffData: see also alias.xml <BUFF>
		@type  buffData: BUFF
		"""
		self._addBuff( buffData )

	def _addBuff( self, buffData ):
		"""
		���һ��buff
		"""
		sk = buffData["skill"]
		index = buffData["index"]

		# ���ͻ����Ƿ����2��������ͬ��buff�� ������������ԭ����
		# ����ɫ��½��ͻ��˻�δ���������Ҫbuff�б�ʱ�����ڼ�����һ��
		# buff�� �ܵ�����������buff��֪ͨallclients�� �������ǿͻ��˴�����һ��
		# ������buff�� ����֮��ͻ��˽�ɫ��ʼ�����˿�ʼ���������Ҫbuff�б���ʱ
		# �ͻ��˾ͻ���һ��һ����buff��
		for buff in self.attrBuffs:
			if index == buff[ "index" ]:
				return
		self.attrBuffs.append( buffData )
		buffItem = BuffItem( buffData )
		self.attrBuffItems.append( buffItem )

		INFO_MSG( "%i: add buff: %i-%s, index:%i" % ( self.id , sk.getID(), sk.getBuffID(), index ) )

		caster = BigWorld.entities.get( buffData["caster"] )
		# �����浽���ݿ��BUFF��������ߵ�ʱ���ǲ��ܱ�֤�����ҵ�ʩ���ߵ�
		sk.cast( caster, self )	# buff��Ч����

		self.setArmCaps()

		# ����Ƿ���Ҫ�ͻ�����ʾBUFFͼ��
		if buffData["isNotIcon"]: return

		if BigWorld.player().targetEntity and self.id == BigWorld.player().targetEntity.id:
			# ����ѡ���ߵ�BUFF
			ECenter.fireEvent( "EVT_ON_TARGET_BUFFS_CHANGED" )

		if sk.isMalignant() :
			GUIFacade.onAddDuff( self.id, buffData )
		else :
			GUIFacade.onAddBuff( self.id, buffData )

	def onUpdateBuffData( self, buffIndex, buffData ):
		"""
		Define method.
		��һ�������Ѿ����ڵ�ͬ����BUFF or Duff ����׷�Ӳ���
		�����BUFF����׷��ʲô�ɼ̳��߾���
		@param buffsIndex: �������ͬ���͵�BUFF����attrbuffs��λ��
		@param buffData: Ҫ�޸ĵ����ݣ�һ��buff�����ֵ�
		"""
		for idx in range( len(self.attrBuffs) ):
			data = self.attrBuffs[ idx ]
			if data["skill"].getBuffID() == buffData["skill"].getBuffID():
				self.attrBuffs[ idx ] = buffData
				buffIndex = data["index"]
				break
		sk = buffData["skill"]

		# ����Ƿ���Ҫ�ͻ�����ʾBUFFͼ��
		if buffData["isNotIcon"]: return

		if BigWorld.player().targetEntity and self.id == BigWorld.player().targetEntity.id:
			# ����ѡ���ߵ�BUFF
			ECenter.fireEvent( "EVT_ON_TARGET_BUFFS_CHANGED" )
		GUIFacade.onUpdateBDuffData( self.id, buffIndex, buffData, sk.isMalignant() )

	def onRemoveBuff( self, index ):
		"""
		Define method.
		ɾ��buff
		"""
		INFO_MSG( "%i: remove::find buff of index(%i)" % ( self.id, index ) )
		buffData = self.findBuffByIndex( index )
		if not buffData:
			INFO_MSG( "%i: remove::buff [ index:%i ] not found!" % ( self.id, index ) )
			return

		# �Ƴ�buff ʱ, ����ʩ�����Ƿ����,���Ƴ�Ч��
		sk = buffData["skill"]
		INFO_MSG( "%i: remove::buff found [ %s-%i ]" % ( self.id, sk.getBuffID(), sk.getID() ) )
		self.attrBuffs.remove( buffData )
		for buffItem in self.attrBuffItems:
			if buffItem.buffIndex == index:
				self.attrBuffItems.remove( buffItem )

		caster = None
		try:
			caster = BigWorld.entities[ buffData[ "caster" ] ]
		except Exception, e:
			WARNING_MSG( "not find the caster,id is", buffData[ "caster" ] )

		sk.end( caster, self )
		player = BigWorld.player()

		self.setArmCaps()

		# ����Ƿ���Ҫ�ͻ�����ʾBUFFͼ��
		if buffData["isNotIcon"]: return

		if self.id == player.id:
			if not self.hasFlag( csdefine.ROLE_FLAG_HIDE_INFO ):
				self.statusMessage( csstatus.SKILL_BUFF_END, sk.getName()  )

		if player.targetEntity and self.id == player.targetEntity.id:
			# ����ѡ���ߵ�BUFF
			ECenter.fireEvent( "EVT_ON_TARGET_BUFFS_CHANGED" )

		if buffData["skill"].isMalignant() :
			GUIFacade.onRemoveDuff( self.id, index )
		else :
			GUIFacade.onRemoveBuff( self.id, index )


	def findBuffByUID( self, buffUID ):
		"""
		ͨ��uid�ҵ�ĳ��buff
		"""
		for buffData in self.attrBuffs:
			if buffData["skill"].getUID() == buffUID:
				return buffData
		return None

	def findBuffByIndex( self, index ):
		"""
		ͨ��index�ҵ�ĳ��buff
		"""
		for buffData in self.attrBuffs:
			if buffData["index"] == index:
				return buffData
		return None

	def findBuffByBuffID( self, buffID ):
		"""
		ͨ��buffid�ҵ�ĳ��buff
		@buffID: ����
		"""
		# ԭ���Ĵ����е��ң��������ϵ�attrBuffs[x]["skill"].getBuffID()���������ͻ��˵�ȴ���ַ���������ͳһʹ���������� by mushuang
		buffID = int( buffID )
		for buffData in self.attrBuffs:
			if int( buffData["skill"].getBuffID() ) == buffID:
				return buffData
		return None

	def findBuffByID( self, ID ):
		"""
		ͨ��ID����ĳ��buff
		"""
		ID = int( ID )
		for buffData in self.attrBuffs:
			if buffData["skill"].getID() == ID :
				return buffData
		return None

	def getSourceTypeByBuffIndex( self, buffIndex ):
		"""
		��ȡbuff��С�ࣨbuff��Դ��
		"""
		buffData = self.findBuffByIndex( buffIndex )
		if buffData:
			return buffData["sourceType"]
		else :
			return csdefine.BUFF_ORIGIN_NONE

	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		self.actionCount = 0  # �ÿղ��Ŷ������ô���

	def playActions( self, actionNames ):
		"""
		���Ŷ���
		param actionName	: �������б�
		type actionName		: list of string
		return				: None
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return
		delActionNames = []
		for actionName in actionNames:
			if model and not model.hasAction( actionName ):
				delActionNames.append( actionName )
		for actionName in delActionNames:
			actionNames.remove( actionName )
		if len( actionNames ) == 0: return
		func = Functor( self.onActionOver, actionNames )
		isPlay = self.actionRule.playActions( model, actionNames, functor = func )
		if isPlay:
			self.onPlayActionStart( actionNames )
		else:
			if hasattr( self, "className"):
				DEBUG_MSG( "Entity(className: %s ):action was stopped for priority! currActions:%s, newActions:%s"%( self.className, str(self.actionRule.currActionNames),str(actionNames) ) )

	def onPlayActionStart( self, actionNames ):
		"""
		��ʼ���Ŷ�����ʱ������ʲô...
		"""
		if actionNames == []: return  # �ն���������
		self.actionCount += 1

	def onActionOver( self, actionNames ):
		"""
		����������ɻص�
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return
		# ����ĳЩ��������¶����ص���bug
		if actionNames == self.getActionNames() and self.actionCount >= 2:
			actionCount = self.actionCount
			self.onPlayActionOver( actionNames )
			self.actionCount = actionCount - 1  # ��������²��������������
			return
		self.actionRule.onActionOver( actionNames )
		self.onPlayActionOver( actionNames )

	def onPlayActionOver( self, actionNames ):
		"""
		���Ŷ���������ʱ������ʲô...
		"""
		self.actionCount = 0

	def getActionNames( self ):
		"""
		���ص�ǰ���Ŷ����б�
		"""
		if not self.inWorld: return []
		return self.actionRule.getActionNames()

	def stopActions( self ):
		"""
		define method.
		ֹͣ��ǰ���ŵĶ���
		"""
		if not self.inWorld: return
		model = self.getModel()
		if model is None: return

		actionNames = self.getActionNames()
		for actionName in actionNames:
			rds.actionMgr.stopAction( model, actionName )

	def isActionning( self ):
		"""
		��ǰ�Ƿ��ڲ��Ŷ���
		"""
		if not self.inWorld: return False
		return self.actionRule.isActionning()

	def onHomingSpellResist( self, targetID ):
		"""
		define method.
		�������ܱ��ֿ���Ŀ��ID
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_REST_STATUS", targetID )

	def showSkillName( self, skillID ):
		"""
		��ʾ��������
		"""
		pass
	
	def setArmCaps( self ) :
		"""
		����ƥ��caps
		"""
		pass
	
	def actionStateMgr( self, state = Define.COMMON_NO ):
		"""
		�������Ź���(����)
		state ��ǰ��״̬
		"""
		model = self.getModel()
		if model is None:
			return False
		
		#�������Ծ״̬�Ͳ������ܻ�����
		for actionName in model.queue:
			if actionName.startswith( "jump" ):
				return False
		
		#�޵�״̬/����״̬�������κ��ܻ�
		if self.effect_state & (csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_HEGEMONY_BODY ) > 0:
			return  False
		
		#����״̬�º�����ͨ�ܻ�
		if state == Define.COMMON_BE_HIT and hasattr( self, "intonating" ) and self.intonating():
			return  False
		
		#��������������ͨ�ܻ�
		if state == Define.COMMON_BE_HIT and hasattr( self, "isInHomingSpell" ) and self.isInHomingSpell:
			return False
		
		#�����ܻ�������ͨ�ܻ�
		if state == Define.COMMON_BE_HIT and self.effect_state & csdefine.EFFECT_STATE_BE_HOMING: 
			return  False
		
		return True
		
# SpellUnit.py
