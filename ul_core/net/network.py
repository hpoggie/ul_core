import types

from .network_manager import NetworkManager
from ul_core.core.enums import numericEnum
from ul_core.net.serialization import (serialize, deserialize,
                                       DeserializationError)
from ul_core.net import rep
from ul_core.core.event_handler import EventHandler


class OpcodeError(Exception):
    pass


class ULNetworkManager(NetworkManager):
    def tryCall(self, key, args):
        if not hasattr(self.base, key):
            raise OpcodeError("Opcode not found: " + key)

        getattr(self.base, key)(*args)

    def tryFindKey(self, opcode):
        try:
            return self.Opcodes.keys[opcode]
        except IndexError:
            raise OpcodeError("Invalid index: " + str(opcode))


def log_send(key, player, args, encoded):
    print("Send %s to player %s:" % (key, player))
    print("    ARGS: " + repr(args))
    print("    ENCODED: " + repr(encoded))


class ServerNetworkManager (ULNetworkManager):
    def __init__(self, base):
        super().__init__()
        self.startServer()
        self.base = base

    Opcodes = numericEnum(
        'requestNumPlayers',
        'addPlayer',
        'decideWhetherToGoFirst',
        'selectFaction',
        'mulligan',
        'revealFacedown',
        'playFaceup',
        'attack',
        'play',
        'makeDecision',
        'useFactionAbility',
        'endTurn')

    def player_for_addr(self, addr):
        """
        Return the server's players
        TODO: use a cleaner way
        """
        return self.base.players[addr] if hasattr(self.base, 'players') else None

    def onGotPacket(self, packet, addr):
        if packet == '':
            return

        try:
            operands = deserialize(packet)
        except DeserializationError:
            print("Got malformed packet: " + repr(packet))
            return

        (opcode, operands) = (operands[0], operands[1:])

        key = self.tryFindKey(opcode)

        if self.verbose:
            print("got opcode: ", key)

        decoded_args = rep.decode_args_from_client(key, operands, self.player_for_addr(addr))

        self.tryCall(key, [addr] + list(decoded_args))

    def onClientConnected(self, conn):
        # Make it so each client opcode is a function
        for i, key in enumerate(ClientNetworkManager.Opcodes.keys):
            class OpcodeFunc:
                def __init__(self, key, opcode):
                    self.key = key
                    self.opcode = opcode

                def __call__(self, base, *args):
                    player = base.manager.player_for_addr(base.addr)

                    encoded = list(
                        rep.encode_args_to_client(self.key, args, player))

                    if base.manager.verbose:
                        log_send(self.key, player, args, encoded)

                    base.manager.send(
                        base.addr,
                        serialize([self.opcode] + encoded))

            # Bind the OpcodeFunc as a method to the class
            setattr(conn, key, types.MethodType(OpcodeFunc(key, i), conn))

        conn.manager = self
        self.base.onClientConnected(conn)

    def handoff_to(self, new_base):
        """
        Handoff the connections to new_base
        """
        self.base = new_base
        for conn in self.connections:
            conn.manager = self


class ClientNetworkManager (ULNetworkManager):
    """
    The ClientNetworkManager takes incoming network opcodes and turns them into
    calls to the client.
    """
    def __init__(self, base, ip, port, state):
        super().__init__()
        self.base = base
        self.ip = ip
        self.port = port
        self.state = state

        # Make it so each server opcode is a function
        for i, key in enumerate(ServerNetworkManager.Opcodes.keys):
            class OpcodeFunc:
                def __init__(self, key, opcode):
                    self.opcode = opcode
                    self.key = key

                def __call__(self, base, *args):
                    base.send(
                        (base.ip, base.port),
                        serialize([self.opcode] + list(
                            rep.encode_args_to_server(self.key, args, base.player))))

            # Bind the OpcodeFunc as a method to the class
            setattr(self, key, types.MethodType(OpcodeFunc(key, i), self))

    @property
    def player(self):
        return self.state.player if hasattr(self.state, 'player') else None

    Opcodes = numericEnum(
        'onEnteredGame',
        'requestGoingFirstDecision',
        'updateNumPlayers',
        'updateEnemyFaction',
        'enemyGoingFirst',
        'enemyGoingSecond',
        'updateBothPlayersMulliganed',
        'updatePlayerHand',
        'updateEnemyHand',
        'updatePlayerFacedowns',
        'updateEnemyFacedowns',
        'updatePlayerFaceups',
        'updateHasAttacked',
        'updateEnemyFaceups',
        'updatePlayerGraveyard',
        'updateEnemyGraveyard',
        'updatePlayerManaCap',
        'updatePlayerMana',
        'updateEnemyManaCap',
        'updatePlayerCounter',
        'updateEnemyCounter',
        'updatePlayerFacedownStaleness',
        'updateEnemyFacedownStaleness',
        'playAnimation',
        'requestDecision',
        'endRedraw',
        'winGame',
        'loseGame',
        'setActive',
        'kick')

    Animations = numericEnum(
        'on_spawn',
        'on_fight',
        'on_die',
        'on_change_controller',
        'on_reveal_facedown',
        'on_play_faceup',
        'on_play_facedown',
        'on_draw',
        'on_end_turn')

    def onGotPacket(self, packet, addr):
        if packet == '':
            return

        try:
            operands = deserialize(packet)
        except DeserializationError:
            print("Got malformed packet: " + repr(packet))
            return

        (opcode, operands) = (operands[0], operands[1:])

        key = self.tryFindKey(opcode)

        if self.verbose:
            print("got opcode ", key + " with args " + str(operands))

        self.tryCall(key, rep.decode_args_from_server(key, operands, self.player))


class AnimationHandler(EventHandler):
    """
    Calls animations for client

    Should look something like

    >>> AnimationHandler().__dict__.keys()
    dict_keys(['on_spawn', 'on_fight', 'on_die', 'on_change_controller', 'on_reveal_facedown', 'on_play_faceu
    p', 'on_play_facedown', 'on_draw', 'on_end_turn'])
    """
    pass

for i, eventName in enumerate(ClientNetworkManager.Animations.keys):
    # Python binding rules WHY
    def make_callAndReturn(i):
        def callAndReturn(self, *args, **kwargs):
            getattr(super(), eventName)(*args, **kwargs)
            return i

        return callAndReturn

    setattr(AnimationHandler, eventName, make_callAndReturn(i))
