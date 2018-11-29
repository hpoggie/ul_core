import pytest
import net.network as network
import net.network_manager as network_manager
import os
import time
import sys
import signal


class FakeServer:
    def onClientConnected(self, client):
        client.updateNumPlayers(-1)


class FakeClient:
    def __init__(self):
        self.recvdPackets = []

    def updateNumPlayers(self, d):
        self.recvdPackets.append(d)

    def recv(self):
        self.networkManager.recv()


@pytest.fixture(scope='function')
def server():
    pid = os.fork()
    if pid == 0:
        snm = network.ServerNetworkManager(FakeServer())
        while len(snm.connections) < 1:
            snm.accept()  # accept does not block
        while True:
            try:
                snm.recv()
            except network_manager.ConnectionClosed:
                pass

    yield pid
    os.kill(pid, signal.SIGKILL)


@pytest.fixture(scope='function')
def client():
    cl = FakeClient()
    cnm = network.ClientNetworkManager(cl, 'localhost', 9099)
    cl.networkManager = cnm
    cnm.verbose = True
    cnm.connect(('localhost', 9099))
    return cl


def test_sanity_check(server, client):
    stime = time.time()
    while time.time() < stime + 1 and len(client.recvdPackets) == 0:
        client.recv()

    assert len(client.recvdPackets) > 0


def test_bad_packets():
    nms = (network.ServerNetworkManager(None),
            network.ClientNetworkManager(None, 'localhost', 9099))

    for nm in nms:
        nm.onGotPacket('00000', ('localhost', 9099))
        nm.onGotPacket('i@3#b1', ('localhost', 9099))
        nm.onGotPacket('i' + '8' * 50000, ('localhost', 9099))
        nm.onGotPacket('i8' * 50000, ('localhost', 9099))
