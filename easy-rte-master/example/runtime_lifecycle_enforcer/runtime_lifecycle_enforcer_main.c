#include "F_runtime_lifecycle_enforcer.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <Python.h>
#include <wchar.h>

bool verify_data(inputs_runtime_lifecycle_enforcer_t inputs, outputs_runtime_lifecycle_enforcer_t outputs) {

    printf("res1: %d, res2: %d, res3: %d\r\n",outputs.res, outputs.res2, outputs.res3);
    if(outputs.res>0 || outputs.res2>0 || outputs.res3>0){
        printf("\t PROPERTY VIOLATED!!!\n");
        outputs.res = 0;
        outputs.res2 = 0;
        outputs.res3 = 0;
        return 0;
    }
    return 1;
}


int main() {
    enforcervars_runtime_lifecycle_enforcer_t enf;
    inputs_runtime_lifecycle_enforcer_t inputs;
    outputs_runtime_lifecycle_enforcer_t outputs;
    
    runtime_lifecycle_enforcer_init_all_vars(&enf, &inputs, &outputs);

	Py_Initialize();
    
    PyRun_SimpleString("import sys;import os; os.chdir('..');print(os.getcwd()); sys.path.append(os.getcwd()); sys.argv = ['']");

	// fp = _Py_fopen(filename1, "r");
	// PyRun_SimpleFile(fp, filename1);

    // PyRun_SimpleString("print(os.listdir())");
    
    //mapping Index and Name
    int16_t* map[6];
    map[0] = &inputs.W_A_G1;
    map[1] = &inputs.W_B_G1;
    map[2] = &inputs.W_C_G1;
    map[3] = &inputs.W_C_G2;
    map[4] = &inputs.W_D_G2;
    map[5] = &inputs.W_E_G2;


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
                for(int i=0;i<6;i++){
                    if(peer_index == i)
                        *map[i] = 1;
                    else 
                        *map[i] = 0;
                }
                
                //erte runtime enforcement
                runtime_lifecycle_enforcer_run_via_enforcer(&enf, &inputs, &outputs);
                
                if(verify_data(inputs, outputs)==true){
                    PyObject *write = PyObject_CallMethod(module, "write_action","O", PyList_GetItem(actions, idx));
                    if (!write){
                        goto done;
                    }
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

void runtime_lifecycle_enforcer_run(inputs_runtime_lifecycle_enforcer_t *inputs, outputs_runtime_lifecycle_enforcer_t *outputs) {
    //do nothing
}

// make c_enf c_build  PROJECT=runtime_lifecycle_enforcer
// ./example_runtime_lifecycle_enforcer


