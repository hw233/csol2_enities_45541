# -*- coding:gb18030 -*-
#

import Define
from Function import Functor
from EffectMgr import EffectMgr
from ..FishingDataMgr import FishingDataMgr


def fadeOutModel(pyModel, lastTime = 1.0):
	"""
	渐隐模型
	@type		pyModel		: PyModel
	@param		pyModel		: 渐变的模型
	@type		lastTime	: Float
	@param		lastTime	: 渐隐的持续时间
	@return
	"""
	EffectMgr.instance().fadeOutModel(pyModel, lastTime)


def fadeInModel(pyModel, lastTime = 1.0):
	"""
	渐显模型
	@type		pyModel		: PyModel
	@param		pyModel		: 渐变的模型
	@type		lastTime	: Float
	@param		lastTime	: 渐隐的持续时间
	@return
	"""
	EffectMgr.instance().fadeInModel(pyModel, lastTime)


def applyEffect(model, effectID, ptype = Define.TYPE_PARTICLE_NPC):
	"""应用光效到模型上"""
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
	"""把光效从模型上移除"""
	particles = FishingDataMgr.instance().getEffectByID(effectID)

	for hp in particles[3]:
		node = EffectMgr.instance().accessNode(model, hp)
		for attachment in node.attachments:
			node.detach(attachment)
