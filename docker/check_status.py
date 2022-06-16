import requests
import os

zks = os.getenv('ZOO_SERVERS')
zk_stats = {}

for zk in zks.split(' '):
    zk_host = zk.split('=')[1].split(':')[0]
    zk_stats[zk_host] = requests.get('http://{}:{}/commands/monitor'.format(zk_host, 8080), timeout=0.01).json()

leader = []
followers = []
synced_followers = 0

for zk in zk_stats:
    stats = zk_stats[zk]
    if 'server_state' in stats:
        if stats['server_state'] == 'leader':
            leader.append(zk)
            synced_followers = stats['synced_followers']
        else:
            followers.append(zk)

if synced_followers < 2 or len(leader) > 1 or len(leader) < 1 or len(followers) < 2 or len(followers) > 2:
    print("alert!")
    print("stats: {}".format(zk_stats))
    print("synced_followers: {}".format(synced_followers))
else:
    print("all OK \n")
    print("leader: {}".format(leader))
    print("followers: {}".format(followers))
    print("synced_followers: {}".format(synced_followers))
