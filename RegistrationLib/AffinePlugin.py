import os
from __main__ import vtk, qt, ctk, slicer
import RegistrationLib


#########################################################
#
#
comment = """

  RegistrationPlugin is a superclass for code that plugs into the
  slicer LandmarkRegistration module.

  These classes are Abstract.

# TODO :
"""
#
#########################################################



#
# RegistrationPlugin
#

class AffinePlugin(RegistrationLib.RegistrationPlugin):
  """ Base class for Registration plugins
  """

  #
  # generic settings that can (should) be overridden by the subclass
  #
  
  # displayed for the user to select the registration
  name = "Affine Registration"
  tooltip = "Uses landmarks to define linear transform matrices"

  # can be true or false
  # - True: landmarks are displayed and managed by LandmarkRegistration
  # - False: landmarks are hidden
  usesLandmarks = True

  # can be any non-negative number
  # - widget will be disabled until landmarks are defined
  landmarksNeededToEnable = 1

  # used for reloading - every concrete class should include this
  sourceFile = __file__

  def __init__(self,parent=None):
    super(AffinePlugin,self).__init__(parent)

  def create(self,registationState):
    """Make the plugin-specific user interface"""
    super(AffinePlugin,self).create(registationState)
    #
    # Linear Registration Pane - initially hidden
    # - interface options for linear registration
    # - TODO: move registration code into separate plugins
    #
    self.linearCollapsibleButton = ctk.ctkCollapsibleButton()
    self.linearCollapsibleButton.text = "Linear Registration"
    linearFormLayout = qt.QFormLayout()
    self.linearCollapsibleButton.setLayout(linearFormLayout)
    self.widgets.append(self.linearCollapsibleButton)

    buttonLayout = qt.QVBoxLayout()
    self.linearModeButtons = {}
    self.linearModes = ("Rigid", "Similarity", "Affine")
    for mode in self.linearModes:
      self.linearModeButtons[mode] = qt.QRadioButton()
      self.linearModeButtons[mode].text = mode
      self.linearModeButtons[mode].setToolTip( "Run the registration in %s mode." % mode )
      buttonLayout.addWidget(self.linearModeButtons[mode])
      self.widgets.append(self.linearModeButtons[mode])
      self.linearModeButtons[mode].connect('clicked(bool)', self.onLinearTransform)
    #self.linearModeButtons[self.logic.linearMode].checked = True
    linearFormLayout.addRow("Registration Mode ", buttonLayout)

    if False:
      self.linearTransformSelector = slicer.qMRMLNodeComboBox()
      self.linearTransformSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
      self.linearTransformSelector.selectNodeUponCreation = True
      self.linearTransformSelector.addEnabled = True
      self.linearTransformSelector.removeEnabled = True
      self.linearTransformSelector.noneEnabled = True
      self.linearTransformSelector.showHidden = False
      self.linearTransformSelector.showChildNodeTypes = False
      self.linearTransformSelector.setMRMLScene( slicer.mrmlScene )
      self.linearTransformSelector.setToolTip( "Pick the transform for linear registration" )
      linearFormLayout.addRow("Target Linear Transform ", self.linearTransformSelector)

    self.parent.layout().addWidget(self.linearCollapsibleButton)


  def destroy(self):
    """Clean up"""
    super(AffinePlugin,self).destroy()

  def onLandmarkMoved(self,state):
    """Perform the linear transform using the vtkLandmarkTransform class"""
    if state.transformed.GetTransformNodeID() != state.linearTransform.GetID():
      state.transformed.SetAndObserveTransformNodeID(state.linearTransform.GetID())

    self.linearMode = "Rigid"

    # try to use user selection, but fall back if not enough points are available
    landmarkTransform = vtk.vtkLandmarkTransform()
    if self.linearMode == 'Rigid':
      landmarkTransform.SetModeToRigidBody()
    if self.linearMode == 'Similarity':
      landmarkTransform.SetModeToSimilarity()
    if self.linearMode == 'Affine':
      landmarkTransform.SetModeToAffine()
    if state.fixedFiducials.GetNumberOfFiducials() < 3:
      landmarkTransform.SetModeToRigidBody()

    volumeNodes = (state.fixed, state.moving)
    fiducialNodes = (state.fixedFiducials,state.movingFiducials)
    points = state.logic.vtkPointForVolumes( volumeNodes, fiducialNodes )
    landmarkTransform.SetSourceLandmarks(points[state.moving])
    landmarkTransform.SetTargetLandmarks(points[state.fixed])
    landmarkTransform.Update()
    t = state.linearTransform
    t.SetAndObserveMatrixTransformToParent(landmarkTransform.GetMatrix())


  def onLinearTransform(self):
    pass



# Add this plugin to the dictionary of available registrations.
# Since this module may be discovered before the Editor itself,
# create the list if it doesn't already exist.
try:
  slicer.modules.registrationPlugins
except AttributeError:
  slicer.modules.registrationPlugins = {}
slicer.modules.registrationPlugins['Affine'] = AffinePlugin

