# -*- coding: gb18030 -*-
#
# $Id: Spell_313100003.py,v 1.9 2008-04-16 08:26:50 zhangyuxing Exp $

"""
"""

from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import LostItemDistr
import ECBExtend
import BigWorld
import random

MONSTER_RANGE = 50.0				#������Χ����İ뾶

class Spell_313100003( Spell ):
	"""
	�ٻ�
	�����ٻ��ೡ����������Ŷ������ٻ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )

	def getIntonateTime( self , caster ):
		"""
		virtual method.
		��ȡ�������������ʱ�䣬������ʱ������б�Ҫ�����Ը��������߾��������ʱ����

		@param caster:	ʹ�ü��ܵ�ʵ�塣�����Ժ���չ����ĳЩ�츳��Ӱ��ĳЩ���ܵ�Ĭ������ʱ�䡣
		@type  caster:	Entity
		@return:		�ͷ�ʱ��
		@rtype:			float
		"""
		return caster.queryTemp( "quest_box_intone_time", 0.0 )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#���Ӵ������һ����Χ�ڣ��ҵ������Լ�������֣�������ͨ�����������л������
		receiveScript = target.getObject().getScript()
		monsterList = caster.entitiesInRangeExt( MONSTER_RANGE, "Monster", caster.position )
		for m in monsterList:
			if m.className in ( receiveScript.param1, receiveScript.param4, receiveScript.param7 ):
				if m.bootyOwner[1] == 0 and m.bootyOwner[0] == caster.id:
					return csstatus.SKILL_INTONATING
				if caster.teamMailbox is not None and m.bootyOwner[1] == caster.teamMailbox.id:
					return csstatus.SKILL_INTONATING
		return csstatus.SKILL_GO_ON

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None or entity.isDestroyed:
			return []
		return [ entity ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		# ʩ���߿����Ҳ��� �μ�receiveOnReal�ӿ�
		if not caster:
			return
				
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# �ص����������Լ�ִ��ĳЩ����
		receiver.onReceiveSpell( caster, self )

		receiveScript = receiver.getScript()
		npcConfig = (
			( receiveScript.param1, receiveScript.param2, receiveScript.param3, ),
			( receiveScript.param4, receiveScript.param5, receiveScript.param6, ),
			( receiveScript.param7, receiveScript.param8, receiveScript.param9, ),
		)
		rateInt = random.randint( 0, 100 )
		npcs = []
		for npcID, amount, rate in npcConfig:
			if len( npcID ):
				if rate > rateInt:
					amount = int( amount )
					npcs.extend( [ npcID, ] * amount )


		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# ���ݵȼ�ȡ�õ�����Ʒ�ֲ�ͼ
		direction = receiver.direction
		pos = receiver.position

		# ��ʼ��NPC
		for keyName in npcs:
			itemDistr.pop(0)
			x1, z1 = itemDistr[ random.randint( 0, len( itemDistr ) - 1 ) ]	# ȡ��ƫ��λ��
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# ��������õ�λ��
			entity = receiver.createObjectNearPlanes( keyName, (x, y+2, z), direction, {} )

			# ���ٻ���������������⴦��ֱ��������bootyOwner
			getEnemyTeam = getattr( caster, "getTeamMailbox", None )	# ����ж������¼����mailbox
			if getEnemyTeam and getEnemyTeam():
				entity.bootyOwner = ( caster.id, getEnemyTeam().id )
			else:
				# ����ս��״̬���һ�������˺�Ŀ�꽫����Ϊ������
				entity.bootyOwner = ( caster.id, 0 )
			entity.firstBruise = 1		# ����Monster�е�һ�����˺���bootyOwner����

			#entity.spawnMB = receiver.base
			receiver.getScript().addMonsterCount( receiver, 1 )
			entity.spawnPos = (x, y, z)	# �ƶ�����������׷����Χ
			receiver.entityDead()
			"""
			if self._lifetime > 0:
				# ����һ���Զ���ʧ��time
				entity.addTimer( self._lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
			"""

# $Log: not supported by cvs2svn $
# Revision 1.8  2007/12/27 03:29:54  phw
# method modified: receive(), �����޷���ȷ�ٻ������bug
#
# Revision 1.7  2007/12/27 02:00:39  phw
# method modified: getIntonateTime(), popTemp -> queryTemp
#
# Revision 1.6  2007/12/22 08:23:09  kebiao
# �޸ĵ���ģ��
#
# Revision 1.5  2007/12/22 08:10:18  kebiao
# ��Ϊ����Ϊ�ǹ̶��� ����ǿ����һЩ����
#
# Revision 1.4  2007/12/22 03:26:01  kebiao
# ��������
#
# Revision 1.3  2007/12/22 01:06:12  phw
# method modified: receive(), ��receiver���лص�onReceiveSpell()
#
# Revision 1.2  2007/12/18 05:57:56  kebiao
# ������һЩ������ӿڣ� ��Ϊ�˼���Ϊ�̶�����²Ż�ʹ�õĶ�����������Щ�������
#
# Revision 1.1  2007/12/18 04:16:30  kebiao
# no message
#
#