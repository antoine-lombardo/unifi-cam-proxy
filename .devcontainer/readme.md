Tested On
Ubuntu 24.04 with Docker (with Dev Container support)

docker network create -d macvlan \
  --subnet=192.168.0.0/24 \
  --gateway=192.168.0.1 \
  -o parent=lan0 \
  lan_net

Replace lan0 with your actual network interface name (e.g., eth0, enp3s0, etc.).
Replace the MAC address (`**:__:__:__:__:__`) in `.devcontainer/devcontainer.json` with your desired value.