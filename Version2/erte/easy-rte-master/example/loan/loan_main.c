#include "F_loan.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <Python.h>
#include <wchar.h>

 bool verify_data(outputs_loan_t *outputs) {

    printf("P1: %d, P2: %d\r\n",outputs->P1, outputs->P2);
     if(outputs->P1==1 || outputs->P2==1)
        {printf("\t PROPERTY VIOLATED!!!\n");
        exit(0);
//         //reset output channel
//         outputs->res = 0;
//         outputs->res2 = 0;
//         outputs->res3 = 0;
//         return 0;
     }
//     return 1;
 }


int main() {
    enforcervars_loan_t enf;
    inputs_loan_t inputs;
    outputs_loan_t outputs;
    
    loan_init_all_vars(&enf, &inputs, &outputs);

	Py_Initialize();
    
    PyRun_SimpleString("import sys;import os; os.chdir('..');print(os.getcwd()); sys.path.append(os.getcwd()); sys.argv = ['']");
    
    //mapping Index and Name
    int16_t* map[6];
    map[0] = &inputs.A;
    map[1] = &inputs.B;
    map[2] = &inputs.C;
    map[3] = &inputs.D;
    map[4] = &inputs.E;


    PyObject *module = NULL;

    module = PyImport_ImportModule("lifecycle_main");
    if (!module) {
        goto done;
    }

    PyObject *actions = PyObject_CallMethod(module, "parse_actions",NULL);
        if (!actions) {
            goto done;
        }

    if (PyList_Check(actions)) {
            int len = PyList_Size(actions);
            
            printf("%d\n", len);
            for(int idx = 0; idx<len; idx++){
                PyObject *actor = PyObject_CallMethod(module, "get_peer_index","O", PyList_GetItem(actions, idx));

                 if (!actor){
                    goto done;
                }

                int peer_index = (int)PyLong_AsLong(actor);
                // printf("%d\n",peer_index);
                
                //assigning inputs to enforcer..based on mapping
                for(int i=0;i<5;i++){
                    if(peer_index == i)
                        *map[i] = 1;
                    else 
                        *map[i] = 0;
                }
                
                //erte runtime enforcement
                loan_run_via_enforcer(&enf, &inputs, &outputs);
                verify_data(&outputs);

                if(*map[peer_index] == 1){
                    PyObject *write = PyObject_CallMethod(module, "write_action","O", PyList_GetItem(actions, peer_index));
                    if (!write){
                        goto done;
                    }
                }
                else{
                    printf("Action from mapped index %d is discarded \n", peer_index);
                }
            }

        int flag = 0;
        printf("Do you want to check document tampering(0/1)? ");
        scanf("%d", &flag);

        if(flag==1){
            // Verifying Digest using verify_digest method from lifecycle_main.py
            PyObject *verified = PyObject_CallMethod(module, "verify_digest",NULL);
            if (!verified) {
                goto done;
            }
            int verifier = (int)PyLong_AsLong(verified);
            
            if(verifier==1)
                printf("---No tampering detected in document---\n");
            else{
                printf("---Document is tampered---\n");
                goto done;
            }
        }

        // Read actions of particular group and user_name
        do{
            int user_index;
            printf("Enter mapped Index(0-5) for reading files: ");
            scanf("%d", &user_index);
            assert(user_index>=0 && user_index<7);
            PyObject *reader = PyObject_CallMethod(module, "read_document","i", user_index);
            if (!reader) {
                goto done;
            }
            printf("Want to read for more users(0/1): ");
            scanf("%d", &flag);
        }while(flag);
    }

    done:
        PyErr_Print();
        Py_CLEAR(module);
        Py_Finalize();
        return 0;
}

void loan_run(inputs_loan_t *inputs, outputs_loan_t *outputs) {
    //do nothing
}

// make c_enf c_build  PROJECT=runtime_lifecycle_enforcer
// ./example_runtime_lifecycle_enforcer


