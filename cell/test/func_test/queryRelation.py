# -*- coding: utf-8 -*-
import BigWorld
import csdefine
from ObjectScripts.GameObjectFactory import g_objFactory


def Monster_queryRelation( ):

	spaceID = BigWorld.entities.values()[100].spaceID

	m = g_objFactory.getObject( "20321001" ).createEntity( spaceID, (0,0,0), (0,0,0), {} )				#Monster
	m1 = g_objFactory.getObject( "20321001" ).createEntity( spaceID, (0,0,0), (0,0,0), {} )				#Monster
	
	r = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )
	r.utype = csdefine.ENTITY_TYPE_ROLE
	r.state = 0
	r.effect_state = 0
	
	n = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )				#NPC
	n.utype = csdefine.ENTITY_TYPE_NPC
	n.state = 0
	n.effect_state = 0
	n.battleCamp = 0
	
	cm = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )			#ConvoyMonster
	cm.utype = csdefine.ENTITY_TYPE_CONVOY_MONSTER
	cm.state = 0
	cm.effect_state = 0
	cm.battleCamp = 0
	
	sl = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )			#SlaveMonster
	sl.utype = csdefine.ENTITY_TYPE_SLAVE_MONSTER
	sl.ownerID = r.id
	sl.state = 0
	sl.effect_state = 0
	sl.battleCamp = 0
	
	sd = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )			#SlaveDart
	sd.utype = csdefine.ENTITY_TYPE_VEHICLE_DART
	sd.ownerID = r.id
	sd.state = 0
	sd.effect_state = 0
	sd.battleCamp = 0
	
	np = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )			#NPCPanguNagual
	np.utype = csdefine.ENTITY_TYPE_PANGU_NAGUAL
	np.ownerID = r.id
	np.state = 0
	np.effect_state = 0
	np.battleCamp = 0
	
	yy = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )			#NPCYayu
	yy.utype = csdefine.ENTITY_TYPE_YAYU
	yy.state = 0
	yy.effect_state = 0
	yy.battleCamp = 0
	
	callm = BigWorld.createEntity( "NPCObject", spaceID, (0,0,0), (0,0,0), {} )			#CallMonster
	callm.utype = csdefine.ENTITY_TYPE_CALL_MONSTER
	callm.state = 0
	callm.effect_state = 0
	callm.battleCamp = 0

	#��δ��״̬��ɫ�ж�
	r.state = csdefine.ENTITY_STATE_PENDING
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	
	#���뿪��Ϸ״̬��ɫ�ж�
	r.state = csdefine.ENTITY_STATE_QUIZ_GAME
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	
	#������״̬��ɫ�ж�
	r.state = csdefine.ENTITY_STATE_DEAD
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	r.state = 0
	
	#�벻��ս��Ч����ɫ�ж�
	r.effect_state = csdefine.EFFECT_STATE_ALL_NO_FIGHT
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	r.effect_state = 0
	
	#������в���ս��Ч�����ɫ�ж�
	m.effect_state = csdefine.EFFECT_STATE_ALL_NO_FIGHT
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	m.effect_state = 0
	
	#��۲�ģʽ��ɫ�ж�
	r.effect_state = csdefine.EFFECT_STATE_WATCHER
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	r.effect_state = 0

	#������в��ɹ�����־���ɫ�ж�
	m.addFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	m.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )

	#���ɫ�ж�
	assert m.queryRelation( r ) == csdefine.RELATION_ANTAGONIZE
	
	#����пɱ����﹥����־�Ĺ����ж�
	m1.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( m1 ) == csdefine.RELATION_ANTAGONIZE
	m1.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#������пɱ����﹥����־������ж�
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( m1 ) == csdefine.RELATION_ANTAGONIZE
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#��ͬ��Ӫ�����ж�
	m.battleCamp = 1
	m1.battleCamp = 1
	assert m.queryRelation( m1 ) == csdefine.RELATION_FRIEND
	m.battleCamp = 0
	m1.battleCamp = 0

	#�벻ͬ��Ӫ�����ж�
	m.battleCamp = 1
	assert m.queryRelation( m1 ) == csdefine.RELATION_ANTAGONIZE
	m.battleCamp = 0

	#������пɱ����﹥����־��ͬ��Ӫ�����ж�
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	m.battleCamp = 1
	m1.battleCamp = 1
	assert m.queryRelation( m1 ) == csdefine.RELATION_FRIEND
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	m.battleCamp = 0
	m1.battleCamp = 0

	#������ж�
	assert m.queryRelation( m1 ) == csdefine.RELATION_FRIEND
	
	#����пɱ����﹥����־��NPC�ж�
	n.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( n ) == csdefine.RELATION_ANTAGONIZE
	n.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )

	#������пɱ����﹥����־��NPC�ж�
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( n ) == csdefine.RELATION_ANTAGONIZE
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#�벻ͬ��ӪNPC�ж�
	m.battleCamp = 1
	assert m.queryRelation( n ) == csdefine.RELATION_ANTAGONIZE
	m.battleCamp = 0

	#��NPC�ж�
	assert m.queryRelation( n ) == csdefine.RELATION_FRIEND
	
	
	#����пɱ����﹥����־��NPC�ж�
	cm.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( cm ) == csdefine.RELATION_ANTAGONIZE
	cm.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#������пɱ����﹥����־��NPC�ж�
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( cm ) == csdefine.RELATION_ANTAGONIZE
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#�벻ͬ��ӪNPC�ж�
	m.battleCamp = 1
	assert m.queryRelation( cm ) == csdefine.RELATION_ANTAGONIZE
	m.battleCamp = 0

	#��NPC�ж�
	assert m.queryRelation( cm ) == csdefine.RELATION_FRIEND	
	
	#�Լ��ǽٷ��뻤�ڹ����ж�
	m.setTemp( 'is_dart_banditti', True )
	assert m.queryRelation( sl ) == csdefine.RELATION_ANTAGONIZE
	m.removeTemp( 'is_dart_banditti' )

	#�Լ��ǽٷ����ڳ��ж�
	m.setTemp( 'is_dart_banditti', True )
	assert m.queryRelation( sd ) == csdefine.RELATION_ANTAGONIZE
	m.removeTemp( 'is_dart_banditti' )

	#�뻤�ڹ��������ж�
	sl.ownerID = r.id
	assert m.queryRelation( sl ) == csdefine.RELATION_ANTAGONIZE
	
	#���ڳ������ж�
	sd.ownerID = r.id
	assert m.queryRelation( sd ) == csdefine.RELATION_ANTAGONIZE
	
	#���ػ������ж�
	np.ownerID = r.id
	assert m.queryRelation( np ) == csdefine.RELATION_ANTAGONIZE
	
	#������ж�
	assert m.queryRelation( yy ) == csdefine.RELATION_ANTAGONIZE
	
	#���ٻ������ж�
	assert m.queryRelation( callm ) == csdefine.RELATION_ANTAGONIZE

	print "test finish!"