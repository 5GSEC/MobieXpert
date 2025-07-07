#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/file.h>
#include "rules.c"

int stopflag;
FILE *fp;
extern struct rulelist *pb_rules;
extern int pb_tsnum;
double timestamp;
const char* delimiter = ";";

void inthandler()
{
  stopflag = 1;
  fclose(fp);
  printf("Exiting...\n");
  exit(0);
}

// Function to handle the periodic task
void Engine_Maintenance_Event(char *token) {
    // periodically wake up PBest engine
    struct maintenance_event m;
    int index = 0;
    int totalFeature = 2;
    while (token != NULL) {
        switch (index) {
            case 0:
                // message type
                break;
            case 1:
                m.ts = strtod(token, NULL);
                break;
        }
        ++index;
        token = strtok(NULL, delimiter);
    }
    if (index == totalFeature) {
        assert_maintenance_event(pb_rules, &pb_tsnum, m.ts, 1.0, "");
        engine(pb_rules, &pb_tsnum);
    }
}

void Engine_UE_MobiFlow_Event(char *token) {
    struct ue_mobiflow ue;
    int index = 0;
    int totalFeature = 23; // TODO change this index when updating MobiFlow
    while(token != NULL)
    {
        switch (index) {
            case 0:
                ue.msg_type = token;
                break;
            case 1:
                ue.msg_id = atoi(token);
                break;
            case 2:
                ue.mobiflow_ver = token;
                break;
            case 3:
                ue.generator_name = token;
                break;
            case 4:
                ue.timestamp = strtod(token, NULL);
                break;
            case 5:
                ue.nr_cell_id = strtod(token, NULL);
                break;
            case 6:
                ue.gnb_cu_ue_f1ap_id = atoi(token);
                break;
            case 7:
                ue.gnb_du_ue_f1ap_id = atoi(token);
                break;
            case 8:
                ue.rnti = atoi(token);
                break;
            case 9:
                ue.s_tmsi = strtod(token, NULL);
                break;
            case 10:
                ue.mobile_id = strtod(token, NULL);
                break;
            case 11:
                ue.rrc_cipher_alg = atoi(token);
                break;
            case 12:
                ue.rrc_integrity_alg = atoi(token);
                break;
            case 13:
                ue.nas_cipher_alg = atoi(token);
                break;
            case 14:
                ue.nas_integrity_alg = atoi(token);
                break;
            case 15:
                ue.rrc_msg = token;
                break;
            case 16:
                ue.nas_msg = token;
                break;
            case 17:
                ue.rrc_state = atoi(token);
                break;
            case 18:
                ue.nas_state = atoi(token);
                break;
            case 19:
                ue.rrc_sec_state = atoi(token);
                break;
            case 20:
                ue.reserved_field_1 = strtod(token, NULL);
                break;
            case 21:
                ue.reserved_field_2 = strtod(token, NULL);
                break;
            case 22:
                ue.reserved_field_3 = strtod(token, NULL);
                break;
           
        }
        ++index;
        token = strtok(NULL, delimiter);
    }
    if (ue.rnti != 0 && index == totalFeature) {
        assert_ue_mobiflow(pb_rules, &pb_tsnum, ue.msg_type, ue.msg_id, ue.mobiflow_ver, ue.generator_name, ue.timestamp,
                           ue.nr_cell_id, ue.gnb_cu_ue_f1ap_id, ue.gnb_du_ue_f1ap_id, ue.rnti, ue.s_tmsi, ue.mobile_id,
                           ue.rrc_cipher_alg, ue.rrc_integrity_alg, ue.nas_cipher_alg, ue.nas_integrity_alg,
                           ue.rrc_msg, ue.nas_msg, ue.rrc_state, ue.nas_state, ue.rrc_sec_state,
                           ue.reserved_field_1, ue.reserved_field_2, ue.reserved_field_3, 1.0, "");
        engine(pb_rules, &pb_tsnum);
    }
}

void Engine_BS_MobiFlow_Event(char *token) {
    struct bs_mobiflow bs;
    int index = 0;
    int totalFeature = 11; // TODO change this index when updating MobiFlow
    while (token != NULL) {
        switch (index) {
            case 0:
                bs.msg_type = token;
                break;
            case 1:
                bs.msg_id = atoi(token);
                break;
            case 2:
                bs.timestamp = strtod(token, NULL);
                break;
            case 3:
                bs.mobiflow_ver = token;
                break;
            case 4:
                bs.generator_name = token;
                break;
            case 5:
                bs.nr_cell_id = strtod(token, NULL);
                break;
            case 6:
                bs.mcc = token;
                break;
            case 7:
                bs.mnc = token;
                break;
            case 8:
                bs.tac = token;
                break;
            case 9:
                bs.report_period = atoi(token);
                break;
            case 10:
                bs.status = atoi(token);
                break;
        }
        ++index;
        token = strtok(NULL, delimiter);
    }
    if (bs.nr_cell_id != -1 && index == totalFeature) {
        assert_bs_mobiflow(pb_rules, &pb_tsnum, bs.msg_type, bs.msg_id, bs.timestamp, bs.mobiflow_ver, bs.generator_name,
                           bs.nr_cell_id, bs.mcc, bs.mnc, bs.tac, bs.report_period, bs.status,
                           1.0, "");
        engine(pb_rules, &pb_tsnum);
    }
}


int main (int argc, char *argv[])
{
    if (argc < 2) {
        printf("Please provide input csv file name\n");
        exit(1);
    }

	setvbuf(stdout, NULL, _IONBF, 0); // disable output buffering

	pb_init(&pb_rules); // initialize expert system

	// parse CSV input
	const int MAXCHAR = 500;
	char row[MAXCHAR];
	char *token;
	char* r;

    signal(SIGINT, inthandler); // register SIGINT handler

	while (1) {
	  fp = fopen(argv[1], "r");
	  if (fp /* != NULL */)
	    break;
	  sleep (2);
	}

	while(1) {
        // Acquire lock
        flock(fileno(fp), LOCK_EX);
        r = fgets(row, MAXCHAR, fp);
        flock(fileno(fp), LOCK_UN);
        if (r != NULL) {
            if (row == NULL)
                continue;   // TODO fix later
            token = strtok(row, delimiter);
            if (strcmp(token, "UE") == 0) {
                Engine_UE_MobiFlow_Event(token);
            }
            else if (strcmp(token, "BS") == 0) {
                Engine_BS_MobiFlow_Event(token);
            }
            else if (strcmp(token, "MAINTENANCE") == 0) {
                Engine_Maintenance_Event(token);
            }
        } // end of if
        else {
            clearerr(fp);
        }

	} // end of while
	fclose(fp);
	return 0;
}

