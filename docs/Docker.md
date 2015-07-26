# Docker

Docker is an open platform for building, shipping and running applications. Docker allows VPSolver to run on a large variety of platforms with very little effort.

## Docker Setup
Install Docker [[Docker installation instructions](https://docs.docker.com/installation/)].

Option 1: simply `pull` VPSolver from Docker repository (without building):

```bash
user@locahost ~$ docker pull fdabrandao/vpsolver
```

Option 2: `clone` VPSolver and `build` locally:

```bash 
user@locahost ~$ git clone git@github.com:fdabrandao/vpsolver.git vpsolver
user@locahost ~$ docker build -t fdabrandao/vpsolver vpsolver
```

## Usage
Directly using the command line interface:

```bash
user@locahost ~$ docker run -it fdabrandao/vpsolver bash
root@55d14f6b6f32:~# python examples/example.py
...
```

or through the VPSolver Web APP (example URL: `http://172.17.0.60:5555/`):

```bash
user@locahost ~$ docker run -it -p 5555 fdabrandao/vpsolver 
eth0      Link encap:Ethernet  HWaddr 02:42:ac:11:00:3c  
          inet addr:*172.17.0.60*  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:acff:fe11:3c/64 Scope:Link
          UP BROADCAST  MTU:1500  Metric:1
          RX packets:2 errors:0 dropped:0 overruns:0 frame:0
          TX packets:2 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:168 (168.0 B)  TX bytes:180 (180.0 B)

 * Running on http://0.0.0.0:5555/
...
```

## Advanced
Run vpsolver in background:

```bash
user@locahost ~$ CID=$(docker run -d -p 5555 fdabrandao/vpsolver)
user@locahost ~$ docker inspect --format URL:http://{{.NetworkSettings.IPAddress}}:5555/ $CID
URL:http://172.17.0.71:5555/
```

List all running vpsolver containers:

```bash
user@locahost ~$ docker ps | grep fdabrandao/vpsolver
...
```

List URLs of all running vpsolver containers:

```bash
user@locahost ~$ CIDs=$(docker ps | grep fdabrandao/vpsolver | cut -d" " -f1)
user@locahost ~$ docker inspect --format URL:http://{{.NetworkSettings.IPAddress}}:5555/ $CIDs
...
```

Stop and remove all vpsolver containers:

```bash
user@locahost ~$ docker stop $(docker ps -a | grep fdabrandao/vpsolver | cut -d" " -f1)
user@locahost ~$ docker rm $(docker ps -a | grep fdabrandao/vpsolver | cut -d" " -f1)
```

***
Copyright © Filipe Brandão. All rights reserved.  
E-mail: <fdabrandao@dcc.fc.up.pt>. [[Homepage](http://www.dcc.fc.up.pt/~fdabrandao/)]