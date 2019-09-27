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


def log_send_to_client(key, player, args, encoded):
    print("""
Send %s to player %s:
    ARGS: %s
    ENCODED: %s""" % (key, player, args, encoded))


def log_send_to_server(key, args, encoded):
    print("""
Send %s to server:
    ARGS: %s
    ENCODED: %s""" % (key, args, encoded))


def log_recv_from_client(key, args, decoded):
    print("""
Recv %s from client:
    ARGS: %s
    DECODED: %s""" % (key, args, decoded))


def log_recv_from_server(key, args, decoded):
    print("""
Recv %s from server:
    ARGS: %s
    DECODED: %s""" % (key, args, decoded))


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

        decoded_args = rep.decode_args_from_client(key, operands, self.player_for_addr(addr))

        if self.verbose:
            log_recv_from_client(key, operands, decoded_args)

        self.tryCall(key, [addr] + list(decoded_args))

    def onClientConnected(self, conn):
        # Make it so each client opcode is a function
        for i, key in enumerate(ClientNetworkManager.Opcodes.keys):
            class OpcodeFunc:
                def __init__(self, key, opcode):
                    self.key = key
                    self.opcode = opcode

                def __call__(self, base, *args, player=None):
                    if player is None:
                        player = base.manager.player_for_addr(base.addr)

                    encoded = list(
                        rep.encode_args_to_client(self.key, args, player))

                    if base.manager.verbose:
                        log_send_to_client(self.key, player, args, encoded)

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
                    encoded = list(rep.encode_args_to_server(self.key, args, base.player))

                    if base.verbose:
                        log_send_to_server(self.key, args, encoded)

                    base.send((base.ip, base.port), serialize([self.opcode] + encoded))

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
        'updateZone',
        'updateBothPlayersMulliganed',
        'updateHasAttacked',
        'updatePlayerManaCap',
        'updatePlayerMana',
        'updateEnemyManaCap',
        'updatePlayerFacedownStaleness',
        'updateEnemyFacedownStaleness',
        'playAnimation',
        'moveCard',
        'updateCounter',
        'updateCardVisibility',
        'requestDecision',
        'endRedraw',
        'illegalMove',
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

        decoded = rep.decode_args_from_server(key, operands, self.player)

        if self.verbose:
            log_recv_from_server(key, operands, decoded)

        self.tryCall(key, decoded)
