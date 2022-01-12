# -*- coding: gb18030 -*-

# For updating skill items when the target moves far away or close
# by ganjinxing 2010-11-09

import BigWorld
import event.EventCenter as ECenter
from Function import Functor
from AbstractTemplates import Singleton


class SKItemDetector( Singleton ) :

	def __init__( self ) :
		self.__currTarget = -1											# ��ǰĿ���ID
		self.__triggers = {}

		self.__itemToDist = {}											# ���ӵ������ӳ��
		self.__distToItem = {}											# ���뵽���ӵ�ӳ��
		self.__distToTrap = {}											# ���뵽�����ӳ��

		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		ע���¼�
		"""
		self.__triggers["EVT_ON_TARGET_BINDED"]			= self.__onTargetBinded		# ���ı�ѡ��Ŀ��ʱ������
		self.__triggers["EVT_ON_TARGET_UNBINDED"]		= self.__onTargetUnbinded	# ���ı�ѡ��Ŀ��ʱ������
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __onTargetBinded( self, target ) :
		"""
		�¼�����ѡ��Ŀ��
		"""
		self.updateTarget()
		for pyItem in self.__itemToDist.keys() :						# ��Ϊ�ⲿ���ܻ�ı��ֵ䳤�ȣ����Բ�Ҫ��iterkeys
			pyItem.onDetectorTrigger()

	def __onTargetUnbinded( self, target ) :
		"""
		�¼������Ƴ�Ŀ��
		"""
		self.unbindTarget()
		for pyItem in self.__itemToDist.keys() :						# ��Ϊ�ⲿ���ܻ�ı��ֵ䳤�ȣ����Բ�Ҫ��iterkeys
			pyItem.onDetectorTrigger()

	# -------------------------------------------------
	def __onTrapThrough( self, distInfo, trapEnts ) :
		"""
		ĳ�����崥��
		"""
		trapData = self.__distToTrap.get( distInfo )
		if trapData is None : return									# �ܹ���������ɾ���������Ȼ�лص�
		isEnter = BigWorld.player() in trapEnts
		if trapData[2] == isEnter : return								# �����ж�����Ƿ�Խ������
		trapData[2] = isEnter
		pyItems = self.__distToItem.get( distInfo, [] )
		for pyItem in list( pyItems ) :
			pyItem.onDetectorTrigger()									# Լ���ĸ��·���

	def __createTrap( self, distInfo ) :
		"""
		����ĳ������ε�����
		"""
		player = BigWorld.player()
		if player is None or not player.isPlayer() : return None
		target = player.targetEntity
		if target is None or target is player : return None				# �����ǰû��Ŀ�����Ŀ�����Լ����򲻴���
		trapData = self.__distToTrap.get( distInfo )
		if trapData : return trapData									# �������ζ�Ӧ�������Ѵ��ڣ����ٴ���
		trapFunc = Functor( self.__onTrapThrough, distInfo )			# �ص��������������������ʶ��
		skType, dist = distInfo											# ��ȡ����ĳ��Ⱥͼ��㷽ʽ
		absoDist = DistCalcMap[ skType ]( player, target, dist )
		trapID = target.addTrapExt( absoDist, trapFunc )					# ��������
		trapData = [ trapID, trapFunc, None ]							# �������������ӳ�䣨���һ��None��Ԥ��λ��
		self.__distToTrap[ distInfo ] = trapData
		return trapData

	def __delTrap( self, trapID ) :
		"""
		ɾ��IDΪtrapID������
		"""
		target = BigWorld.entities.get( self.__currTarget )				# ��ȡ��ǰ��Ŀ��
		if target is None : return
		target.delTrap( trapID )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		"""
		�����¼�ʱ����
		"""
		self.__triggers[ evtMacro ]( *args )

	def unbindTarget( self ) :
		"""
		�Ƴ���ǰĿ��
		"""
		target = BigWorld.entities.get( self.__currTarget )				# ��ȡ֮ǰ��Ŀ��
		if target :														# ���֮ǰ��Ŀ�껹��
			for trapData in self.__distToTrap.itervalues() :			# ��֮ǰ�ӵ������ϵ������Ƴ�
				target.delTrap( trapData[0] )
		self.__distToTrap = {}											# ��վ��뵽�����ӳ��
		self.__currTarget = -1

	def updateTarget( self ) :
		"""
		����Ŀ��
		"""
		target = None
		player = BigWorld.player()
		if player and player.isPlayer() :
			target = player.targetEntity
		if target is None or target is player :							# ��ǰû��Ŀ��
			self.unbindTarget()
		elif target.id != self.__currTarget :							# Ŀ�귢���ı�
			self.unbindTarget()
			self.__currTarget = target.id
			for distInfo in self.__distToItem.iterkeys() :				# ���°�һ��Ŀ���
				self.__createTrap( distInfo )							# ����Ŀ�����ϴ�����Ӧ����ε�����

	# -------------------------------------------------
	def bindPyItem( self, pyItem, distInfo ) :
		"""
		��һ�����ܸ��Ӱ󶨵������
		@param		pyItem 		: ���漼�ܽű�ʵ��
		@param		distInfo	: ���¾���: ( "COM", 5 ) ��ͨ���ܣ�����������5�ף�
											( "PET", 10 ) ���＼�ܣ���������10��
		@type		distInfo	: tuple : ( dist, label )
		"""
		self.__createTrap( distInfo )									# ����ĳ������ε�����
		pyItems = self.__distToItem.get( distInfo )						# ���Ҹþ���ε�����
		if pyItems is None :											# �����û�д���
			pyItems = set()												# �򴴽�һ���µ�
			self.__distToItem[ distInfo ] = pyItems
		pyItems.add( pyItem )											# ����������ӵĸ���

		distData = self.__itemToDist.get( pyItem )						# �����ø��Ӷ�Ӧ�ľ�����Ϣ
		if distData is None :											# �����û����Ϣ
			distData = set()											# ���½�һ��
			self.__itemToDist[ pyItem ] = distData
		distData.add( distInfo )										# ���µľ�����Ϣ����
		#print "-------->>> bind item count:", len( self.__itemToDist )

	def unbindPyItem( self, pyItem ) :
		"""
		��һ�����ܸ��Ӵ�������Ƴ�
		@param		pyItem 		: ���漼�ܽű�ʵ��
		"""
		distData = self.__itemToDist.get( pyItem )
		if distData is None : return									# ���û�иø��Ӷ�Ӧ�����ݣ���ֱ���˳�
		for distInfo in distData :
			pyItems = self.__distToItem.get( distInfo )					# ���Ҹ�������
			pyItems.remove( pyItem )									# ���ø����Ƴ�
			if len( pyItems ) : continue								# ����þ���λ����������ӣ������
			trapData = self.__distToTrap.get( distInfo )				# ��������þ������û�и��ӣ�
			if trapData :
				self.__delTrap( trapData[0] )							# �������Ƴ�
				del self.__distToTrap[ distInfo ]						# �������Ӧ�ľ�����Ƴ�
			del self.__distToItem[ distInfo ]							# �����Ӷ�Ӧ�ľ�����Ϣ�Ƴ�
		del self.__itemToDist[ pyItem ]									# �������Ӧ�ĸ��������Ƴ�
		#print "-------->>> leave item count:", len( self.__itemToDist )

	# -------------------------------------------------
	def clearDetector( self ) :
		"""
		���̽����
		"""
		self.unbindTarget()
		self.__itemToDist = {}											# ���ӵ������ӳ��
		self.__distToItem = {}											# ���뵽���ӵ�ӳ��


SKIDetector = SKItemDetector()


#---------------------------------------------------------------------
# ���ܹ�������ļ��㷽��
#---------------------------------------------------------------------
def calcDistInCommon( caster, target, dist ) :
	"""
	��ͨ���ܵĹ���������㷽��
	"""
	tDistBB = target.getBoundingBox().z / 2
	cDistBB = caster.getBoundingBox().z / 2
	return dist + tDistBB + cDistBB										# ��������Ҫ����ģ��ƫ��

def calcDistInPet( caster, target, dist ) :
	"""
	���＼�ܵĹ���������㷽��
	"""
	return dist

# -----------------------------------------------------
DistCalcMap = {
	"COM" : calcDistInCommon,
	"PET" : calcDistInPet,
	}
