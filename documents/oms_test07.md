[TOC]

### RabbitMQ 的使用

#### 1. Ubuntu 中 RabbitMQ 的安装

```bash
sudo apt-get update -y
sudo apt-get install curl gnupg -y
curl -fsSL https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc | sudo apt-key add -
sudo apt-get install apt-transport-https
sudo tee /etc/apt/sources.list.d/bintray.rabbitmq.list <<EOF
deb https://dl.bintray.com/rabbitmq-erlang/debian bionic erlang
deb https://dl.bintray.com/rabbitmq/debian bionic main
EOF
sudo apt-get update -y
sudo apt-get install rabbitmq-server -y --fix-missing
```

