import json
import time
import boto3
from Tafweej_Scheduling_Optimizer import Tafweej_Scheduling_Optimizer

#dynamoDB client
dynamodb = boto3.resource('dynamodb')
optimization_table = dynamodb.Table('optimization_database')

def route_data_to_optimizer(input_data: dict, verbose: int=0):
    selected_optimizer = input_data.get("selected_optimizer")
    input_payload = input_data.get("data")

    if not selected_optimizer or not input_payload:
        return {"error": "Invalid input data. 'selected_optimizer' and 'data' are required."}

    result = None
    start_time = time.time()

    if selected_optimizer == "Tafweej_Scheduling_Optimizer":
        try:
            optimizer = Tafweej_Scheduling_Optimizer()
            model, r, d = optimizer.scheduling_model_corrected(input_payload)
            result = {
                "status": "success",
                "model_status": model.status,
                "decision_variables": {
                    "group_assignemnts": {str(k): v.X for k, v in r.items() if v.X > 0},
                    "dispatch_time": {str(k): v.X for k, v in d.items() if v.X > 0},
                },
            }
            if verbose==1:
                optimizer.print_solution_row(model, r, d, input_data=input_data)
            if verbose==2:
                optimizer.print_solution_row(model, r, d, input_data=input_data)
                optimizer.visualize(model, r, d, input_data=input_data)
        except Exception as e:
            result = {"status": "error", "message": str(e)}

    # elif selected_optimizer == "EV_Stations_Placement_Optimizer":
    #     try:
    #         optimizer = Tafweej_Scheduling_Optimizer()
    #         model, r, d = optimizer.scheduling_model_corrected(input_payload)
    #         result = {
    #             "status": "success",
    #             "model_status": model.status,
    #             "decision_variables": {
    #                 "group_assignemnts": {str(k): v.X for k, v in r.items() if v.X > 0},
    #                 "dispatch_time": {str(k): v.X for k, v in d.items() if v.X > 0},
    #             },
    #         }
    #         if verbose==1:
    #             optimizer.print_solution_row(model, r, d, input_data=input_data)
    #         if verbose==2:
    #             optimizer.print_solution_row(model, r, d, input_data=input_data)
    #             optimizer.visualize(model, r, d, input_data=input_data)
    #     except Exception as e:
    #         result = {"status": "error", "message": str(e)}
    else:
        result = {"error": "Selected optimizer not recognized."}

    end_time = time.time()
    execution_time = end_time - start_time

    result["execution_time"] = execution_time

    #post result to DynamoDB
    optimization_table.put_item(
        Item={
            "job_id": input_data.get("job_id", f"job-{int(time.time())}"),
            "selected_optimizer": selected_optimizer,
            "input_payload": input_payload,
            "result": result,
            "timestamp": int(time.time())
        }
    )
    return result

if __name__ == "__main__":
    input_json = {}

    result = route_data_to_optimizer(input_json)
    print(json.dumps(result, indent=4))
