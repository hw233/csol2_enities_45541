# -*- coding: gb18030 -*-
#

#
"""

"""

from Monster import Monster
import Love3
import csdefine
import BigWorld

class LiuWangMuBoss( Monster ):
	"""
	�ع�����Ĺboss�ű�
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )

	def onLiuWangMuBossDieNotify( self, notifyStr ):
		"""
		����֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( notifyStr, [] )