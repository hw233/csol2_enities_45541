# -*- coding: gb18030 -*-
#
# $Id: Transporter.py,v 1.7 2007-11-23 06:36:07 phw Exp $

"""
Transporter
"""

from bwdebug import *
import NPC
import BigWorld
import GUIFacade
from gbref import rds
import Define

class Transporter( NPC.NPC ):
	"""
	Transporter
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		NPC.NPC.__init__( self )
		self.transportTrapID = 0

	def getRoleAndNpcSpeakDistance( self ):
		"""
		NPC����ҶԻ��ľ���
		"""
		return self.enterRange

	def enterWorld( self ):
		"""
		��������
		"""
		NPC.NPC.enterWorld( self )
		# entity�Ǵ�����
		if self.isTransportDoor:
			self.model = rds.effectMgr.createModel( ["particles/gxcone.model"] )
			rds.effectMgr.createParticleBG( self.model, "HP_root", "particles/chuansongmen/chuansongmen.xml", type = Define.TYPE_PARTICLE_NPC )

			self.transportTrapID = self.addTrapExt(self.enterRange, self.onTransport )

	def leaveWorld( self ):
		"""
		�뿪����
		"""
		NPC.NPC.leaveWorld( self )
		if self.transportTrapID:
			self.delTrap( self.transportTrapID )

	def onTransport( self, entitiesInTrap ):
		"""
		��ҽ����뿪����Ĵ�����
		"""
		# ��ҽ��봫����
		if BigWorld.player() in entitiesInTrap:
			GUIFacade.gossipHello( self )


#
# $Log: not supported by cvs2svn $
# Revision 1.6  2007/06/14 10:32:35  huangyongwei
# ������ȫ�ֺ궨��
#
# Revision 1.5  2007/05/14 06:24:46  panguankong
# �޸Ĵ����ű�־
#
# Revision 1.4  2007/05/14 03:06:43  panguankong
# ɾ���˽���trap��־
#
# Revision 1.3  2007/05/14 00:41:19  panguankong
# ������ɫ�Ի�����ӿڣ�ɾ���Զ��رնԻ�����
#
# Revision 1.2  2007/05/10 03:35:29  panguankong
# �޸Ĵ����ŶԻ��ӿ�
#
# Revision 1.1  2007/05/10 02:26:34  panguankong
# ����ļ�
#
#