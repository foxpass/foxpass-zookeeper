import os

zks = os.getenv('ZOO_SERVERS')
zk_stats = {}

for zk in zks.split(' '):
   zk_host = zk.split('=')[1].split(':')[0]
   zk_port = zk.split('=')[1].split(':')[2].split(';')[1]
   zk_stats[zk_host] = os.popen("echo mntr | nc {} {}".format(zk_host, zk_port)).read()

leader = []
followers = []
for zk in zk_stats:
   stats = zk_stats[zk]
   for stat in stats.split("\n"):
      if "zk_server_state" in stat:
          if "leader" in stat:
              leader.append(zk)
          if "follower" in stat:
              followers.append(zk)

if len(leader) > 1 or len(leader) < 1 or len(followers) < 2 or len(followers) > 2:
    print("alert!")
    print("stats: {}".format(zk_stats))
else:
    print("all OK \n")
    print("leader: {}".format(leader))
    print("followers: {}".format(followers))
