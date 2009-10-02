import sys
import oyAuxiliaryFunctions as oyAux
from PyQt4 import QtGui, QtCore
import mainWindowUI

from oyProjectManager.dataModels import assetModel, projectModel
from oyProjectManager import __version__


#----------------------------------------------------------------------
def UI(environment=None, fileName=None, path=None ):
    """the UI
    """
    global app
    global mainWindow
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow(environment, fileName, path)
    mainWindow.show()
    app.setStyle('Plastique')
    app.exec_()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))






########################################################################
class MainWindow(QtGui.QMainWindow, mainWindowUI.Ui_MainWindow):
    """the main dialog of the system
    """
    
    
    
    #----------------------------------------------------------------------
    def __init__(self, environment, fileName, path):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        # change the window title
        self.setWindowTitle( self.windowTitle() + ' v' + __version__ )
        
        # connect SIGNALs
        # close button
        QtCore.QObject.connect(self.save_button, QtCore.SIGNAL("clicked()"), self.saveButton_action )
        QtCore.QObject.connect(self.cancel_button1, QtCore.SIGNAL("clicked()"), self.close )
        QtCore.QObject.connect(self.cancel_button2, QtCore.SIGNAL("clicked()"), self.close )
        
        # project change ---> update sequence
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self._updateProjectObject )
        QtCore.QObject.connect(self.project_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSequenceList)
        
        # sequence change ---> update _noSubNameField
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self._updateSequenceObject )
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateForNoSubName)
        
        # sequence change ---> update asset type
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetTypeList)
        
        # sequence change ---> update shot lists
        QtCore.QObject.connect(self.sequence_comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotList )
        
        # type change ---> base and shot enable disable
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFieldsInSave )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateShotDependentFieldsInOpen )
        
        # type change ---> fill baseName comboBox
        QtCore.QObject.connect(self.assetType_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameFieldInSave )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateBaseNameFieldInOpen )
        
        # shotName or baseName change ---> fill subName comboBox
        QtCore.QObject.connect(self.shot_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInSave )
        QtCore.QObject.connect(self.shot_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInOpen )
        QtCore.QObject.connect(self.baseName_comboBox1, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInSave )
        QtCore.QObject.connect(self.baseName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateSubNameFieldInOpen )
        
        # subName change ---> fille assets_listWidget2 update ( OPEN TAB only )
        QtCore.QObject.connect(self.subName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.baseName_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.shot_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        QtCore.QObject.connect(self.assetType_comboBox2, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateAssetsListWidget )
        
        # get latest revision --> revision
        QtCore.QObject.connect(self.revision_pushButton, QtCore.SIGNAL("clicked()"), self.updateRevisionToLatest )
        
        # get latest version --> version
        QtCore.QObject.connect(self.version_pushButton, QtCore.SIGNAL("clicked()"), self.updateVersionToLatest )
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # create a database
        self._db = projectModel.Database()
        
        # fill them later
        self._project = None
        self._sequence = None
        
        self.environment = environment
        self.fileName = fileName
        self.path = path
        
        self.setDefaults()
        self.updateProjectList()
        
        self.fillFieldsFromFileInfo()
    
    
    
    #----------------------------------------------------------------------
    def setDefaults(self):
        """sets the default values
        """
        
        # set sub name to MAIN by default
        self.subName_comboBox1.clear()
        self.subName_comboBox1.addItem( "MAIN" )
        
        # append the users to the users list
        userInits = self._db.getUserInitials()
        
        self.user_comboBox1.clear()
        self.user_comboBox1.addItems( userInits )
        
        # update the user with the last selected user
        lastUser = self._db.getLastUser()
        
        userIndex = 0
        
        # get the user index
        for i in range(0, len(userInits)):
            if userInits[i] == lastUser:
                userIndex = i 
        
        self.user_comboBox1.setCurrentIndex( userIndex )
    
    
    
    #----------------------------------------------------------------------
    def fillFieldsFromFileInfo(self):
        """fills the ui fields from the data that comes from the fileName and path
        """
        
        # no use without the path
        if self.path == None:
            return
        
        # get the project and sequence names
        projectName, sequenceName = self._db.getProjectAndSequenceNameFromFilePath( self.path )
        
        currentProject = projectName
        currentSequence = sequenceName
        
        # set the project and sequence
        self.setProjectName(projectName)
        self.setSequenceName(sequenceName)
        
        # no file name no use of the rest
        if self.fileName == None:
            return
        
        # fill the fields with those info
        # create an asset with the file name and get the information from that asset object
        
        #assetObj = assetModel.Asset( projectName, sequenceName, self.fileName )
        assetObj = assetModel.Asset( currentProject, currentSequence, self.fileName )
        
        assetType = assetObj.getTypeName()
        shotNumber = assetObj.getShotNumber()
        baseName = assetObj.getBaseName()
        subName = assetObj.getSubName()
        revNumber = assetObj.getRevisionNumber()
        verNumber = assetObj.getVersionNumber()
        userInitials = assetObj.getUserInitials()
        notes = assetObj.getNotes()
        
        # fill the fields
        # assetType
        element = self.assetType_comboBox1
        element.setCurrentIndex( element.findText( assetType ) )
        
        # shotNumber and baseName
        if asset.isShotDependent():
            element = self.shot_comboBox1
            element.setCurrentIndex( element.findText( shotNumber) )
        else:
            self.baseName_comboBox1.setCurrentIndex( self.baseName_comboBox1.findText(baseName) )
        
        sequenceObject = projectModel.Sequence( projectName, sequenceName )
        
        if not sequenceObject._noSubNameField: # remove this block when the support for old version becomes obsolute
            # sub Name
            self.subName_comboBox1.setCurrentIndex( self.subName_comboBox1.findText(subName) )
        
        # revision
        self.revision_spinBox.setValue( revNumber )
        
        # version : set the version and increase it by one
        self.version_spinBox.setValue( verNumber + 1 )
        
        # user
        element = self.user_comboBox1
        element.setCurrentIndex( element.findText( userInitials ) )
        
        # notes
        self.note_lineEdit1.setText( notes )
    
    
    
    #----------------------------------------------------------------------
    def updateProjectList(self):
        """updates projects list
        """
        
        serverPath = self._db.getServerPath()
        
        projectsList = self._db.getProjects()
        projectsList.sort()
        
        self.server_comboBox.clear()
        self.project_comboBox.clear()
        self.server_comboBox.addItem( serverPath )
        self.project_comboBox.addItems( projectsList )
    
    
    
    #----------------------------------------------------------------------
    def updateSequenceList(self, *arg):
        """updates the sequence according to selected project
        """
        
        self._updateProjectObject()
        currentProjet = self._project
        
        # create a project and ask the child sequences
        self.sequence_comboBox.clear()
        sequences = currentProjet.getSequenceNames()
        
        self.sequence_comboBox.addItems( sequences )
        
        self._updateSequenceObject() # it is not needed but do it for now
    
    
    
    #----------------------------------------------------------------------
    def updateAssetTypeList(self):
        """updates asset types
        """
        
        # get the asset types of that sequence
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get asset types
        assetTypes = currentSequence.getAssetTypes()
        
        assetTypeNames = [ assetType.getName() for assetType in assetTypes ]
        
        # SAVE ASSET TAB
        # clear and update the comboBoxes
        # try to keep the same item in the list
        lastSelectedItem = self.assetType_comboBox1.currentText()
        self.assetType_comboBox1.clear()
        self.assetType_comboBox1.addItems( assetTypeNames )
        # reselect the last selected item
        
        if lastSelectedItem != "":
            self.assetType_comboBox1.setCurrentIndex( self.assetType_comboBox1.findText( lastSelectedItem ) )
        
        # OPEN ASSET TAB
        lastSelectedItem = self.assetType_comboBox2.currentText()
        self.assetType_comboBox2.clear()
        self.assetType_comboBox2.addItems( assetTypeNames )
        #reselect the last seelected item
        if lastSelectedItem != "":
            self.assetType_comboBox2.setCurrentIndex( self.assetType_comboBox2.findText( lastSelectedItem ) )
    
    
    
    #----------------------------------------------------------------------
    def updateShotList(self):
        """
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get shot list
        shotList = currentSequence.getShotList()
        
        # clear and update the list
        self.shot_comboBox1.clear()
        self.shot_comboBox1.addItems( shotList )
        
        self.shot_comboBox2.clear()
        self.shot_comboBox2.addItems( shotList )
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameFieldInSave(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetTypeInSave()
        
        if currentTypeName == None:
            return
        
        comboBox = self.baseName_comboBox1
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
            # do nothing
            return
        
        # get the assets of that type
        allAssets = currentSequence.filterAssets( currentSequence.getAllAssets(), typeName = currentTypeName )
        
        # get the base names
        baseNamesList = [] * 0
        for asset in allAssets:
            baseNamesList.append( asset.getBaseName() )
        
        # remove duplicates
        baseNamesList = oyAux.unique( baseNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # add an item for new items
        comboBox.addItem("")
        
        # add the list
        comboBox.addItems( baseNamesList )    
    
    
    
    #----------------------------------------------------------------------
    def updateBaseNameFieldInOpen(self):
        """updates the baseName fields with current asset baseNames for selected
        type, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        currentTypeName = self.getCurrentAssetTypeInOpen()
        
        if currentTypeName == None:
            return
        
        comboBox = self.baseName_comboBox2
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None or currentType.isShotDependent():
            return
        
        # get the assets of that type
        allAssets = currentSequence.filterAssets( currentSequence.getAllAssets(), typeName = currentTypeName )
        
        # get the base names
        baseNamesList = [] * 0
        for asset in allAssets:
            baseNamesList.append( asset.getBaseName() )
        
        # remove duplicates
        baseNamesList = oyAux.unique( baseNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # add the list
        comboBox.addItems( baseNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameFieldInSave(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            return
        
        currentAssetTypeName = self.getCurrentAssetTypeInSave()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotStringInSave() )
        else:
            currentBaseName = self.getCurrentBaseNameInSave()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox1 )
    
    
    
    #----------------------------------------------------------------------
    def updateSubNameFieldInOpen(self):
        """updates the subName fields with current asset subNames for selected
        baseName, if the type is not shot dependent
        """
        
        # if the current selected type is not shot dependent
        # get all the assets of that type and get their baseNames
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # if the current sequence doesn't support subName field just return
        if currentSequence._noSubNameField:
            return
        
        currentAssetTypeName = self.getCurrentAssetTypeInOpen()
        
        assetTypeObj = currentSequence.getAssetTypeWithName( currentAssetTypeName )
        
        if assetTypeObj == None:
            return
        
        if assetTypeObj.isShotDependent():
            currentBaseName = currentSequence.convertToShotString( self.getCurrentShotStringInOpen() )
        else:
            currentBaseName = self.getCurrentBaseNameInOpen()
        
        self._updateSubNameField( currentSequence, currentAssetTypeName, currentBaseName, self.subName_comboBox2 )
    
    
    
    #----------------------------------------------------------------------
    def _updateSubNameField(self, currentSequence, currentTypeName, currentBaseName, comboBox):
        """
        """
        
        if currentTypeName == None or currentBaseName == None:
            return
        
        currentType = currentSequence.getAssetTypeWithName( currentTypeName )
        
        if currentType == None:
            # do nothing
            return
        
        # get the assets of that type
        allAssets = currentSequence.filterAssets( currentSequence.getAllAssets(), typeName=currentTypeName, baseName=currentBaseName )
        
        # get the subNames
        subNamesList = [] * 0
        for asset in allAssets:
            subNamesList.append( asset.getSubName() )
        
        # add MAIN as default
        subNamesList.append('MAIN')
        
        # remove duplicates
        subNamesList = oyAux.unique( subNamesList )
        
        # add them to the baseName combobox
        comboBox.clear()
        
        # do not add an item for new items, the default should be MAIN
        # add the list
        comboBox.addItems( subNamesList )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFields(self):
        """updates shot dependent fields like the shotList and basName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName1 = self.getCurrentAssetTypeInSave()
        assetTypeName2 = self.getCurrentAssetTypeInOpen()
        
        assetType1 = currentSequence.getAssetTypeWithName( assetTypeName1 )
        assetType2 = currentSequence.getAssetTypeWithName( assetTypeName2 )
        
        if assetType1 != None:
            # enable the shot if the asset type is shot dependent
            isShotDependent = assetType1.isShotDependent() 
            self.shot_comboBox1.setEnabled( isShotDependent )
            self.baseName_comboBox1.setEnabled( not isShotDependent )
        
        # ----- update OPEN ASSET FIELDS -------
        if assetType2 != None:
            isShotDependent = assetType2.isShotDependent()
            self.shot_comboBox2.setEnabled( isShotDependent )
            self.baseName_comboBox2.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFieldsInSave(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetTypeInSave()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox1.setEnabled( isShotDependent )
        self.baseName_comboBox1.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateShotDependentFieldsInOpen(self):
        """updates shot dependent fields like the shotList and baseName
        """
        
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        # get selected asset type name
        assetTypeName = self.getCurrentAssetTypeInOpen()
        
        assetType = currentSequence.getAssetTypeWithName( assetTypeName )
        
        if assetType == None:
            return
        
        # enable the shot if the asset type is shot dependent
        isShotDependent = assetType.isShotDependent() 
        self.shot_comboBox2.setEnabled( isShotDependent )
        self.baseName_comboBox2.setEnabled( not isShotDependent )
    
    
    
    #----------------------------------------------------------------------
    def updateAssetsListWidget(self):
        """fills the assets listWidget with assets
        """
        
        self._updateProjectObject()
        self._updateSequenceObject()
        
        currentProject = self._project
        currentSequence = self._sequence
        
        typeName = self.getCurrentAssetTypeInOpen()
        
        if typeName == '' or typeName == None:
            return
        
        # if the type is shot dependent get the shot number
        # if it is not use the baseName
        if currentSequence.getAssetTypeWithName( typeName ).isShotDependent():
            baseName = currentSequence.convertToShotString( self.getCurrentShotStringInOpen() )
        else:
            baseName = self.getCurrentBaseNameInOpen()
        
        subName = self.getCurrentSubNameInOpen()
        
        # construct the dictionary
        assetInfo = dict()
        assetInfo['baseName'] = baseName
        assetInfo['subName' ] = subName
        assetInfo['typeName'] = typeName
        
        # construct the asset with base info
        #asset = assetModel.Asset( currentProject.getName(), currentSequence.getName())
        asset = assetModel.Asset( currentProject, currentSequence)
        asset.setInfoVariables( **assetInfo )
        
        # get all versions list
        allVersionsList = asset.getAllVersions()
        
        # append them to the asset list view
        self.assets_listWidget2.clear()
        
        if len(allVersionsList) > 0:
            self.assets_listWidget2.addItems( sorted([asset.getFileName() for asset in allVersionsList]) )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentProjectName(self):
        """returns the current project name
        """
        return str( self.project_comboBox.currentText() )
    
    
    
    def getCurrentSequenceName(self):
        """returns the current sequence name
        """
        return str( self.sequence_comboBox.currentText() )
    
    
    
    ##----------------------------------------------------------------------
    #def getCurrentAssetType(self):
        #"""returns the current assetType from the UI
        #"""
        
        #return str( self.assetType_comboBox1.currentText() ), str( self.assetType_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetTypeInSave(self):
        """returns the current assetType from the UI
        """
        return str( self.assetType_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentAssetTypeInOpen(self):
        """returns the current assetType from the UI
        """
        return str( self.assetType_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotStringInSave(self):
        """returns the current shot string from the UI
        """
        
        return str( self.shot_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentShotStringInOpen(self):
        """returns the current shot string from the UI
        """
        
        return str( self.shot_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseNameInSave(self):
        """returns the current baseName from the UI
        """
        
        return str( self.baseName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentBaseNameInOpen(self):
        """returns the current baseName from the UI
        """
        
        return str( self.baseName_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubNameInSave(self):
        """returns the current subName from the UI
        """
        
        return str( self.subName_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentSubNameInOpen(self):
        """returns the current subName from the UI
        """
        
        return str( self.subName_comboBox2.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentRevNumber(self):
        """returns the current revision number from the UI
        """
        
        return str( self.revision_spinBox.value() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentVerNumber(self):
        """returns the current version number from the UI
        """
        
        return str( self.version_spinBox.value() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentUserInitials(self):
        """returns the current user initials from the UI
        """
        
        return str( self.user_comboBox1.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def getCurrentNote(self):
        """returns the current note from the UI
        """
        
        return str( self.note_lineEdit1.text() )
    
    
    
    #----------------------------------------------------------------------
    def updateRevisionToLatest(self):
        """ tries to get the latest revision
        """
        
        # get the asset object from fields
        asset = self.getAssetObjectFromSaveFields()
        
        if asset == None or not asset.isValidAsset():
            return
        
        maxRevAsset, maxRevNumber = asset.getLatestRevision()
        
        if maxRevNumber == None:
            maxRevNumber = 0
            
        # update the field
        self.revision_spinBox.setValue( maxRevNumber )
    
    
    
    #----------------------------------------------------------------------
    def updateVersionToLatest(self):
        """ tries to get the latest version
        """
        
        # get the asset objet from fields
        asset = self.getAssetObjectFromSaveFields()
        
        if asset == None or not asset.isValidAsset():
            return
        
        maxVerAsset, maxVerNumber = asset.getLatestVersion()
        
        if maxVerNumber == None:
            maxVerNumber = 0
        
        # update the field
        self.version_spinBox.setValue( maxVerNumber + 1 )
    
    
    
    #----------------------------------------------------------------------
    def setProjectName(self, projectName):
        """sets the project in the combobox
        """
        if projectName == None:
            return
        
        index = self.project_comboBox.findText( projectName )
        
        if index != -1:
            self.project_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.project_comboBox.update()
    
    
    
    #----------------------------------------------------------------------
    def setSequenceName(self, sequenceName):
        """sets the sequence in the combobox
        """
        if sequenceName == None:
            return
        
        currentIndex = self.sequence_comboBox.currentIndex()
        
        index = self.sequence_comboBox.findText( sequenceName )
        
        if index != -1:
            self.sequence_comboBox.setCurrentIndex( index )
        
        # be sure it is updated
        self.sequence_comboBox.update()
    
    
    
    #----------------------------------------------------------------------
    def getAssetObjectFromSaveFields(self):
        """returns the asset object from the fields
        """
        
        #assetObj = Asset( self._project.getName(), self._sequence.getName() )
        assetObj = assetModel.Asset( self._project, self._sequence )
        
        # gather information
        typeName = self.getCurrentAssetTypeInSave()
        
        assetTypeObj = self._sequence.getAssetTypeWithName(typeName)
        
        if assetTypeObj == None:
            return
        
        isShotDependent = assetTypeObj.isShotDependent()
        if isShotDependent:
            baseName = self._sequence.convertToShotString( self.getCurrentShotStringInSave() )
        else:
            baseName = self.getCurrentBaseNameInSave()
        
        subName = self.getCurrentSubNameInSave()
        rev = self.getCurrentRevNumber()
        ver = self.getCurrentVerNumber()
        userInitials = self.getCurrentUserInitials()
        notes = self.getCurrentNote()
        
        # construct info variables
        infoVars = dict()
        infoVars['baseName'] = baseName
        infoVars['subName'] = subName
        infoVars['typeName'] = typeName
        infoVars['rev'] = rev
        infoVars['ver'] = ver
        infoVars['userInitials'] = userInitials
        infoVars['notes'] = notes
        
        assetObj.setInfoVariables( **infoVars )
        
        return assetObj
    
    
    #----------------------------------------------------------------------
    def getFileNameFromSaveFields(self):
        """returns the file name from the fields
        """
        # get the asset object from fields
        assetObject = self.getAssetObjectFromSaveFields()
        
        return assetObject.getPathVariables(), assetObject
    
    
    
    ##----------------------------------------------------------------------
    #def validateFieldInput(self, UIElement):
        #"""validates the fields input
        #"""
        #pass
        ##if type(UIElement) == type(QtGui.QComboBox):
            ### validate the item
            ##assert(isinstance(UIElement, QtGui.QComboBox))
            
            ##UIElement.a oyAux.file_name_conditioner( UIElement.currentText() )
    
    
    
    #----------------------------------------------------------------------
    def saveButton_action(self):
        """returns the asset file name from the fields and closes the interface
        """
        
        self.close()
        return self.getFileNameFromSaveFields()
    
    
    
    #----------------------------------------------------------------------
    def updateForNoSubName(self):
        """this method will be removed in later version, it is written just to support
        old types of assets those have no subName field
        """
        
        # if the current sequence has no support for subName fields disable them
        self._updateSequenceObject()
        currentSequence = self._sequence
        
        self.subName_comboBox1.setEnabled(not currentSequence._noSubNameField)
        self.subName_comboBox2.setEnabled(not currentSequence._noSubNameField)
    
    
    
    #----------------------------------------------------------------------
    def _updateProjectObject(self):
        """updates the project object if it is changed
        it is introduced to take advantege of the cache system
        """
        
        currentProjectName = self.getCurrentProjectName()
        
        #assert(isinstance(self._project,Project))
        
        if self._project == None or (self._project.getName() != currentProjectName and (currentProjectName != "" or currentProjectName != None ) ):
            self._project = projectModel.Project( currentProjectName )
    
    
    
    #----------------------------------------------------------------------
    def _updateSequenceObject(self):
        """updates the sequence object if it is not
        """
        
        currentSequenceName = self.getCurrentSequenceName()
        
        #assert(isinstance(self._sequence,Sequence))
        
        if self._sequence == None or (self._sequence.getName() != currentSequenceName and (currentSequenceName != "" or currentSequenceName != None ) ):
            self._updateProjectObject()
            #newSeq = sequence.Sequence( self._project.getName(), currentSequenceName )
            newSeq = projectModel.Sequence( self._project, currentSequenceName )
            if newSeq._exists:
                self._sequence = newSeq