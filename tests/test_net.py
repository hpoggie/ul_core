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


def test_sanity_check(server):
    cl = FakeClient()
    cnm = network.ClientNetworkManager(cl, 'localhost', 9099)
    cnm.verbose = True
    cnm.connect(('localhost', 9099))

    stime = time.time()
    while time.time() < stime + 1 and len(cl.recvdPackets) == 0:
        cnm.recv()

    assert len(cl.recvdPackets) > 0
