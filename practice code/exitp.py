import os
import random
from stem import CircStatus
from stem.control import Controller
from stem.descriptor import parse_file

relays = []

with Controller.from_port(port = 9051) as controller:
  controller.authenticate()
  data_dir = controller.get_conf('DataDirectory')
  for rel in parse_file(os.path.join(data_dir, 'cached-microdesc-consensus')):
    relays.append(rel)

  check = random.choice(relays)
  print check.flags
  print 'Exit' in check.flags