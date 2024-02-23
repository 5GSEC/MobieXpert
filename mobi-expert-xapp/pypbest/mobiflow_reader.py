import logging
import threading
import datetime
import time
from .mobiflow.lockutil import *
from .mobiflow.mobiflow import get_time_ms, MOBIFLOW_DELIMITER
from .rpc.client import MobiFlowRpcClient

class MobiFlowReader:
    def __init__(self, rpc_ip_addr, rpc_port, query_interval, csv_file, maintenance_time_threshold=0):
        # input writer
        self.csv_file = csv_file
        self.clear_file()
        self.last_write_time = 0
        self.ue_mobiflow_table_name = "ue_mobiflow"
        self.bs_mobiflow_table_name = "bs_mobiflow"
        # init RPC client
        logging.info(f"[App] MobiFlow RPC server config {rpc_ip_addr}:{rpc_port} interval {query_interval}")
        self.rpc_client = MobiFlowRpcClient(rpc_ip_addr, rpc_port)
        self.rpc_query_interval = query_interval  # in ms
        # start a new thread to read database from MobiFlow Auditor xApp
        logging.info("[App] Starting MobiFlow reading thread")
        self.db_thread = threading.Thread(target=self.read_mobiflow_rpc)
        self.db_thread.start()
        # start a new thread to track maintenance event
        logging.info("[App] Starting Maintenance thread")
        self.maintenance_time_threshold = maintenance_time_threshold  # in ms
        self.maintenance_thread = threading.Thread(target=self.pbest_write_maintenance)
        self.maintenance_thread.start()

    def read_mobiflow_rpc(self):
        if self.rpc_client is None:
            logging.error(f"[App] RPC Client is NULL!")
            return
        if not self.rpc_client.check_server():
            return
        f = open(self.csv_file, "a")
        # polling loop
        while True:
            # query MobiFlow from RPC server
            bs_results = self.rpc_client.query_mobiflow_streaming(self.bs_mobiflow_table_name)
            ue_results = self.rpc_client.query_mobiflow_streaming(self.ue_mobiflow_table_name)

            # write MobiFlow based on timestamp order
            u_idx = 0
            b_idx = 0
            while u_idx < len(ue_results) or b_idx < len(bs_results):
                if u_idx >= len(ue_results):
                    write_decision = "BS"
                elif b_idx >= len(bs_results):
                    write_decision = "UE"
                else:
                    # compare timestamp
                    umf = str(ue_results[u_idx])
                    bmf = str(bs_results[b_idx])
                    umf_ts = float(umf.split(MOBIFLOW_DELIMITER)[2])
                    bmf_ts = float(bmf.split(MOBIFLOW_DELIMITER)[2])
                    if umf_ts < bmf_ts:
                        write_decision = "UE"
                    else:
                        write_decision = "BS"

                if write_decision == "UE":
                    # Assign lock
                    acquire_lock(f)
                    umf = ue_results[u_idx]
                    logging.info("[MobiFlow] Writing UE MobiFlow: " + umf)
                    self.last_write_time = get_time_ms()
                    f.write(umf + "\n")
                    f.flush()
                    release_lock(f)
                    u_idx += 1
                elif write_decision == "BS":
                    # Assign lock
                    acquire_lock(f)
                    bmf = bs_results[b_idx]
                    logging.info("[MobiFlow] Writing BS MobiFlow: " + bmf)
                    self.last_write_time = get_time_ms()
                    f.write(bmf + "\n")
                    f.flush()
                    release_lock(f)
                    b_idx += 1

            time.sleep(self.rpc_query_interval / 1000)
        f.close()

    # P-Best only: support maintenance event
    def pbest_write_maintenance(self):
        f = open(self.csv_file, "a")
        # write a maintenance event to wake up PBest if necessary
        while True:
            cur_time = get_time_ms()
            if self.last_write_time != 0 and cur_time - self.last_write_time > self.maintenance_time_threshold:
                # Assign lock
                acquire_lock(f)
                maintenance_event = MOBIFLOW_DELIMITER.join(["MAINTENANCE", str(cur_time)])
                logging.info("[MobiFlow] Writing Maintenance event: " + maintenance_event.__str__())
                self.last_write_time = cur_time
                f.write(maintenance_event + "\n")
                f.flush()
                release_lock(f)
            time.sleep(self.maintenance_time_threshold / 1000)
        f.close()

    def clear_file(self) -> None:
        f = open(self.csv_file, "w")
        acquire_lock(f)
        f.write("")
        release_lock(f)
        f.close()

    @staticmethod
    def timestamp2str(ts):
        return datetime.datetime.fromtimestamp(ts/1000).__str__() # convert ms into s

