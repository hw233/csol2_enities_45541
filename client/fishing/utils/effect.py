# -*- coding:gb18030 -*-
#

import Define
from Function import Functor
from EffectMgr import EffectMgr
from ..FishingDataMgr import FishingDataMgr


def fadeOutModel(pyModel, lastTime = 1.0):
	"""
	����ģ��
	@type		pyModel		: PyModel
	@param		pyModel		: �����ģ��
	@type		lastTime	: Float
	@param		lastTime	: �����ĳ���ʱ��
	@return
	"""
	EffectMgr.instance().fadeOutModel(pyModel, lastTime)


def fadeInModel(pyModel, lastTime = 1.0):
	"""
	����ģ��
	@type		pyModel		: PyModel
	@param		pyModel		: �����ģ��
	@type		lastTime	: Float
	@param		lastTime	: �����ĳ���ʱ��
	@return
	"""
	EffectMgr.instance().fadeInModel(pyModel, lastTime)


def applyEffect(model, effectID, ptype = Define.TYPE_PARTICLE_NPC):
	"""Ӧ�ù�Ч��ģ����"""
	particles = FishingDataMgr.instance().getEffectByID(effectID)

	if particles is None:
		print "Can't find effect by id %s" % str(effectID)
	else:
		def onParticleLoaded(path, hp, p):
			#print "Particle loaded callback: %s, %s, %i" % (path, hp, p.nSystems())
			pass

		for (source, scale, duration, hps) in particles:
			for hp in hps:
				callback = Functor(onParticleLoaded, source, hp)
				EffectMgr.instance().createParticleBG(model, hp, source, callback, duration, ptype, scale)


def removeEffect(model, effectID):
	"""�ѹ�Ч��ģ�����Ƴ�"""
	particles = FishingDataMgr.instance().getEffectByID(effectID)

	for hp in particles[3]:
		node = EffectMgr.instance().accessNode(model, hp)
		for attachment in node.attachments:
			node.detach(attachment)
