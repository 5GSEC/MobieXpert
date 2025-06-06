import os
import threading
import logging
import json
import datetime
from .log_formatter import LogFormatter
from ..manager import SdlManager

class PBest:
    def __init__(self, exec_path, log_path, csv_file, sdl_mgr: SdlManager):
        # paths and parameters
        self.process_name = exec_path
        self.log_file_name = log_path
        self.log_file = open(log_path, 'w')
        self.process = None
        self.polling_thread = None
        self.event_header = "[EVENT]"
        self.print_debug = True
        self.csv_file = csv_file
        self.sdl_mgr = sdl_mgr
        self.SDL_EVENT_NS = "mobiexpert-event"
        self.event_counter = 0
        # output logger
        self.logger = logging.getLogger("PBest")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False # avoid double printing
        self.warning_event_list = ["Null Cipher & Integrity (NAS)",
                                   "Null Cipher & Integrity (RRC)",
                                   "Uplink IMSI Extractor",
                                   "Uplink DoS Service Request",
                                   "Uplink DoS Attach Request"
                                   ]
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(LogFormatter())
        self.logger.addHandler(ch)

    def run(self):
        # cmd = f"./{self.process_name} > {self.output_fname} &"
        cmd = f"{self.process_name} {self.csv_file} > {self.log_file_name} &"
        #self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=self.work_dir)
        os.system(cmd)
        logging.info(f"PBest process started!")
        # start a new thread to keep log output
        self.polling_thread = threading.Thread(target=self.pbest_poll_output)
        self.polling_thread.start()

    def pbest_poll_output(self):
        f = open(self.log_file_name, 'r')
        while True:
            output = f.readline()
            if output:
                self.process_output(output)
        f.close()

    def process_output(self, output: str):
        if output is None:
            return
        output = output.strip() # remove unnecessary \n
        if output.startswith(self.event_header):
            # print it as an event
            # parse event
            output = output.replace(self.event_header, "").strip()
            event_dict = json.loads(output)
            # if "Time" in event_dict.keys():
                # event_dict["Time"] = self.timestamp2str(event_dict["Time"])
            self.event_counter = self.event_counter + 1

            if event_dict["Level"] == "Warning":
                formatted_str = json.dumps(event_dict, indent=2)
                self.logger.warning("[PBest] Warning event detected")
                self.logger.warning(formatted_str)
                str_list = [str(v) for v in event_dict.values()]
                self.sdl_mgr.store_data_to_sdl(self.SDL_EVENT_NS, str(self.event_counter), ";".join(str_list))
            elif event_dict["Level"] == "Critical":
                formatted_str = json.dumps(event_dict, indent=2)
                self.logger.critical("[PBest] Attack event detected")
                self.logger.critical(formatted_str)
                str_list = [str(v) for v in event_dict.values()]
                self.sdl_mgr.store_data_to_sdl(self.SDL_EVENT_NS, str(self.event_counter), ";".join(str_list))
            elif event_dict["Level"] == "Info":
                formatted_str = json.dumps(event_dict, indent=2)
                self.logger.info("[PBest] Info event detected")
                self.logger.info(formatted_str)
                str_list = [str(v) for v in event_dict.values()]
                self.sdl_mgr.store_data_to_sdl(self.SDL_EVENT_NS, str(self.event_counter), ";".join(str_list))
        else:
            if self.print_debug is True:
                # print it as a log entry
                self.logger.info("[PBest] " + output)

    @staticmethod
    def timestamp2str(ts):
        return datetime.datetime.fromtimestamp(ts).__str__()

    def exit(self):
        if self.process is not None:
            self.process.kill()
        if self.log_file is not None:
            self.log_file.close()

