# -*- coding: gb18030 -*-
#
# 2009-2-3 ���巼
#

import csdefine
import csstatus
from SpellBase import SystemSpell

class Spell_122159018( SystemSpell ):
	"""
	�뿪�չ�ԡ������ʱʩ�Ŵ˼���
	���ڸ�Ϊ----�뿪ָ��������ձ���ֽ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		self._removeBuffIDs = []
		buffIDs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split( "|" )
		for e in buffIDs:
			self._removeBuffIDs.append( int( e ) )

		# ��Ҫ����ƷID����(60101013|60101014|60101015|60101016|60101017|60101018|60101019|60101020)
		self._reqireItems = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split( '|' )

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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		# ������������ͻ��߳������ͻ����ڳ������ڣ����͵�ʵ����д���
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
			for spellBuffID in self._removeBuffIDs:	# ɾ����ɫ�����չ�ԡbuff
				receiver.removeAllBuffByBuffID( spellBuffID, [csdefine.BUFF_INTERRUPT_NONE] )
		"""
		return	# ��ʱreturn����Ϊ����������⣬�߻���Ȼ�ỹҪ�ĵģ�����Ȳ���ɾ��������
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return
		if receiver.isReal() :
			for i in self._reqireItems:
				receiver.removeItemTotal( int(i), 1, csdefine.DELETE_ITEM_SYS_RECLAIM_ITEM )
				#item = receiver.findItemFromNKCK_( int(i) )	# �ж��Ƿ��Ѿ���ֽ����
				#if item != None:
				#	receiver.removeItem_( item.order )		# �Ƴ���������ϵ�ֽ��
		else :
			receiver.receiveOnReal( -1, self )				# ʩ����ID����-1����ʾûʩ����