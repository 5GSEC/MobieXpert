<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->

# MobieXpert

MobieXpert is the first L3 cellular attack detection xApp deployed at O-RAN compliant near-RT RIC. 
MobieXpert’s design is based on the Production-Based Expert System Toolset ([P-BEST](https://ieeexplore.ieee.org/document/766911)) language, 
which has been widely used for decades in stateful intrusion detection. 
With MobieXpert, network operators can program stateful production-based IDS rules for detecting a wide range of cellular L3 attacks.

MobieXpert is an essential part of 5G-Spector. To get started and learn more about 5G-Spector, please refer to our 
[paper](https://web.cse.ohio-state.edu/~wen.423/papers/5G-Spector-NDSS24.pdf) in NDSS'24
and the [5G-Spector](https://github.com/5GSEC/5G-Spector) git repository.

MobieXpert is dedicated for the [OSC RIC](https://wiki.o-ran-sc.org/display/ORAN).
It is developed based on the [OSC RIC's python SDK](https://github.com/o-ran-sc/ric-plt-xapp-frame-py).
MobieXpert obtains MobiFlow telemetry stream from the [MobiFlow Auditor xApp](https://github.com/5GSEC/MobiFlow-Auditor) via the Shared Data Layer (SDL) database.

We also have an old version at branch `master` implemented for the [ONOS RIC](https://docs.onosproject.org/v0.6.0/onos-cli/docs/cli/onos_ric/) on [SD-RAN](https://docs.sd-ran.org/master/index.html). It was used as part of the [5G-Spector](https://github.com/5GSEC/5G-Spector) artifact but not recommended any more since the ONOS RIC xApp python SDK is no longer being maintained.


## Prerequisite

### Local Docker registry

MobieXpert is built from source as a local Docker container. Refer to the official tutorial (https://docs.docker.com/engine/install/) to install and set up the Docker environment.

Create a local docker registry to host docker images: 

```
sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

### OSC nRT RIC

Before deploying the xApp, make sure the OSC nRT-RIC is deployed by following this [tutorial](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#deploy-the-osc-near-rt-ric).

### MobiFlow Auditor xApp

MobieXpert directly acquires security telemetry from the SDL generated from the [MobiFlow Auditor xApp](https://github.com/5GSEC/MobiFlow-Auditor) xApp. Following the instructions to prepare the environment and collect data from a 5G network.


## IDS Programming with MobieXpert

MobieXpert’s programming capability is powered by the Production-Based Expert System Toolset ([P-BEST](https://ieeexplore.ieee.org/document/766911)) language.
The IDS rule file is located at [src/pbest/expert/rules.pbest](./src/pbest/expert/rules.pbest). It has already integrated the L3 attack detection rules described in our original paper.

To get started with the P-BEST syntax, please refer to the P-BEST original paper: [Detecting computer and network misuse through the production-based expert system toolset (P-BEST)](https://ieeexplore.ieee.org/document/766911).

During compilation and building, the P-BEST rule file will be translated into C executables by the `pbcc` compiler. The executable listens to the input from a local `csv` file that is constantly updated with MobiFlow streams.


## Example Walkthrough

Below we provided an example of how [BTS Resource Depletion Attack](https://ieeexplore.ieee.org/document/8835363) could be detected by programming a P-BEST rule set which has been already integrated into [src/pbest/expert/rules.pbest](./src/pbest/expert/rules.pbest) from [line 433-536](./src/pbest/expert/rules.pbest#L433).
Our original [paper](https://web.cse.ohio-state.edu/~wen.423/papers/5G-Spector-NDSS24.pdf) also describes how this rule sets were developed.

![alt text](https://github.com/5GSEC/MobieXpert/blob/osc/figure.png)

The following P-BEST rule defined in `rules.pbest`  serves as an auxiliary rule for detecting BTS resource depletion attack:

```
rule[bts_depletion_add_first_transient_ue_5g:
    [+s:ue_session^TRANSIENT]
    [+ts_ev:ts_event]
    [?|s.nas_state == 1]                                        `NAS registering state
    [?|ts_ev.value - s.ts > 'BTS_DEPLETION_REG_INIT_TIME_THRESHOLD]
    [-transient_ue_counter|bs_id == s.bs_id]
    [-transient_ue|bs_id == s.bs_id, rnti == s.rnti]
==>
    [+transient_ue_counter|bs_id = s.bs_id, value = 1, ts = s.ts]
    [+transient_ue|bs_id = s.bs_id, rnti = s.rnti, ts = s.ts]
    [$|s:TRANSIENT]
    [!|debugprintf("[BTS Resource Depletion][ADD_FIRST_TRANSIENT_UE_5G] Marking UE %d/%x as transient\n", s.rnti, s.rnti)]
    [!|debugprintf("[BTS Resource Depletion][ADD_FIRST_TRANSIENT_UE_5G] Transient UE counter of bs %d is %d\n", s.bs_id, 1)]
]
```

This rule based on certain user-defined `xtype` structures in the P-BEST file. It determines whether a UE is a `transient UE` that explicits a layer-3 RRC DoS pattern.
From the rule, it leverages the MobiFlow features, i.e., the UE timers, and checks whether the session has been stuck at NAS registering state exceeding a time threshold `BTS_DEPLETION_REG_INIT_TIME_THRESHOLD`.
Then this rule will be triggered to add a transient UE instance and update the counters. The accumulated counters will then be evaluated to determine whether to trigger a BTS resource depletion attack alert, based on the rule below:

```
rule[bts_depletion_generate_event:
    [+tran_ue_cntr: transient_ue_counter^BTS_RESOURCE_DEPLETION]
    [?|tran_ue_cntr.value > 'BTS_DEPLETION_UE_THRESHOLD]
==>
    [$|tran_ue_cntr: BTS_RESOURCE_DEPLETION]
    [+event|id = 'event_id_cntr,
	        name = "BTS Resource Depletion",
            ts = tran_ue_cntr.ts,
            bs_id = tran_ue_cntr.bs_id,
            ue = 0
    ]
    [!|'event_id_cntr += 1 ]
    [!|debugprintf("[BTS Resource Depletion][GENERATE_EVENT] Event detected for bs %d\n", tran_ue_cntr.bs_id)]
    [!|eventprintfjson('event_id_cntr, "BTS Resource Depletion", tran_ue_cntr.bs_id, tran_ue_cntr.ts, tran_ue_cntr.value)]
]
```

Additionally, all the defined `ptype` in P-BEST need to be cleaned up in time. The rule below uses a timer-based clean up strategy to release the transient UEs to avoid filing an false alarm:

```
rule[bts_depletion_release_transient_ue:
    [+tran_ue:transient_ue]
    [+tran_ue_cntr:transient_ue_counter|bs_id == tran_ue.bs_id]
    [+ts_ev:ts_event]
    [?|(ts_ev.value - tran_ue.ts) > 'BTS_DEPLETION_RELEASE_TIME_THRESHOLD]
==>
    [/tran_ue_cntr|value -= 1]
    [-|tran_ue]
    [!|debugprintf("[BTS Resource Depletion][RELEASE_TRANSIENT_UE] Removing transient UE %d/%x\n", tran_ue.rnti, tran_ue.rnti)]
]
```

## Build the MobieXpert xApp

After the new rules are integrated into [src/pbest/expert/rules.pbest](./src/pbest/expert/rules.pbest), you can use our Docker build script to build the MobiExpert xApp: 

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container.

```
$ docker images
localhost:5000/mobiexpert-xapp               0.0.1        39cc298cbb97   11 minutes ago   232MB
```

If your `rules.pbest` file contains syntax error, an exception will occur and fail the build process.

## Install the MobieXpert xApp

First, onboard the xApp. You need to set up the proper environment with the `dms_cli` tool. Following the instructions here: https://github.com/5GSEC/OAI-5G-Docker/blob/master/O-RAN%20SC%20RIC%20Deployment%20Guide.md#mobiexpert-xapp. Execute the following to onboard the xApp:

```
cd init
sudo -E dms_cli onboard --config_file_path=config-file.json --shcema_file_path=schema.json
```

Then, simply run the script to deploy the xApp under the `ricxapp` K8S namespace in the nRT-RIC.

```
cd ..
./deploy.sh
```

Successful deployment:

```
$ kubectl get pods -n ricxapp
ricxapp       ricxapp-mobiexpert-xapp-796846cc9b-sjwhn                     1/1     Running     0          26m
```

## Uninstall MobieXpert xApp

Undeploy the MobieXpert xApp from Kubernetes:

```
./undeploy.sh
```


## Publication

```
@inproceedings{5G-Spector:NDSS24,
  title     = {5G-Spector: An O-RAN Compliant Layer-3 Cellular Attack Detection Service},
  author    = {Wen, Haohuang and Porras, Phillip and Yegneswaran, Vinod and Gehani, Ashish and Lin, Zhiqiang},
  booktitle = {Proceedings of the 31st Annual Network and Distributed System Security Symposium (NDSS'24)},
  address   = {San Diego, CA},
  month     = {February},
  year      = 2024
}
```
