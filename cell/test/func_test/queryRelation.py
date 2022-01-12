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

	#与未决状态角色判定
	r.state = csdefine.ENTITY_STATE_PENDING
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	
	#与离开游戏状态角色判定
	r.state = csdefine.ENTITY_STATE_QUIZ_GAME
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	
	#与死亡状态角色判定
	r.state = csdefine.ENTITY_STATE_DEAD
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	r.state = 0
	
	#与不可战斗效果角色判定
	r.effect_state = csdefine.EFFECT_STATE_ALL_NO_FIGHT
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	r.effect_state = 0
	
	#自身具有不可战斗效果与角色判定
	m.effect_state = csdefine.EFFECT_STATE_ALL_NO_FIGHT
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	m.effect_state = 0
	
	#与观察模式角色判定
	r.effect_state = csdefine.EFFECT_STATE_WATCHER
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	r.effect_state = 0

	#自身具有不可攻击标志与角色判定
	m.addFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )
	assert m.queryRelation( r ) == csdefine.RELATION_NOFIGHT
	m.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )

	#与角色判定
	assert m.queryRelation( r ) == csdefine.RELATION_ANTAGONIZE
	
	#与具有可被怪物攻击标志的怪物判定
	m1.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( m1 ) == csdefine.RELATION_ANTAGONIZE
	m1.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#自身具有可被怪物攻击标志与怪物判定
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( m1 ) == csdefine.RELATION_ANTAGONIZE
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#与同阵营怪物判定
	m.battleCamp = 1
	m1.battleCamp = 1
	assert m.queryRelation( m1 ) == csdefine.RELATION_FRIEND
	m.battleCamp = 0
	m1.battleCamp = 0

	#与不同阵营怪物判定
	m.battleCamp = 1
	assert m.queryRelation( m1 ) == csdefine.RELATION_ANTAGONIZE
	m.battleCamp = 0

	#自身具有可被怪物攻击标志与同阵营怪物判定
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	m.battleCamp = 1
	m1.battleCamp = 1
	assert m.queryRelation( m1 ) == csdefine.RELATION_FRIEND
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	m.battleCamp = 0
	m1.battleCamp = 0

	#与怪物判定
	assert m.queryRelation( m1 ) == csdefine.RELATION_FRIEND
	
	#与具有可被怪物攻击标志的NPC判定
	n.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( n ) == csdefine.RELATION_ANTAGONIZE
	n.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )

	#自身具有可被怪物攻击标志与NPC判定
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( n ) == csdefine.RELATION_ANTAGONIZE
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#与不同阵营NPC判定
	m.battleCamp = 1
	assert m.queryRelation( n ) == csdefine.RELATION_ANTAGONIZE
	m.battleCamp = 0

	#与NPC判定
	assert m.queryRelation( n ) == csdefine.RELATION_FRIEND
	
	
	#与具有可被怪物攻击标志的NPC判定
	cm.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( cm ) == csdefine.RELATION_ANTAGONIZE
	cm.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#自身具有可被怪物攻击标志与NPC判定
	m.addFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	assert m.queryRelation( cm ) == csdefine.RELATION_ANTAGONIZE
	m.removeFlag( csdefine.ENTITY_FLAG_CAN_BE_HIT_BY_MONSTER )
	
	#与不同阵营NPC判定
	m.battleCamp = 1
	assert m.queryRelation( cm ) == csdefine.RELATION_ANTAGONIZE
	m.battleCamp = 0

	#与NPC判定
	assert m.queryRelation( cm ) == csdefine.RELATION_FRIEND	
	
	#自己是劫匪与护镖怪物判定
	m.setTemp( 'is_dart_banditti', True )
	assert m.queryRelation( sl ) == csdefine.RELATION_ANTAGONIZE
	m.removeTemp( 'is_dart_banditti' )

	#自己是劫匪与镖车判定
	m.setTemp( 'is_dart_banditti', True )
	assert m.queryRelation( sd ) == csdefine.RELATION_ANTAGONIZE
	m.removeTemp( 'is_dart_banditti' )

	#与护镖怪物主人判定
	sl.ownerID = r.id
	assert m.queryRelation( sl ) == csdefine.RELATION_ANTAGONIZE
	
	#与镖车主人判定
	sd.ownerID = r.id
	assert m.queryRelation( sd ) == csdefine.RELATION_ANTAGONIZE
	
	#与守护主人判定
	np.ownerID = r.id
	assert m.queryRelation( np ) == csdefine.RELATION_ANTAGONIZE
	
	#与犽于判定
	assert m.queryRelation( yy ) == csdefine.RELATION_ANTAGONIZE
	
	#与召唤怪物判定
	assert m.queryRelation( callm ) == csdefine.RELATION_ANTAGONIZE

	print "test finish!"