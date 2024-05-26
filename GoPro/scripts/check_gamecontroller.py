import zmq

from services import Messages
from services.data.GameControlData import GameControlData


def run(mq_port: int):
    print('Listen to GameController messages on bus port', mq_port)

    packet = -1
    ctx = zmq.Context.instance()
    sub = ctx.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, Messages.GameController.key)
    sub.connect(f"tcp://localhost:{mq_port}")

    while True:
        try:
            topic, message = sub.recv_multipart()  # type: bytes, bytes
            if topic == Messages.GameControllerMessage.key:
                gc = GameControlData(message)
                if gc is not None and packet != gc.packetNumber:
                    print(gc)
                    # check if one team is 'invisible'
                    if any([t.teamNumber == 0 for t in gc.team]):
                        print("-- INVISIBLES are playing! --\n")
                    print('Team left:', gc.team[0].teamNumber, 'Team right:', gc.team[1].teamNumber)
                    packet = gc.packetNumber
        except (KeyboardInterrupt, SystemExit):
            print("Shutting down ...")
            break
        except Exception as ex:
            # Unknown exception
            print("Unknown exception: " + str(ex))
            continue
