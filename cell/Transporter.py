# -*- coding: gb18030 -*-
#
# $Id: Transporter.py,v 1.6 2007-11-23 06:36:22 phw Exp $

"""
Transporter
"""

from bwdebug import *
import NPC
import BigWorld
import Love3
import csstatus
import cschannel_msgs

class Transporter( NPC.NPC ):
	"""
	Transporter
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		NPC.NPC.__init__( self )

	def isInteractionRange( self, entity ):
		"""
		�ж�һ��entity�Ƿ����Լ��Ľ�����Χ��
		"""
		return self.position.flatDistTo( entity.position ) < self.enterRange + 1 # ������ʱ�����ڷ�Χ����Ӵ�1��

	# �ش�
	def transportDialog( self, srcEntityID, talkID ):
		"""
		virtual method.
		exposed method.
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param srcEntityID: ˵�������ID
		@type  srcEntityID: EntityID
		@param       talkID: �Ի��ؼ���
		@type        talkID: str
		@return: ��
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# ���Ӧ����Զ�������ܵ���
			return

		if self.isTransportDoor:
			if not self.isInteractionRange( playerEntity ):
				WARNING_MSG( "%s(%i): target too far." % (playerEntity.playerName, playerEntity.id) )
				return
		else:
			if not NPC.NPC.isInteractionRange( self, playerEntity ):
				WARNING_MSG( "%s(%i): target too far." % (playerEntity.playerName, playerEntity.id) )
				return

		transportHistory = playerEntity.transportHistory

		# �Ի�����
		if talkID == "Talk":
			# ��Ǵ�����
			if not transportHistory & self.transportSign:
				playerEntity.tagTransport( self.transportSign )
				transportHistory = transportHistory & self.transportSign

			# ��client��ʾ�Ѿ�����Ĵ�����
			show = False
			for space, value in Love3.g_transporterData.getData().iteritems():
				for sign, sect in value.iteritems():
					if transportHistory & sign and sign != self.transportSign:
						self.addGossipOption( playerEntity, "DOOR" + str(sign), sect["name"] )
						show = True
			if show:
				self.setGossipText( playerEntity, cschannel_msgs.CELL_Transporter_1 )
				if self.isTransportDoor:
					self.sendGossipComplete( playerEntity )
		else:
			# ѡ����
			for space, value in Love3.g_transporterData.getData().iteritems():
				for sign, sect in value.iteritems():
					if transportHistory & sign and str(sign) == talkID[4:]:
						self.endGossip( playerEntity )
						playerEntity.gotoSpace( space, sect["pos"], sect["direction"] )
						break

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2007/05/14 06:25:23  panguankong
# �޸Ĵ����ű�־
#
# Revision 1.4  2007/05/14 05:40:34  phw
# method modified: transportDialog(), playerEntity.goto -> playerEntity.gotoSpace
#
# Revision 1.3  2007/05/14 00:36:15  panguankong
# �޸Ĵ����ŶԻ��ӿ�
#
# Revision 1.2  2007/05/10 03:36:13  panguankong
# �޸Ĵ����ŶԻ��ӿ�
#
# Revision 1.1  2007/05/10 02:26:50  panguankong
# ����ļ�
#
#