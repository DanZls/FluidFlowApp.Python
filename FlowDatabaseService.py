import pymongo
from bson.objectid import ObjectId
from FlowModel import FlowModel
from Environment import databaseConnectionString


class FlowDatabaseService:
    
  def __init__(self):
    self.databaseClient = pymongo.MongoClient(databaseConnectionString)
    self.database = self.databaseClient.FlowDatabase
    self.collection = self.database["FlowModels"]


  def InsertModel(self, model: FlowModel) -> bool:
    serializedModel = {}
    serializedModel["staticBoundarySnapshot"] = model._vortices.tolist()
    serializedModel["dynamicBoundarySnapshots"] = []
    for snapshot in model._dynamicBoundariesSnapshots:
        serializedModel["dynamicBoundarySnapshots"].append(snapshot.tolist())
    result = self.collection.insert_one(serializedModel)
    return result.acknowledged
  

  def GetModel(self, id: str) -> dict:
    dbModel = self.collection.find_one({'_id': ObjectId(id)})
    model = {}
    model["_id"] = str(dbModel.get('_id'))
    model["staticBoundarySnapshot"] = dbModel.get("staticBoundarySnapshot")
    model["dynamicBoundarySnapshots"] = dbModel.get("dynamicBoundarySnapshots")
    return model
  

  def GetModelReferenceList(self) -> list:
    dbModels = self.collection.find()
    models = []
    for dbModel in dbModels:
      model = {}
      model["_id"] = str(dbModel.get('_id'))
      models.append(model)
    return models
  

  def GetModelList(self) -> list:
    dbModels = self.collection.find()
    models = []
    for dbModel in dbModels:
      model = {}
      model["_id"] = str(dbModel.get('_id'))
      model["staticBoundarySnapshot"] = dbModel.get("staticBoundarySnapshot")
      model["dynamicBoundarySnapshots"] = dbModel.get("dynamicBoundarySnapshots")
      models.append(model)
    return models

  
  def DeleteModel(self, id: str) -> bool:
    result = self.collection.delete_one({'_id': ObjectId(id)})
    return result.acknowledged

  
  def Drop(self):
    self.collection.drop()

