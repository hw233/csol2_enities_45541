# -*- coding: gb18030 -*-
#
# $Id: Spell_313100001.py,v 1.9 2008-08-13 03:42:15 phw Exp $

"""
"""

from bwdebug import *
import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine
import BigWorld

g_items = items.instance()

class Spell_313100005( Spell ):
	"""
	������	�򿪱����ೡ����������Ŷ�����������Ʒ
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

		receiver.onReceiveSpell( caster, self )

		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# ���ݵȼ�ȡ�õ�����Ʒ�ֲ�ͼ
		itemDistr.pop(0)	# ȥ����0λ,��Ϊ��0λ����������,������
		direction = (0.0, 0.0, 0.0)
		pos = receiver.position

		#  ������ȡ����
		propDict = { "ownerIDs": [caster.id] }
		receiveScript = receiver.getScript()
		items = list( receiveScript.items )
		minAmount = receiveScript.param6
		maxAmount = receiveScript.param7
		dropAmount = random.randint( minAmount, maxAmount )

		# ��ʼ�ŵ���
		itemkeyList = []

		while ( len( itemkeyList ) < dropAmount ):
			item = random.choice( items )    # item��ʽ( itemID,amount,rate )
			if len( item[0] ) == 0:
				items.remove( item )
				continue
			if random.random() > item[2]:	continue
			items.remove( item )
			for  i in xrange( item[1] ):
				if len( itemkeyList ) < dropAmount:
					itemkeyList.append( item[0] )
				else:break

		itemList = []
		for itemKey in itemkeyList:
			item = g_items.createDynamicItem( int( itemKey ) , 1 )
			itemList.append( item )

		x1, z1 = itemDistr.pop(0)										# ȡ��ƫ��λ��
		x, y, z = x1 + pos[0], pos[1], z1 + pos[2]
		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperName" : receiver.queryTemp( "bossName", "" ) }
		itemBox = caster.createEntityNearPlanes( "DroppedBox", (x, y, z), ( 0,0,0 ), params )
		itemBox.init( ( caster.id, 0 ), itemList )
		receiver.destroy()

# $Log: not supported by cvs2svn $
# Revision 1.8  2008/04/16 08:26:40  zhangyuxing
# ��ReceiverObjectʵ������һ���������������ṩ��رȽ���Ϣ��
#
# Revision 1.7  2007/12/27 02:00:39  phw
# method modified: getIntonateTime(), popTemp -> queryTemp
#
# Revision 1.6  2007/12/22 09:05:54  phw
# method modified: receive(), �����˶�keyNameΪ""ʱ��bug
#
# Revision 1.5  2007/12/22 08:23:09  kebiao
# �޸ĵ���ģ��
#
# Revision 1.4  2007/12/22 08:10:18  kebiao
# ��Ϊ����Ϊ�ǹ̶��� ����ǿ����һЩ����
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