# Relaypot
Transport-layer honeycloud framework for IoT malware research by LOCI team, University of Jinan.

This project provides a simple reverse proxy-like framework to implement high- or low-interaction honeycloud systems for various TCP-based application layer protocols.
The *frontend* module works as a remote server to simply forward requests from adversaries to the *backend* server.
*Agents* in the *backend* server will parse the requests and generate a response based on defined rules, or forward requests to backing services.

This framework was inspired by [Cowrie](https://github.com/cowrie/cowrie) and powered by [Twisted](https://github.com/twisted/twisted).

## Features
- TCP conversation management and payload logging;
- Event-driven framework for handling TCP requests;
- Modular design for high- or low-interaction decoys (*agents*) and log writers;
    - High-interaction agent working with backing devices as a transport layer proxy.
    - Low-interaction decoys based on response databases.
    - Event-based log writer model build for ElasticSearch.
- Launch as twistd module or integrate with `systemd`.

## Requirements

- Linux + Python 3.
- ElasticSearch for default `elastic` log writer.
- Backing devices for high-interaction agents with corresponding services enabled.

## Usage Sample

### For both
1. Deploy code on remote frontend servers and on the local backend server
2. Edit `config.yaml`, set backend host, agent module, and log writer.
3. Install prerequisites in `requirements.txt`.

### Integrating and Launching with systemd
4. Edit & install `scripts/rpot-b.service` on backend server and `scripts/rpot-f<PORT>.service` on frontend servers.
5. run `systemctl start rpot-b.service` on backend server and `systemctl start rpot-f<PORT>.service` on frontend servers.

### ~~Launching in shell is deprecated~~

## Files of Interest in `src/relaypot`

- `frontend/`: Code for *frontend* servers, deployed on remote servers.
- `backend/`: Code for the *backend* server, dispatches conversation to agents and log writers.
- `agent/`: Agent modules for parsing requests and generating responses.
    - `base.py`: Definition of agent interfaces.
- `output/`: Log writer modules.
    - `__init__.py`: Definition of how writers fill basic fields and generate semi-structured logs.
- `utils/`: Utility codes:
    - `config.py`: Config parser & loader.
    - `mods.py`: Module loader.


## Implemented Modules

### Backend `agents`

Most of them are just demos and not actually used

- `bridge`: High-interaction agent for telnet protocol, working with backing devices as a transport layer proxy.
- `dummy`: Only listen to requests and make no response.
- `match2`: Select a response from a database based on a request's hashsum.
- `telnet`: A simple telnet shell. 

### Log Writers

- `elastic`: Log requests and responses into an ElasticSearch server.
- `file`: Log a conversation into a file.

## Acknowledgement

This projected was supported by Prof Zhenxiang Chen and [LOCI team](http://loci.ujn.edu.cn) at [University of Jinan](https://www.ujn.edu.cn).

This work and related literature works were supported by the National Natural Science Foundation of China under Grants No.61672262, No.61472164 and No.61702218, Project of Independent Cultivated Innovation Team of Jinan City under Grant No.2018GXRC002, the Shandong Provincial Key R&D Program under Grant No.2018CXG0706 and No.2019GGX101028, Project of Shandong Province Higher Educational Youth Innovation Science and Technology Program NO.2019KJN028.

Thanks Huawei Technologies for funding research projects on Android and IoT network security.

## About LOCI@University of Jinan
The Cyber Intelligence Lab (loci Lab) in the School of Information Science and Engineering at the University of Jinan is directed by Prof. Zhenxiang Chen. The lab conducts research mainly on Internet traffic measurement and behavior analysis, mobile network security and privacy issues, and mobile malware detection. Recently, we are focusing on building an automatic and intelligent traffic collection and analysis system and using the network traffic to detect malware behavior.

We are looking for extensive international collaborators and welcome scholars from the world to visit our Lab.

Site: http://loci.ujn.edu.cn

## Related Works and Literatures
Literature works used datasets collected by this code:
- *Hasan et al.*
    IoT Botnet Detection framework from Network Behavior based on Extreme Learning Machine
    (INFOCOM WKSHPS 2022)
    ([IEEE link](https://ieeexplore.ieee.org/abstract/document/9798307))
- *Zhu et al.*
    Mining Function Homology of Bot Loaders from Honeypot Logs
    (In progress)
    ([arXiv Link](https://arxiv.org/abs/2206.00385))
