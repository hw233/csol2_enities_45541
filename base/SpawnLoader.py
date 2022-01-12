# -*- coding: gb18030 -*-

"""
# ------------------------------------------------------------------------
# space spawn�Ĵ������
# ���˼�룺��һ��space����������Ժ�����space��SpawnLoader(��ǰ��)
#           ע��(����registerSpace())��SpawnLoader�����ŵ������У����ֵ���
#           space����entityʱ����ø�spaceEntity��createSpawnPoint()������
# �ʣ�Ϊʲô��ֱ����ÿ��spaceEntity����ʱ�Լ���������entity��
# ������һ��baseapp���ܻ�ͬʱ�������space�����ÿ��spaceͬʱ����entity��
#     ��ôֻ������ÿ��spaceÿ��ͬʱ���������ģ���10����entity�������baseapp
#     ��entityID����������ٶ�������
# �ʣ�Ϊʲô��Ҫspaceÿ�봴��������entity��ÿ��ֻ����10������ʲô���⣺
# �����ÿ��ֻ����10��entity����ô������ҽ��븱����ʱ�򣬸ø���������Ҫ��
#     ��ʱ����ܰ�entity�����꣬��������Ҹս��븱��ʱ���ܻ�ʲô����������
#     ��ˣ�������Ҫͬʱ���������entity��ʹ����ʱ�価�����١�������ô����
#     �������ͬʱ���������⣬���������Ҫ�෽����أ��縱����entity������Щ��
#     �����ô����ٶȼӿ죬���ڲ�ͬ��baseapp�ﴴ��������
# �ʣ�Ϊʲô������spaceManager�У����Ƿ���ÿ��baseapp�У�
# ���������ĺô���ÿ��baseapp������ͬʱ�����Լ��������ϵ�space��entity��
#     �Դﵽ������Ŀ�ġ�
# ------------------------------------------------------------------------
"""
import Language
import BigWorld
from bwdebug import *
from Function import Functor
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnLoader( BigWorld.Base ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )

		self.spaceInfo 			= []
		self.spawnTimerID 			= 0

	def registerSpace( self, spaceEntity ):
		"""
		define method
		"""
		self.spaceInfo.append(  spaceEntity )
		self.startSpawnEntity()

	def startSpawnEntity( self ):
		"""
		"""
		if self.spawnTimerID == 0:
			INFO_MSG( "Start spawn entity." )
			self.spawnTimerID = self.addTimer( 1, 0.1 )			#�Է�������һ��tick 0.1��Ϊ���ڽ���ˢ��

	# -----------------------------------------------------------------
	# �ص�����
	# -----------------------------------------------------------------
	def onTimer( self, timerID, userData ):
		"""
		ʹ�ûص�����spawnPoint
		"""
		if self.spawnTimerID != timerID:
			ERROR_MSG( "Space spawn timer was be change! please check!!"  )
			return
		
		if len( self.spaceInfo ) == 0:
			self.delTimer( timerID )
			self.spawnTimerID = 0
			return
		
		spaceEntity = self.spaceInfo[0]

		try:
			if not spaceEntity.createSpawnPoint():
				self.spaceInfo.pop( 0 )
		except:
			EXCEHOOK_MSG( "Space (entity className = %s) createSpawnPoint error." % ( spaceEntity.className ) )
			self.spaceInfo.pop( 0 )

# SpawnLoader.py
