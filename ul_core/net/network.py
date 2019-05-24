import types

from .network_manager import NetworkManager
from ul_core.core.enums import numericEnum
from ul_core.net.serialization import (serialize, deserialize,
                                       DeserializationError)
from ul_core.net import rep


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

        self.tryCall(key, [addr] + rep.decode_args_from_client(key,
                                                               operands,
                                                               self.player_for_addr(addr)))

    def onClientConnected(self, conn):
        # Make it so each client opcode is a function
        for i, key in enumerate(ClientNetworkManager.Opcodes.keys):
            class OpcodeFunc:
                def __init__(self, manager, key, opcode):
                    self.key = key
                    self.manager = manager
                    self.opcode = opcode

                def __call__(self, base, *args):
                    self.manager.send(
                        base.addr,
                        serialize([self.opcode] + list(
                            rep.encode_args_to_client(self.key, args,
                                                      self.manager.player_for_addr(base.addr)))))

            # Bind the OpcodeFunc as a method to the class
            setattr(conn, key, types.MethodType(OpcodeFunc(self, key, i), conn))

        self.base.onClientConnected(conn)


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
        'requestDecision',
        'endRedraw',
        'winGame',
        'loseGame',
        'setActive',
        'kick')

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
