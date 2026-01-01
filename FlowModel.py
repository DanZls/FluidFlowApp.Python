import numpy as np
import time

from HydroMathUtils import add_points, add_col_points, add_norm_points, del_points
from HydroMathUtils import CalculateMatrix_A, CalculateVector_b, CalculateFieldCoefficients
from HydroMathUtils import CalculateFieldVelocity, CalculateFieldVelocityWithJit


class FlowModel:
  def __init__(self) -> None:
    self.initialStaticBoundaryPoints: np.ndarray = np.empty(shape=[0,2])
    self.initialDynamicBoundaryPoints: np.ndarray = np.empty(shape=[0,2])
    self.pointsDistanceMin: float = 0.05
    self.pointsDistanceMax: float = 0.1
    self.defaultFlowVelocity: np.ndarray = np.array([-1, 0])
    self.simulationTime: float = 1.0
    self.simulationTimeStep: float = 0.01
    self._vortices: np.ndarray = np.empty(shape=[0,2])
    self._collocationPoints: np.ndarray = np.empty(shape=[0,2])
    self._collocationNormals: np.ndarray = np.empty(shape=[0,2])
    self._dynamicPoints: np.ndarray = np.empty(shape=[0,2])
    self._vectorFieldCoefficients: np.ndarray = np.empty(shape=(0,))
    self._dynamicBoundariesSnapshots: list[np.ndarray] = []


  def CalculateVectorField(self) -> None:
    self._vortices = add_points(self.initialStaticBoundaryPoints, self.pointsDistanceMax)
    self._collocationPoints = add_col_points(self._vortices)
    self._collocationNormals = add_norm_points(self._collocationPoints)
    self._dynamicPoints = add_points(self.initialDynamicBoundaryPoints, self.pointsDistanceMax)
    matrix_A = CalculateMatrix_A(self._vortices, self._collocationPoints, self._collocationNormals)
    vector_b = CalculateVector_b(self._collocationNormals, self.defaultFlowVelocity, 1)
    self._vectorFieldCoefficients = CalculateFieldCoefficients(matrix_A, vector_b)


  def RunSimulation(self, timeout=np.inf) -> None:
    startTime = time.time()
    self._dynamicBoundariesSnapshots.append(self._dynamicPoints)
    totalTime = self.simulationTime
    tau = self.simulationTimeStep
    for t in np.arange(0, totalTime, tau):
      if (time.time() - startTime) > timeout:
        break
      print("step", round(t/tau), "/", round(totalTime/tau))
      v = CalculateFieldVelocityWithJit(
        self._dynamicPoints, 
        self._vortices, 
        self._vectorFieldCoefficients, 
        self.defaultFlowVelocity)
      self._dynamicPoints = self._dynamicPoints + v*tau
      self._dynamicPoints = add_points(self._dynamicPoints, self.pointsDistanceMax)
      self._dynamicPoints = del_points(self._dynamicPoints, self.pointsDistanceMin)
      self._dynamicBoundariesSnapshots.append(self._dynamicPoints)