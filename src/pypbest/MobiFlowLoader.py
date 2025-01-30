import datetime
import time
import threading
from ricxappframe.xapp_frame import RMRXapp
from .lockutil import acquire_lock, release_lock
from ..manager import SdlManager

class MobiFlowLoader():

    def __init__(self, rmr_xapp: RMRXapp, sdl_mgr: SdlManager, query_interval, csv_file, maintenance_time_threshold=0):
        """
        Init MobiFlow Reader

        Parameters:
            rmr_xapp: xApp instance
            sdl_mgr: SDL Manager instance
            query_interval: MobiFlow query interval (in ms)
            csv_file: output csv file for MobiFlow records
            maintenance_time_threshold: time interval to write a maintenance event to wake up PBest (in ms)
        """
        self.rmr_xapp = rmr_xapp
        self.sdl_mgr = sdl_mgr
        self.query_interval = query_interval
        self.maintenance_time_threshold = maintenance_time_threshold  # in ms
        # csv file
        self.csv_file = csv_file
        self.clear_file()
        self.last_write_time = 0
        # Mobiflow namespaces in SDL
        self.BS_MOBIFLOW_NS = "bs_mobiflow"
        self.UE_MOBIFLOW_NS = "ue_mobiflow"
        self.MOBIFLOW_DELIMITER = ";"

    def run(self):
        """
        Start MobiFlow loading threads
        """
        # start a new thread to read database from MobiFlow Auditor xApp
        self.rmr_xapp.logger.info("[App] Starting MobiFlow reading thread")
        self.db_thread = threading.Thread(target=self.load_mobiflow)
        self.db_thread.start()
        # start a new thread to track maintenance event
        self.rmr_xapp.logger.info("[App] Starting Maintenance thread")
        self.maintenance_thread = threading.Thread(target=self.pbest_write_maintenance)
        self.maintenance_thread.start()

    def load_mobiflow(self):
        """
        Load mobiflow entries from the SDL database
        """
        f = open(self.csv_file, "a")
        ue_mobiflow_idx = 0
        bs_mobiflow_idx = 0
        while True:
            bs_results = []
            ue_results = []
            # query MobiFlow from SDL
            while True:
                resp = self.sdl_mgr.get_sdl_with_key(self.UE_MOBIFLOW_NS, ue_mobiflow_idx)
                if resp is None or len(resp) == 0:
                    break
                else:
                    mf_data = resp[str(ue_mobiflow_idx)]
                    ue_mobiflow_idx += 1
                    ue_results.append(mf_data[2:].decode("ascii")) # remove first two non-ascii chars

            while True:
                resp = self.sdl_mgr.get_sdl_with_key(self.BS_MOBIFLOW_NS, bs_mobiflow_idx)
                if resp is None or len(resp) == 0:
                    break
                else:
                    mf_data = resp[str(bs_mobiflow_idx)]
                    bs_mobiflow_idx += 1
                    bs_results.append(mf_data[2:].decode("ascii")) # remove first two non-ascii chars
            
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
                    umf_ts = float(umf.split(self.MOBIFLOW_DELIMITER)[4])
                    bmf_ts = float(bmf.split(self.MOBIFLOW_DELIMITER)[2])
                    if umf_ts < bmf_ts:
                        write_decision = "UE"
                    else:
                        write_decision = "BS"

                if write_decision == "UE":
                    # Assign lock
                    acquire_lock(f)
                    umf = ue_results[u_idx]
                    self.rmr_xapp.logger.info("[MobiFlow] Writing UE MobiFlow: " + umf)
                    self.last_write_time = self.get_time_sec()
                    f.write(umf + "\n")
                    f.flush()
                    release_lock(f)
                    u_idx += 1
                elif write_decision == "BS":
                    # Assign lock
                    acquire_lock(f)
                    bmf = bs_results[b_idx]
                    self.rmr_xapp.logger.info("[MobiFlow] Writing BS MobiFlow: " + bmf)
                    self.last_write_time = self.get_time_sec()
                    f.write(bmf + "\n")
                    f.flush()
                    release_lock(f)
                    b_idx += 1

            time.sleep(self.query_interval / 1000)
        f.close()
            

    # P-Best only: support maintenance event
    def pbest_write_maintenance(self):
        """
        write a maintenance event to wake up PBest if necessary
        """
        f = open(self.csv_file, "a")
        while True:
            cur_time = self.get_time_sec()
            if self.last_write_time != 0 and cur_time - self.last_write_time > (self.maintenance_time_threshold / 1000):
                # Assign lock
                acquire_lock(f)
                maintenance_event = self.MOBIFLOW_DELIMITER.join(["MAINTENANCE", str(cur_time)])
                self.rmr_xapp.logger.info("[MobiFlow] Writing Maintenance event: " + maintenance_event.__str__())
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
    def get_time_ms():
        return time.time() * 1000

    @staticmethod
    def get_time_sec():
        return time.time()

    @staticmethod
    def timestamp2str(ts):
        return datetime.datetime.fromtimestamp(ts/1000).__str__() # convert ms into s