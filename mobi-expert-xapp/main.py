#!/usr/bin/env python3
# Copyright 2004-present Facebook. All Rights Reserved.
# SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>
#
# SPDX-License-Identifier: Apache-2.0

# import onos_ric_sdk_py as sdk
import argparse
import json
import logging
from pypbest.pbest import PBest
from pypbest.mobiflow_reader import MobiFlowReader

mf_reader = None
pb = None

def main(args: argparse.Namespace) -> None:
    rpc_ip = args.rpc_addr
    rpc_port = args.rpc_port
    with open(args.mobiflow_config) as f:
        mobiflow_config = json.load(f)
        # load configs
        db_path = mobiflow_config["mobiflow"]["sqlite3_db_path"]
        rpc_query_interval = mobiflow_config["mobiflow"]["rpc_query_interval"]
        csv_file = mobiflow_config["pbest"]["pbest_csv_file"]
        pbest_exec_name = mobiflow_config["pbest"]["pbest_exec_name"]
        pbest_log_path = mobiflow_config["pbest"]["pbest_log_path"]
        maintenance_time_threshold = int(mobiflow_config["pbest"]["maintenance_time_threshold"])
        # Init mobiflow writer configs
        global mf_reader
        mf_reader = MobiFlowReader(rpc_ip, rpc_port, rpc_query_interval, csv_file, maintenance_time_threshold)
        # Init pbest configs
        global pb
        pb = PBest(pbest_exec_name, pbest_log_path, csv_file)
        pb.run()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="MobiExpert xApp.")
    parser.add_argument("--mobiflow-config", type=str, help="MobiFlow config")
    parser.add_argument("--rpc-addr", type=str, help="RPC server IP address for reaching MobiFlow Service")
    parser.add_argument("--rpc-port", type=int, help="RPC server port for reaching MobiFlow Service")
    args = parser.parse_args()
    main(args)


