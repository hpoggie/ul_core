class Card:
    """
    A card has the following characteristics:
        Name
        cost
        rank
        abilities
        image

    It is owned by a player.
    """
    nodsl = False

    def __init_subclass__(cls, **kwargs):
        """
        Evil metaclass-ish hacking to make an internal domain-specific
        language.
        https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
        This method is called when a subclass of Card is created. It takes the
        class variables of that card and makes them into instance variables.
        Look at the faction files for examples of how to use this.
        """
        super().__init_subclass__(**kwargs)  # Maintain compatibility

        newAttrs = dict(
            (key, val) for key, val in cls.__dict__.items()
            if not key.startswith('__') and
            not hasattr(val, '__call__') and
            not isinstance(val, property))

        for key in newAttrs.keys():
            delattr(cls, key)

        oldInit = cls.__init__

        def __init__(self, **kwargs):
            kwargs.update(newAttrs)
            oldInit(self, **kwargs)

        cls.__init__ = __init__

    def __init__(self, **kwargs):
        self.name = "Placeholder Name"
        self.image = "missing.png"
        self.spell = False
        self.continuous = False  # If spell, do we stay out after spawn
        self.illusion = False  # If spell, do we die to attacks
        self.cost = 0
        self._rank = 0
        self.fast = False
        self.taunt = False
        self.isValidTarget = True
        self.owner = None
        self.game = None
        self._zone = None
        self._visible = False
        self.desc = ""
        self.stale = False  # Will this fizzle at end of turn?
        self.locked = False  # Can this be cast?

        # Alpha effects can only be done as the first action on your turn
        self.alpha = False

        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "%s at 0x%x owned by %s" % (
            self.name,
            id(self),
            self.owner)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self.zone.dirty = True

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        self.spell = (value == 's' or value == 'il')
        self.illusion = value == 'il'
        self._rank = value

    @property
    def requiresTarget(self):
        return self.onSpawn.__code__.co_argcount > 1

    @property
    def isUnit(self):
        return not self.spell

    def cast(self, target=None):
        self.controller.mana -= self.cost
        self.spawn()
        if self.requiresTarget:
            # Remove the pushed effect and re-add it with target
            effect = self.game.triggeredEffectStack.pop()
            self.controller.pushTriggeredEffect(lambda: effect.resolve(target))

    def spawn(self, newController=None):
        if newController is None:
            newController = self.controller

        self.zone = newController.faceups

        self.pushSpawnEffect()

    def pushSpawnEffect(self):
        def cleanupSpell():
            self.zone = self.owner.graveyard

        if self.spell and not self.continuous:
            self.controller.pushTriggeredEffect(cleanupSpell)

        if self.requiresTarget:
            def doActionWithTarget(target):
                if (target is not None and
                        isinstance(target, Card) and
                        target.isValidTarget):
                    self.onSpawn(target)
                    self.game.eventHandler.on_spawn(self)

            self.controller.pushTriggeredEffect(doActionWithTarget)
        else:
            def doAction():
                self.onSpawn()
                self.game.eventHandler.on_spawn(self)

            self.controller.pushTriggeredEffect(doAction)

    def attack(self, target):
        self.hasAttacked = True

        if target is self.controller.opponent.face:
            self.attackFace()
        else:
            self.game.fight(attacker=self, target=target)

    def attackFace(self):
        self.game.dealDamage(self.controller.opponent, self.rank)

    def onSpawn(self):
        pass

    def onDeath(self):
        pass

    def onDiscard(self):
        pass

    def beforeFight(self, target):
        pass

    def afterFight(self, target):
        pass

    def beforeAttack(self, target):
        pass

    def afterAttack(self, target):
        pass

    @property
    def zone(self):
        return self._zone

    @zone.setter
    def zone(self, value):
        self.moveToZone(value)

    def moveToZone(self, zone):
        if self._zone == self.controller.faceups and zone == self.owner.graveyard:
            def handleDeath():
                self.onDeath()
                self.game.eventHandler.on_die(self)

            self.controller.pushTriggeredEffect(handleDeath)
        elif self._zone == self.controller.hand and zone == self.owner.graveyard:
            self.onDiscard()

        oldController = self._zone.controller if self._zone is not None else None

        if self._zone is not None:
            self._zone.remove(self)
        self._zone = zone
        self._zone.append(self)
        self.visible = False
        self.hasAttacked = False
        self.stale = False
        self.locked = False

        if self.zone.controller is not oldController:
            self.game.eventHandler.on_change_controller(self, oldController, self.controller)

    @property
    def faceup(self):
        return self.zone is self.controller.faceups

    @property
    def facedown(self):
        return self.zone is self.controller.facedowns

    @property
    def controller(self):
        # TODO: hack
        if self.game is None:
            return self.owner

        for pl in self.game.players:
            if self.zone in pl.zones:
                return pl

        return self.owner

    @property
    def targetDesc(self):
        if hasattr(self, '_targetDesc'):
            return self._targetDesc
        else:
            return self.desc

    @targetDesc.setter
    def targetDesc(self, value):
        self._targetDesc = value

    @property
    def imagePath(self):
        return self.iconPath + '/' + self.image
