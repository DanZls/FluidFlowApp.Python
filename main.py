from flask import Flask, request
from flask_cors import CORS
import numpy as np

from FlowModel import FlowModel
from FlowDatabaseService import FlowDatabaseService


app = Flask(__name__)
CORS(app)

# Get model with the given id from database
@app.route("/GetModel/<id>", methods=['GET'])
def GetModel(id: str):
  try:
    model = FlowDatabaseService().GetModel(id)
    return { "model": model, "result": "Ok" }
  except Exception as error:
    return { "result": error.args[0] }

# Delete model with the given id from database
@app.route("/DeleteModel/<id>", methods=['DELETE'])
def DeleteModel(id: str):
  try:
    response = FlowDatabaseService().DeleteModel(id)
    return {"response": response, "result": "Ok" }
  except Exception as error:
    return {"result": error.args[0]}

# Calculate model from request body and save it in database
@app.route("/SaveModel", methods=['POST'])
def CalculateAndSave():
  try:
    data = request.get_json()
    model = FlowModel()
    model.initialStaticBoundaryPoints = np.array(data['staticBoundary'])
    model.initialDynamicBoundaryPoints = np.array(data['dynamicBoundary'])
    model.pointsDistanceMin = data['pointSpacingRange'][0]
    model.pointsDistanceMax = data['pointSpacingRange'][1]
    model.defaultFlowVelocity = np.array(data['defaultVelocity'])
    model.simulationTime = data['simulationTime']
    model.simulationTimeStep = data['simulationTimeStep']
    model.CalculateVectorField()
    model.RunSimulation(timeout=30)
    result = FlowDatabaseService().InsertModel(model)
    return { "result": result, "result": "Ok" }
  except Exception as error:
    return { "result": error.args[0] }

# Get all models in database
@app.route("/GetModelList", methods=['GET'])
def GetModelList():
  try:
    models = FlowDatabaseService().GetModelList()
    return { "models": models, "result": "Ok" }
  except Exception as error:
    return {"result": error.args[0]}

# Get id list of all models in database
@app.route("/GetModelReferenceList", methods=['GET'])
def GetModelReferenceList():
  try:
    models = FlowDatabaseService().GetModelReferenceList()
    return { "models": models, "result": "Ok" }
  except Exception as error:
    return {"result": error.args[0]}


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=8000)
