from BenchmarkDataset import BenchmarkDataset
from LLM import LLM
import requests
import re
from FormattedTools import PlaceSearchTool,PlaceDetailsTool,TravelTimeTool,NearbyPlacesTool,DirectionsTool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
import os
import time
import json
from langchain.load.dump import dumps 

def extract(s):
    for char in s:
        if char.isdigit():
            return char
    return None  # Return None if no numeric character is found

def search_evaluation_by_model(data, model_id):
    evaluations = data.get("evaluation", [])
    for evaluation in evaluations:
        if evaluation.get("model_id") == model_id and evaluation.get("type") == 5:
            return evaluation
    return data.get("deleted")

class Evaluator:
    def __init__(self, model: LLM, dataset: BenchmarkDataset):
        self.model = model
        self.dataset = dataset
        self.results = []

    def evaluate(self):
        tools = [PlaceSearchTool(),PlaceDetailsTool(),NearbyPlacesTool(),TravelTimeTool(),DirectionsTool()]
        self.model.load_model()
        data = self.dataset.load_data()
        agent = initialize_agent(
                            tools,
                            llm=self.model.llm,
                            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                            verbose=True,
                            handle_parsing_errors=True, 
                            return_intermediate_steps=True 
                         )
        # print(agent.agent.llm_chain.prompt.messages)

        for i in range(len(data) - 1, -1, -1):
        # for i in range(0, len(data)):
            item = data[i]
            
            # if item["id"] < 475 or item["id"] > 500:
            #     continue
            
            print("Running", i + 1, "/", len(data), ":", item["id"])
            # Check if evaluation with the model is existing
            if(search_evaluation_by_model(item, self.model.id) ):
                print("Already evaluated")
                continue
                
            list=[]
            prompt = (
                item["question"]
                + "Choose the answer from the following options (1/2/3/4). So, the output format will be \"^^Option_Number^^\". Choose the correct answer from the following options: "
            )
            
            if item["classification"] is None:
                prompt = prompt + "Option0: Unanswerable, "
                
            for i in range(len(item["answer"]["options"])):
                if(item["answer"]["options"][i] == ""):
                    break
                prompt = (
                    prompt
                    + "Option"
                    + str(i + 1)
                    + ": "
                    + item["answer"]["options"][i]
                    + ", "
                )

            print("Prompt is created. Now passing to the model.", prompt)
            # with get_openai_callback() as cb:
            try:
                result = agent({"input": prompt})
                output = result.get('output', '')
                intermediate_steps = result.get('intermediate_steps', [])

                   
            except Exception as e:
                print(e)
                response = requests.post(
                    "http://localhost:5000/api/evaluation/", json=[
                                                                        {
                                                                            "query_id": item["id" ],
                                                                            "model_id": self.model.id,
                                                                            "answer": str(e),
                                                                            "verdict": "invalid",
                                                                        }]
                )
                continue
            
            
            print("Output received from the model.", output)
            # print("Intermediate steps received from the model.", intermediate_steps)
            
            
            steps = []
            for step in intermediate_steps:
                # print(step)
                # print(step.log)
                temp = json.loads(dumps(step, pretty=True))
                action = temp[0]
                observation = temp[1]
                
                steps.append(temp)
                # print(temp)
                # print(action)
                # print(observation)
                # break
            
            # Save in file
            # Ensure the directory exists
            directory = f"steps/{self.model.id}"
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Write the steps to the JSON file
            with open(f"{directory}/{item['id']}.json", "w") as f:
                json.dump({ "final_answer": output, "intermediate_steps": steps}, f)
            # return
            
            try:
                match = re.search(r"\^\^(.*?)\^\^", output)
            except:
                match = None
            # print(output, match.group(1))
            result = {
                    "id": item["id"],
                    "prompt": prompt,
                    "response": output,
                    "ground_truth": item["answer"]["correct"] + 1,
                }
            
            try:
                if match:
                    option = extract(match.group(1))
                    response = int(option)   
                    print(response)                 
                    self.results.append(
                        result
                    )
                    if result["ground_truth"] == 0:
                        list.append(
                                {
                                    "query_id": result["id"],
                                    "model_id": self.model.id,
                                    "answer": result["response"],
                                    "verdict": "invalid",
                                    "type": 5,
                                    "option": response
                                }
                            )
                    elif response == result["ground_truth"]:
                        list.append(
                            {
                                "query_id": result["id"],
                                "model_id": self.model.id,
                                "answer": result["response"],
                                "verdict": "right",
                                "type": 5,
                                "option": response
                            }
                        )
                    elif response == 0:
                        list.append(
                            {
                                "query_id": result["id"],
                                "model_id": self.model.id,
                                "answer": result["response"],
                                "verdict": "invalid",
                                "type": 5,
                                "option": response
                            }
                        )
                    else:
                        list.append(
                            {
                                "query_id": result["id"],
                                "model_id": self.model.id,
                                "answer": result["response"],
                                "verdict": "wrong",
                                "type": 5,
                                "option": response
                            }
                        )
                else:
                    self.results.append(
                        {
                            "id": item["id"],
                            "prompt": prompt,
                            "response": output,
                            "ground_truth": item["answer"]["correct"] + 1,
                            "type": 5,
                            
                        }
                    )
                    list.append(
                            {
                                "query_id": result["id"],
                                "model_id": self.model.id,
                                "answer": result["response"],
                                "verdict": "invalid",
                                "type": 5,
                                "option": 0
                            }
                        )
                
            except Exception as e:
                print("Error: The response could not be converted to an integer.")
                list.append(
                            {
                                "query_id": result["id"],
                                "model_id": self.model.id,
                                "answer": result["response"],
                                "verdict": "invalid",
                                "type": 5,
                                "option": 0
                            }
                        )
            if len(list) >= 1:
                response = requests.post(
                    "http://localhost:5000/api/evaluation/", json=list
                )
                # print(response)
                list = []
                  # Sleep for 10 seconds before retrying
            # break
            
            time.sleep(60)
            
        if len(list) > 0:
            response = requests.post(
                "http://localhost:5000/api/evaluation/", json=list
            )
            # print(response)
            list = []

    def compute_metrics(self):
        correct_answers = 0
        total_questions = len(self.results)
        invalid_questions = 0
        invalid_answers = 0

        list = []

        for result in self.results:
            # print(result)
            if result["prompt"] == "":
                invalid_questions += 1
                # print(result)
                # list.append(
                #     {
                #         "query_id": result["id"],
                #         "model_id": self.model.id,
                #         "answer": "",
                #         "verdict": "invalid",
                #     }
                # )
            else:
                try:
                    option = extract(result["response"])
                    # response = int(result["response"].split()[0].strip(":.")[-1])
                    response = int(option)
                    if result["ground_truth"] == 0:
                        invalid_questions += 1
                        # list.append(
                        #     {
                        #         "query_id": result["id"],
                        #         "model_id": self.model.id,
                        #         "answer": response,
                        #         "verdict": "invalid",
                        #     }
                        # )

                    elif response == result["ground_truth"]:
                        correct_answers += 1
                        # list.append(
                        #     {
                        #         "query_id": result["id"],
                        #         "model_id": self.model.id,
                        #         "answer": response,
                        #         "verdict": "right",
                        #     }
                        # )
                    elif response == 0:
                        invalid_answers += 1
                        # list.append(
                        #     {
                        #         "query_id": result["id"],
                        #         "model_id": self.model.id,
                        #         "answer": result["response"],
                        #         "verdict": "invalid",
                        #     }
                        # )
                    else:
                        pass
                        # list.append(
                        #     {
                        #         "query_id": result["id"],
                        #         "model_id": self.model.id,
                        #         "answer": response,
                        #         "verdict": "wrong",
                        #     }
                        # )

                except Exception:
                    # print("Error: The response could not be converted to an integer.")
                    invalid_answers += 1
                    # list.append(
                    #     {
                    #         "query_id": result["id"],
                    #         "model_id": self.model.id,
                    #         "answer": result["response"],
                    #         "verdict": "invalid",
                    #     }
                    # )
        # print(list)

        # print(response)
        accuracy = correct_answers * 100 / (total_questions - invalid_questions)
        accuracy = "{:.2f}".format(accuracy)

        # Open the file in write mode ('w')
        print(f"Accuracy: {accuracy}%\n")
        print(f"{invalid_questions} invalid questions\n")
        print(f"{invalid_answers} invalid responses\n")

    def print_results(self):
        # for result in self.results:
        # print(f"Prompt: {result['prompt']}")
        # print(f"Response: {result['response']}")
        # print(f"Ground Truth: {result['ground_truth']}\n")
        pass
