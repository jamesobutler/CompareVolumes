import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# CompareVolumes
#

class CompareVolumes:
  def __init__(self, parent):
    parent.title = "Compare Volumes"
    parent.categories = ["Wizards"]
    parent.dependencies = []
    parent.contributors = ["Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module helps organize layouts and volume compositing to help compare images
    """
    parent.acknowledgementText = """
    This file was originally developed by Steve Pieper, Isomics, Inc. 
    It was partially funded by NIH grant 3P41RR013218-12S1
    and this work is part of the National Alliance for Medical Image
    Computing (NAMIC), funded by the National Institutes of Health
    through the NIH Roadmap for Medical Research, Grant U54 EB005149.
    Information on the National Centers for Biomedical Computing
    can be obtained from http://nihroadmap.nih.gov/bioinformatics.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['CompareVolumes'] = self.runTest

  def runTest(self):
    tester = CompareVolumesTest()
    tester.runTest()

#
# qCompareVolumesWidget
#

class CompareVolumesWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "CompareVolumes Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Target Volume: ", self.inputSelector)

    #
    # Reference Cursors Buttons
    #
    if False:
      self.refOn = qt.QPushButton("Reference Cursors On")
      parametersFormLayout.addRow(self.refOn)
      self.refOff = qt.QPushButton("Reference Cursors Off")
      parametersFormLayout.addRow(self.refOff)
      # connections
      self.refOn.connect('clicked(bool)', self.onRefOn)
      self.refOff.connect('clicked(bool)', self.onRefOff)

    # Add vertical spacer
    self.layout.addStretch(1)

  def onRefOn(self):
    logic = CompareVolumesLogic()
    print("ref on")
    fiducial = slicer.util.getNode('*FiducialNode*')
    target = self.inputSelector.currentNode()
    logic.referenceCursors(fiducial,target)

  def onRefOff(self):
    logic = CompareVolumesLogic()
    print("ref off")
    logic.clearCursors()

  def onReload(self,moduleName="CompareVolumes"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)
    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()

  def onReloadAndTest(self,moduleName="CompareVolumes"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# CompareVolumesLogic
#

class CompareVolumesLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def viewerPerVolume(self,volumeNodes=None,background=None,label=None,viewNames=[],orientation='Axial'):
    """ Load each volume in the scene into its own
    slice viewer and link them all together.
    If background is specified, put it in the background
    of all viewers and make the other volumes be the 
    forground.  If label is specified, make it active as
    the label layer of all viewers.
    """
    import math

    # use a nice set of colors
    colors = slicer.util.getNode('GenericColors')
    lookupTable = colors.GetLookupTable()

    if not volumeNodes:
      volumeNodes = slicer.util.getNodes('*VolumeNode*').values()

    # make a nearly square array - e.g. 3 volumes in 2x2 grid
    c = math.sqrt(len(volumeNodes))
    columns = math.floor(c)
    if c != columns:
      columns += 1
    r = len(volumeNodes)/columns
    rows = math.floor(r)
    if r != rows:
      rows += 1

    #
    # construct the XML for the layout
    #
    viewItemPattern = """
      <item><view class="vtkMRMLSliceNode" singletontag="{viewName}">
        <property name="orientation" action="default">{orientation}</property>
        <property name="viewlabel" action="default">{viewName}</property>
        <property name="viewcolor" action="default">{color}</property>
      </view></item>
     """
    actualViewNames = []
    index = 1
    layoutDescription = ''
    layoutDescription += '<layout type="vertical">\n'
    for row in range(int(rows)):
      layoutDescription += ' <item> <layout type="horizontal">\n'
      for column in range(int(columns)):
        try:
          viewName = viewNames[index-1]
        except IndexError:
          viewName = 'SliceView-%d-%d' % (row,column)
        rgb = [int(round(v*255)) for v in lookupTable.GetTableValue(index)[:-1]]
        color = '#%0.2X%0.2X%0.2X' % tuple(rgb)
        layoutDescription += viewItemPattern.format(viewName=viewName,orientation=orientation,color=color)
        actualViewNames.append(viewName)
        index += 1
      layoutDescription += '</layout></item>\n'
    layoutDescription += '</layout>'

    # assign the xml to the user-defined layout slot
    layoutNode = slicer.util.getNode('*LayoutNode*')
    if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
      layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    else:
      layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

    # put one of the volumes into each view, or none if it should be blank
    layoutManager = slicer.app.layoutManager()
    for index in range(len(actualViewNames)):
      viewName = actualViewNames[index]
      try:
        volumeNodeID = volumeNodes[index].GetID()
      except IndexError:
        volumeNodeID = ""
      sliceWidget = layoutManager.sliceWidget(viewName)
      compositeNode = sliceWidget.mrmlSliceCompositeNode()
      compositeNode.SetBackgroundVolumeID(volumeNodeID)
      sliceNode = sliceWidget.mrmlSliceNode()
      sliceNode.SetOrientation(orientation)
      sliceWidget.fitSliceToBackground()

  def referenceCursors(self,annotationNode,targetVolume):
    """Create an image of the annotated volume centered
    on the annotation and make it the cursor for looking 
    at another volume
    """
    refID = annotationNode.GetAttribute('AssociatedNodeID')
    referenceVolume = slicer.util.getNode(refID)
    annotationRAS = [0,0,0]
    annotationNode.GetFiducialCoordinates(annotationRAS)

    layoutManager = slicer.app.layoutManager()
    for sliceViewName in layoutManager.sliceViewNames():
      # render the reference volume in each view
      sliceWidget = layoutManager.sliceWidget(sliceViewName)
      sliceView = sliceWidget.sliceView()
      compositeNode = sliceWidget.mrmlSliceCompositeNode()
      compositeNode.SetBackgroundVolumeID(referenceVolume.GetID())
      sliceNode = sliceView.mrmlSliceNode()
      sliceNode.JumpSliceByCentering(*annotationRAS)
      sliceView.forceRender()
      pixmap = qt.QPixmap.grabWidget(sliceWidget)
      hotX, hotY = (pixmap.width()/2, pixmap.height()/2)
      cursor = qt.QCursor(pixmap,hotX,hotY)
      sliceWidget.setCursor(cursor)
      compositeNode.SetBackgroundVolumeID(targetVolume.GetID())

  def clearCursors(self):
    layoutManager = slicer.app.layoutManager()
    for sliceViewName in layoutManager.sliceViewNames():
      sliceWidget = layoutManager.sliceWidget(sliceViewName)
      sliceWidget.unsetCursor()

      """
      baseImage = qt.QImage(":/Icons/AnnotationPointWithArrow.png")
      effectImage = qt.QImage(self.effectIconFiles[effectName])
      width = max(baseImage.width(), effectImage.width())
      pad = -9
      height = pad + baseImage.height() + effectImage.height()
      width = height = max(width,height)
      center = int(width/2)
      cursorImage = qt.QImage(width, height, qt.QImage().Format_ARGB32)
      painter = qt.QPainter()
      cursorImage.fill(0)
      painter.begin(cursorImage)
      point = qt.QPoint(center - (baseImage.width()/2), 0)
      painter.drawImage(point, baseImage)
      point.setX(center - (effectImage.width()/2))
      point.setY(cursorImage.height() - effectImage.height())
      painter.drawImage(point, effectImage)
      painter.end()
      cursorPixmap = qt.QPixmap()
      cursorPixmap = cursorPixmap.fromImage(cursorImage)
      self.effectCursors[effectName] = qt.QCursor(cursorPixmap,center,0)
    return self.effectCursors[effectName]
    """

class CompareVolumesTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_CompareVolumes1()

  def test_CompareVolumes1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # first with two volumes
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    head = sampleDataLogic.downloadMRHead()
    brain = sampleDataLogic.downloadDTIBrain()
    logic = CompareVolumesLogic()
    logic.viewerPerVolume()
    self.delayDisplay('Should be one row with two columns')
    logic.viewerPerVolume(volumeNodes=(brain,head), viewNames=('brain', 'head'))
    self.delayDisplay('Should be two columns, with names')

    # now with three volumes
    otherBrain = sampleDataLogic.downloadMRBrainTumor1()
    logic.viewerPerVolume()
    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain), viewNames=('brain', 'head','otherBrain'))
    self.delayDisplay('Should be two rows with two columns, bottom right blank')

    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain), viewNames=('brain', 'head','otherBrain'), orientation='Sagittal')
    self.delayDisplay('same thing in sagittal')

    logic.viewerPerVolume(volumeNodes=(brain,head,otherBrain), viewNames=('brain', 'head','otherBrain'), orientation='Coronal')
    self.delayDisplay('same thing in coronal')

    self.delayDisplay('Test passed!')
