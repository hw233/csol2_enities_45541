# -*- coding: gb18030 -*-

"""
����ڵ�Ѱ·����ģ��
"""
import BigWorld
import ResMgr
import math

QUEST_PATROL_MODEL   = "space/tong_yong/za_wu/za_wu/ty_jian_tou_001.model" #ָ����ͷģ��
NEAR_PATROL_DISTANCE = 3.0  #ɾ����ͷ�ľ���  ����3�׾�ɾ����ͷ
CALLBACK_TIME        = 0.5 #������ص� �ж�����߹��˵�·��
SHOW_MODEL_MOUNT	 = 5	#ֻ��ʾδ�߹��ڵ�ǰ���5��ָ��ģ��

class QuestPatrolMgr():
	"""
	�ڵ�Ѱ·����ģ��
	"""
	def __init__(self):
		self.patrolDatas = [] #����˳�� ·����Ϣ
		self.models = [] #��ӵ�������ϵ�ģ�� ��˳�򣬺�·���Ӧ
		self.cbid = 0
		self.modelPath = QUEST_PATROL_MODEL

	def loadDatas( self, path ):
		"""
		��ȡ�ڵ�·����Ϣ
		"""
		patrolInfos = {} #����·��������ֵ�
		data = ResMgr.openSection( path )
		if data is not None:
			for k,v in data.items():
				patrolInfos[ k ] = {}
				patrolInfos[ k ][ "position" ] = v.readVector3( "worldPosition" )
				patrolInfos[ k ][ "userString" ] = v.readFloat( "userString", 0.0 ) * math.pi /180.0
				for k1, v1 in v.items():
					if k1 == "link":
						patrolInfos[ k ][ "nextID" ] = v1.readString("to")

		firstID = self.getFisrtID( patrolInfos )
		self.patrolDatas = []
		self.models = []
		i = 0
		while i < len( patrolInfos ):
			if not patrolInfos.has_key( firstID ): return
			pos = patrolInfos[ firstID ][ "position" ]
			pitch = patrolInfos[ firstID ][ "userString" ]
			yaw = 0.0
			if patrolInfos[firstID].has_key( "nextID" ):
				new_firstID = patrolInfos[ firstID ]["nextID"]
				next_pos = patrolInfos[ new_firstID ][ "position" ]
				yaw = ( next_pos - pos ).yaw
				firstID = new_firstID
			self.patrolDatas.append( ( pos, pitch, yaw ) )
			i += 1

	def getFisrtID( self, patrolInfos ):
		"""
		��ȡ��һ�����ID
		"""
		nextIDs = []
		allIDs = patrolInfos.keys()
		for k in allIDs:
			if patrolInfos[ k ].has_key( "nextID"):
				nextIDs.append( patrolInfos[ k ][ "nextID" ] )
		firstIDL = list( set( allIDs ) - set( nextIDs ) )
		if len( firstIDL ) != 1:
			return None
		else:
			return firstIDL[ 0 ]

	def showPatrol( self, path, model ):
		"""
		��ʾ�ڵ�Ѱ·��
		"""
		player = BigWorld.player()
		for pyModel in self.models:	# ��յ���һ��·����model
			if pyModel in list( player.models ):
				player.delModel( pyModel )
		self.modelPath = model
		self.loadDatas( path )
		self.showAllGuide()

	def showAllGuide( self ):
		"""
		��ʾ����ָ����ͷ
		"""
		p = BigWorld.player()
		for i in range( len( self.patrolDatas ) ):
			patrol = self.patrolDatas[i]
			model = BigWorld.Model( self.modelPath )
			p.addModel( model )
			model.position = patrol[0]
			model.pitch = patrol[1]
			model.yaw = patrol[2] + math.pi #ģ�ͳ���ͼ�ͷ�������ƫ��math.pi
			model.visible = False
			self.models.append( model )
		for idx in range( SHOW_MODEL_MOUNT ):	# ��ʾǰ5��
			if idx > len( self.models ) - 1: continue
			self.models[idx].visible = True
		self.onArrivePatrol()

	def onArrivePatrol( self ):
		"""
		�ص����� �ж��Ѿ��߹���·��
		"""
		p = BigWorld.player()
		if len( self.models ) == 0:
			p.onArrivePatrol()
			return
		passedPatrol = []
		for i in range( len( self.models ) ):
			dis = ( self.models[i].position - p.position ).length
			if dis <= NEAR_PATROL_DISTANCE:
				passedPatrol.append( i )
		passedPatrol.sort()
		if len( passedPatrol ) > 0: #˵���Ѿ��߹���ĳЩ��
			for idx in range( passedPatrol[-1] + 1 ):
				pyModel = self.models[idx]
				if pyModel in list( p.models ):
					p.delModel( pyModel )
			for idx in range( passedPatrol[-1] + 1, passedPatrol[-1] + SHOW_MODEL_MOUNT + 1 ):
				if idx > len( self.models ) - 1: continue
				self.models[idx].visible = True
			self.models = self.models[ passedPatrol[-1] + 1: ]
		self.cbid = BigWorld.callback( CALLBACK_TIME, self.onArrivePatrol )

patrolMgr = QuestPatrolMgr()
