
# Message Headers
NEW_PARAMETERS = "NEW_PARAMETERS"
CONFIRMED_PARAMETERS = "CONFIRMED_PARAMETERS"
NEW_CONNECTION = "NEW_CONNECTION"
TRAIN = "TRAIN"
TERMINATE = "TERMINATE"
PARAMS = "PARAMS"
FRACTION = "FRACTION"
ROUND = "ROUND"
WAIT = "WAIT"


class Msg:
  def __init__(self, src_id=None, dest_id=None, header=None, content=None):
    self.src_id = src_id
    self.dest_id = dest_id
    self.header = header
    self.content = content

  def __str__(self):
    return 'src: {} dest: {} header: {} content: {}'.format(self.src_id, self.dest_id, self.header, self.content)