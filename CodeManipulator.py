import sublime, sublime_plugin
VERBOSE = 5

def log(message,verbose=1):
    '''print a message with verbose limit
    '''
    if verbose <= VERBOSE:
        print('%s:%s' % (verbose, message) )

class FLine(object):
    '''line in sublime
    '''
    def __init__(self, view=None, region=None, edit=None):
        '''initiates the line extracter
        '''
        self._tabString = None
        self._view      = view
        self._region    = region
        self._edit      = edit

        if view:
            tabSize = view.settings().get("tab_size")
            tabsToSpaces = view.settings().get("translate_tabs_to_spaces")

            if tabsToSpaces:
                self._tabString = ' ' * tabSize
            else:
                self._tabString = '\t'

    #attributes
    def data(self):
        '''get data
        '''
        dataDict = {}
        dataDict["view"]      = self.view()
        dataDict["region"]    = self.region()
        dataDict["tabString"] = self.tabString()
        dataDict["edit"]      = self.edit()
        return dataDict
    
    def setData(self, dataDict):
        '''set data
        '''
        self.setView( dataDict["view"] )
        self.setRegion( dataDict["region"] )
        self.setTabString( dataDict["tabString"] )
        self.setEdit( dataDict["edit"] )

    def edit(self):
        '''get edit
        '''
        return self._edit
    
    def setEdit(self, value):
        '''set edit
        '''
        self._edit = value

    def tabString(self):
        '''return the tabString
        '''
        return self._tabString

    def setTabString(self, value):
        self._tabString = value

    def region(self):
        '''get region
        '''
        return self._region

    def setRegion(self, value):
        '''set region
        '''
        self._region = value
    
    def view(self):
        '''get view
        '''
        return self._view
    
    def setView(self, value):
        '''set view
        '''
        self._view = value

    # methods
    def isEmpty(self):
        '''check if it is empty line
        '''
        if self.lineString().strip() == '':
            return True
        else:
            return False

    def spaceDepth(self):
        '''return the depth of the selected line
        '''
        view       = self.view()
        region     = self.region()
        lineRegion = view.line(region)
        lineString = view.substr( lineRegion )
        log('lineString=%s' % lineString, 6)

        counter = 0
        for i in lineString.split(' '):
            if i == '':
                counter += 1
            else:
                break
        return counter

    def tabDepth(self):
        '''return the dpeth of the selected line in tabs
        '''
        view       = self.view()
        region     = self.region()
        lineRegion = view.line(region)
        lineString = view.substr( lineRegion )
        counter    = 0

        log('lineString=%s' % lineString, 6)

        for i in lineString.split('\t'):
            if i == '':
                counter += 1
            else:
                break
        return counter

    def depth(self):
        '''return the depth of the region
        '''
        view         = self.view()
        tabSize      = view.settings().get("tab_size")
        tabsToSpaces = view.settings().get("translate_tabs_to_spaces")

        if tabsToSpaces:
            return int(self.spaceDepth() / 4)
        else:
            return int(self.tabDepth() )

    def lineString(self):
        '''return the line as string
        '''
        view       = self.view()
        region     = self.region()
        lineRegion = view.line(region)
        log('lineRegion=%s' % lineRegion, 6)
        return view.substr ( lineRegion )

    def goToRegion(self):
        '''return the region of the beginning of the line
        '''
        view   = self.view()
        region = self.region()

        lineRegion = view.line(region)
        lineString = view.substr ( lineRegion )
        strippedLineString = lineString.strip()
        startOffset = lineString.find(strippedLineString)
        startRegion = sublime.Region( lineRegion.a + startOffset, lineRegion.a + startOffset)
        return startRegion
        
    def lineDown(self):
        '''get the one line up
        '''
        view          = self.view()
        edit          = self.edit()
        region        = self.region()
        lineRegion    = view.line(region)
        endLineBefore = lineRegion.b + 1

        maxRange = view.size()
        if endLineBefore >= maxRange:
            return None

        lineDownRegion = view.line( sublime.Region( endLineBefore, endLineBefore) )

        return FLine(view, lineDownRegion, edit )

    def lineUp(self):
        '''get the one line up
        '''
        view = self.view()
        region = self.region()
        lineRegion = view.line(region)
        endLineBefore = lineRegion.a -1
        edit = self.edit()

        if endLineBefore < 0:
            return None

        lineBeforeRegion = view.line( sublime.Region( endLineBefore, endLineBefore) )

        return FLine(view, lineBeforeRegion, edit)

    def grandChildren(self):
        '''return the grand child
        '''
        depth         = self.depth()
        linedownDepth = None
        lineDown      = self
        loop          = True
        children      = []

        while loop:
            lineDown = lineDown.lineDown()
            if lineDown == None:
                loop = False
                continue

            if lineDown.isEmpty():
                continue

            linedownDepth = lineDown.depth()
            if linedownDepth > depth :
                children.append(lineDown)

            if linedownDepth == depth:
                break

            if linedownDepth < depth:
                break

        return children

    def hasChildren(self):
        '''return if has children
        '''
        depth         = self.depth()
        linedownDepth = None
        lineDown      = self
        loop          = True
        children      = []

        while loop:
            lineDown = lineDown.lineDown()
            if lineDown == None:
                loop = False
                continue

            if lineDown.isEmpty():
                continue

            linedownDepth = lineDown.depth()
            if linedownDepth == depth + 1:
                return True

            if linedownDepth == depth:
                return False

        return False

    def children(self):
        '''return the children
        '''
        depth         = self.depth()
        linedownDepth = None
        lineDown      = self
        loop          = True
        children      = []

        while loop:
            lineDown = lineDown.lineDown()
            if lineDown == None:
                loop = False
                continue

            if lineDown.isEmpty():
                continue

            linedownDepth = lineDown.depth()
            if linedownDepth == depth + 1:
                children.append(lineDown)

            if linedownDepth == depth:
                break

        return children

    def contentRegion(self):
        '''return the region of the whole content.
        '''
        children   = self.grandChildren()
        lastChild  = None
        firstChild = None

        if len(children) == 0:
            return None

        firstChild = children[0]

        if len(children) > 1:
            lastChild = children[-1]
        else:
            lastChild = firstChild

        contentRegion = sublime.Region( firstChild.region().a - 1, lastChild.region().b )
        return contentRegion

    def parent(self):
        '''return parent line
        '''
        depth       = self.depth()
        lineupDepth = None
        lineUp      = self
        loop        = True
        parent      = None

        while loop:
            lineUp = lineUp.lineUp()
            if lineUp == None:
                loop = False
                continue

            if lineUp.isEmpty():
                continue

            lineupDepth = lineUp.depth()
            
            if lineupDepth < depth:
                loop = False
                parent = lineUp
        return parent

    def siblingUp(self):
        '''return sibling upwards
        '''
        depth       = self.depth()
        lineupDepth = None
        lineUp      = self
        loop        = True
        parent      = None

        while loop:
            lineUp = lineUp.lineUp()
            if lineUp == None:
                loop = False
                continue

            if lineUp.isEmpty():
                continue

            if not lineUp.hasChildren():
                continue

            lineupDepth = lineUp.depth()

            # is in a parent, not a sibling
            if lineupDepth < depth:
                return

            if lineupDepth == depth:
                loop = False
                parent = lineUp
        return parent

    def siblingDown(self):
        '''return sibling upwards
        '''
        depth       = self.depth()
        lineupDepth = None
        lineDown    = self
        loop        = True
        parent      = None

        while loop:
            lineDown = lineDown.lineDown()
            if lineDown == None:
                loop = False
                continue

            if lineDown.isEmpty():
                continue

            if len(lineDown.children()) == 0:
                continue

            lineupDepth = lineDown.depth()

            # is in a parent, not a sibling
            if lineupDepth < depth:
                return

            if lineupDepth == depth:
                loop = False
                parent = lineDown
        return parent

    def siblingsUp(self):
        '''return all siblings up
        '''
        loop = True
        siblingUp = self
        siblingUps = []
        while loop:
            siblingUp = siblingUp.siblingUp()
            if siblingUp == None:
                loop = False
                continue
            siblingUps.append(siblingUp)

        return siblingUps

    def siblingsDown(self):
        '''return all siblings down
        '''
        loop         = True
        siblingDown  = self
        siblingDowns = []
        while loop:
            siblingDown = siblingDown.siblingDown()
            if siblingDown == None:
                loop = False
                continue
            siblingDowns.append(siblingDown)

        return siblingDowns

    def siblings(self):
        '''return all siblins up and down
        '''
        siblingsUp = self.siblingsUp()
        siblingsDown = self.siblingsDown()

        siblingsUp.reverse()

        return siblingsUp + siblingsDown
        
    def adultDown(self):
        '''get the adult downwards
        '''
        depth       = self.depth()
        lineupDepth = None
        lineDown    = self
        loop        = True
        parent      = None

        while loop:
            lineDown = lineDown.lineDown()
            if lineDown == None:
                loop = False
                continue

            if lineDown.isEmpty():
                continue

            lineupDepth = lineDown.depth()
            
            if lineupDepth < depth:
                loop = False
                parent = lineDown
        return parent

    def documentationRegion(self):
        '''return the region of the docstring
        '''
        view           = self.view()
        region         = self.region()
        start          = None
        end            = None
        lineDown       = self.lineDown()
        lineDownRegion = lineDown.region()
        lineDownString = view.substr( lineDownRegion )
        docSign        = "'''"

        splittedString = lineDownString.split(docSign)

        if len(splittedString) == 1:
            docSign = '"""'
            splittedString = lineDownString.split(docSign)

        # if contains the doc start
        if len(splittedString) > 1:
            print(lineDownString)
            start = lineDown.region().a

            if len(splittedString) > 2:
                end = lineDown.region().b
            else:
                # find the end of docstring in next lines
                loop = True
                line = lineDown
                while loop:
                    line = line.lineDown()
                    if line is None:
                        loop = False
                        continue

                    lineRegion = line.region()
                    lineString = view.substr( lineRegion )
                    if lineString.find(docSign) != -1:
                        end = lineRegion.b
                        loop = False
        if start and end:
            return sublime.Region(start, end)

    def createChildAbove(self, index, value):
        view = self.view()
        edit = self.edit()
        
        children = self.children()

        child = children[index]
        point = child.region().a
        depthSpace = FLineUtils(self.view() ).createDepth(self.depth() + 1)

        insertString = depthSpace + value + '\n'

        view.insert(edit, point , insertString)
        region = sublime.Region(point + 1, point + len(insertString) )
        return FLine(view,region,edit)

    def createChildBelow(self, index, value):

        view = self.view()
        edit = self.edit()
        
        children = self.children()

        child = children[index]
        point = child.region().b
        contentRegion = child.contentRegion()
        if contentRegion:
            point = contentRegion.b

        depthSpace = FLineUtils(self.view() ).createDepth(self.depth() + 1)

        insertString = '\n' + depthSpace + value

        view.insert(edit, point , insertString)

        region = sublime.Region(point + 1, point + len(insertString) )

        return FLine(view,region,edit)

    def createChild(self, value):
        return self.createLastChild(value)

    def createFirstChild(self, value):
        '''add a child to the current item
        '''
        view = self.view()
        edit = self.edit()
        point = self.region().b

        depthSpace = FLineUtils(self.view() ).createDepth(self.depth() + 1)

        insertString = '\n' + depthSpace + value

        view.insert(edit, point , insertString)
        region = sublime.Region(point + 1, point + len(insertString) )
        return FLine(view,region,edit)

    def createLastChild(self, value):
        '''add a last child
        '''
        view = self.view()
        edit = self.edit()
        region = self.region()

        contentRegion = self.contentRegion()
        if contentRegion:
            point = contentRegion.b
        else:
            point = region.b

        depthSpace = FLineUtils(self.view() ).createDepth(self.depth() + 1)

        insertString = '\n' + depthSpace + value

        view.insert(edit, point , insertString)
        region = sublime.Region(point + 1, point + len(insertString) )
        return FLine(view,region,edit)
    
    def erase(self):
        '''erase this line and children from the view
        '''
        view = self.view()
        edit = self.edit()
        region = self.region()
        startPoint = region.a
        endPoint = region.b

        contentRegion = self.contentRegion()
        if contentRegion:
            endPoint = contentRegion.b

        
        region = sublime.Region( startPoint - 1, endPoint )
        view.erase(edit, region )
    

class FPythonLine(FLine):
    """a python line with smarter analyze function of its task in the file"""

    # constants
    TYPE_CLASS      = "type_class"
    TYPE_EMPTY      = "type_empty"
    TYPE_DEFINITION = "type_definition"

    # methods
    def toClass(self):
        '''go to the class
        '''
        loop = True
        currentParent = self.parent()

        while loop:
            if currentParent is None:
                loop = False
                break

            lineString = currentParent.lineString()
            log(lineString)
            

            if lineString.find('class ') != -1:
                return currentParent

            currentParent = currentParent.parent()

    def toMethod(self):
        '''go to the method
        '''
        loop = True
        currentParent = self.parent()

        while loop:
            if currentParent is None:
                loop = False
                break

            lineString = currentParent.lineString()
            log(lineString)
            

            if lineString.find('def ') != -1:
                return currentParent

            currentParent = currentParent.parent()
    
    def type(self):
        lineString = self.lineString()

        if self.lineString().find('class ') != -1:
            return self.TYPE_CLASS

        if self.lineString().find('def ') != -1:
            return self.TYPE_DEFINITION

        if self.isEmpty():
            return self.TYPE_EMPTY

    def definitions(self):
        definitions = []
        for child in self.children():
            child = FPythonLine(child.view(), child.region(), child.edit() )
            if child.type() == self.TYPE_DEFINITION:
                definitions.append(child)

        return definitions

    def findDefinition(self,name):
        '''return a definition
        '''
        for definition in self.definitions():
            if definition.name() == name:
                return definition

    def createDefinition(self, name, arguments):
        defLineString = 'def {name}({arguments}):'.format(name=name, arguments=','.join(arguments) ) 
        return self.createLastChild(defLineString)

    def findCurrentClass(self):
        loop = True
        currentParent = self.parent()

        if currentParent == None:
            return

        currentParent = FPythonLine( currentParent.view(), currentParent.region(), currentParent.edit() )
        while loop:
            if not currentParent:
                break

            if currentParent.type() == self.TYPE_CLASS:
                return currentParent

            currentParent = currentParent.parent()
            currentParent = FPythonLine( currentParent.view(), currentParent.region(), currentParent.edit() )


    def isClass(self):
        '''check if this is class definition
        '''
        if self.type() == self.TYPE_CLASS:
            return True

        return False
        
    def isDef(self):
        '''check if this is class definition
        '''
        if self.type() == self.TYPE_DEFINITION:
            return True

        return False
        
    def name(self):
        return self._parseNameDef( self.lineString() )

    def _parseNameDef(self, lineString):
        log('lineString=%s' % lineString, 6)
        cutoutFirstPart = lineString.strip().split(' ')[1]
        cutoutLastPart = cutoutFirstPart.split('(')[0]
        defName = cutoutLastPart.strip()
        return defName

    def getterUp(self):
        '''return the down setter def if exists
        '''
        isDef = self.isDef()

        if not isDef:
            return None

        isSiblingGet = False
        view         = self.view()
        siblingUp    = self.siblingUp()

        if not siblingUp:
            return None

        region = self.region()
        
        lineString = view.substr( region )
        log('lineString=%s' % lineString, 6)
        name = self._parseNameDef(lineString)

        if name.find("set") != -1:
            name = name.replace("set", "")
        else:
            return None

        siblingUpRegion = siblingUp.region()
        lineString = view.substr( siblingUpRegion )
        nameSibling = self._parseNameDef(lineString)

        if nameSibling.lower() == "get" + name.lower() or nameSibling.lower() == name.lower():
            isSiblingGet = True

        if isSiblingGet and isDef:
            return siblingUp

    def setterDown(self):
        '''return the down setter def if exists
        '''
        view         = self.view()
        isDef        = self.isDef()
        isSiblingSet = False

        if not isDef:
            return None

        siblingDown = self.siblingDown()

        if not siblingDown:
            return None

        region = self.region()
        
        lineString = view.substr( region )
        log('lineString=%s' % lineString, 6)
        name = self._parseNameDef(lineString)

        if name.find("get") != -1:
            name = name.replace("get", "")

        siblingDownRegion = siblingDown.region()
        lineString = view.substr( siblingDownRegion )
        nameSibling = self._parseNameDef(lineString)

        if nameSibling.lower() == "set" + name.lower():
            isSiblingSet = True

        if isSiblingSet and isDef:
            return siblingDown

    def foldGetterSetterRegions(self):
        '''return needd regions to fold 
        '''
        view = self.view()
        regions = []
        region = self.region()
        lineString = view.substr( region )
        nameDef = self._parseNameDef(lineString)

        startPoint = region.a + self.lineString().find('def ')
        endPoint = startPoint + 4
        regions.append( sublime.Region(startPoint, endPoint) )

        startPoint = region.a + (self.lineString().find(nameDef) + len(nameDef) )
        endPoint = self.siblingDown().contentRegion().b
        regions.append( sublime.Region(startPoint, endPoint) )

        return regions

class FClassLine(FPythonLine):
    pass

class FLineUtils(object):
    """docstring for FLineUtils"""
    def __init__(self, view, edit=None):
        super(FLineUtils, self).__init__()
        self._view = view
        self._lineClass = FLine
        self._edit = edit

    def createDepth(self, depth):
        '''return the depth of the region
        '''
        view         = self.view()
        tabSize      = view.settings().get("tab_size")
        tabsToSpaces = view.settings().get("translate_tabs_to_spaces")

        if tabsToSpaces:
            return ' ' * tabSize * depth
        else:
            return '\t' * depth

    def edit(self):
        '''get edit
        '''
        return self._edit
    
    def setEdit(self, value):
        '''set edit
        '''
        self._edit = value
    
    def view(self):
        ''' get self._view
        '''
        return self._view
    
    def setView(self, value):
        ''' set self._view
        '''
        self._view = value

    def lineClass(self):
        '''get lineClass
        '''
        return self._lineClass
    
    def setLineClass(self, value):
        '''set lineClass
        '''
        self._lineClass = value

    def lines(self):
        '''return all lines in given view
        '''
        view = self.view()
        edit = self.edit()
        totalRegion = sublime.Region( 0, view.size() )
        lineRegions = view.lines(totalRegion)
        lines = []

        for lineRegion in lineRegions:
            line = FLine(view, lineRegion, edit)
            lines.append(line)

        return lines

    def currentLine(self):
        '''return the current line
        '''
        view = self.view()
        edit = self.edit()
        selections = view.sel()

        if len(selections) == 0:
            return None

        line = view.line(selections[0])
        return FLine(view, line, edit)

class FPythonLineUtils(FLineUtils):
    def currentLine(self):
        currentLine = super(FPythonLineUtils, self).currentLine()
        if currentLine:
            line = FPythonLine(currentLine.view(), currentLine.region(), currentLine.edit() )
            return line

    def lines(self):
        lines = super(FPythonLineUtils, self).lines()
        returnLines = []
        for line in lines:
            line = FPythonLine(line.view(), line.region(), line.edit() )
            returnLines.append(line)

        return returnLines

    def findClass(self, name):
        for line in self.lines():
            if line.type() == line.TYPE_CLASS and line.name() == name:
                return line

    def findDefinition(self, name):
        for line in self.lines():
            if line.type() == line.TYPE_DEFINITION and line.name() == name:
                return line

    def classes(self):
        returnLines = []
        for line in self.lines():
            if line.type() == line.TYPE_CLASS :
                returnLines.append(line)
        return returnLines

    def definitions(self):
        returnLines = []
        for line in self.lines():
            if line.type() == line.TYPE_DEFINITION :
                returnLines.append(line)
        return returnLines





def testView():
    views = (sublime.active_window().views())
    for view in views:
        if view.file_name() == r'C:\Users\sven\Dropbox\WG_Code\sfr\common\snippets\helloworld.py':
            return view


    
'''hello world
this is my code
'''
# view = testView()

class CodeManipulatorGetterSetter(sublime_plugin.TextCommand):
    def createGetterSetter(self, name, edit=None):
        if edit is None:
            edit = self._edit

        view = sublime.active_window().active_view()
        view = testView()
        utils = FPythonLineUtils(view, edit)

        # utils.findClass('ClassName').createChildBelow(0, 'hais')
        # return

        attributeName = name
        classLine = utils.currentLine().findCurrentClass()
        initDef = classLine.findDefinition('__init__')
        initDef.createLastChild('self._%s = {}' % attributeName)

        
        getter = classLine.createDefinition(attributeName,['self'])

        
        getter.createChild('return self._%s' % attributeName)
        

        setter = classLine.createDefinition('set%s' % attributeName.title(),['self',attributeName])
        setter.createChild('self._%s = %s' % (attributeName, attributeName) )

    def onDone(self, value):
        print (value)
        self.createGetterSetter(value)

    def run(self, edit):
        '''run
        '''
        self._edit = edit
        window = sublime.active_window()
        window.show_input_panel('attribute', '', self.onDone, None, None)
        # createGetterSetter()

class CodeManipulatorShowActionsCommand(sublime_plugin.TextCommand):
    '''test command
    '''
    def view(self):
        return sublime.active_window().active_view()

    def listCommands(self):
        '''return possible commands
        '''
        
        utils = FPythonLineUtils(self.view)
        classLine = utils.currentLine().findClass()
        if classLine:
            return ['add getter setter']

        return []

    def onDone(self, index):
        print (index)
        command = self.listCommands()[index]
        print (command)

    def run(self, edit):
        window = sublime.active_window()
        view = window.active_view()
        # view = testView()
        utils = FPythonLineUtils(view, edit)
        commands = self.listCommands()
        print(commands)
        window.show_quick_panel(commands, self.onDone)
        


class CodeManipulatorDevelopmentCommand(sublime_plugin.TextCommand):
    '''test command
    '''
    def createGetterSetter(self, edit):
        view = sublime.active_window().active_view()
        view = testView()
        utils = FPythonLineUtils(view, edit)

        # utils.findClass('ClassName').createChildBelow(0, 'hais')
        # return

        attributeName = 'position'
        classLine = utils.findClass('myClass')
        initDef = classLine.findDefinition('__init__')
        initDef.createLastChild('self._%s = {}' % attributeName)

        
        getter = classLine.createDefinition(attributeName,['self'])

        
        getter.createChild('return self._%s' % attributeName)
        

        setter = classLine.createDefinition('set%s' % attributeName.title(),['self',attributeName])
        setter.createChild('self._%s = %s' % (attributeName, attributeName) )
        

        

        

    def run(self, edit):
        # view = self.view
        self.createGetterSetter(edit)        


        return
        # classline = utils.findClass('ClassName')
        for classLine in utils.classes():
            print(classLine.name())
            for definition in classLine.definitions():
                print('\t' + definition.name())
            

        # myDef = classline.findDefinition('ha')
        # myDef.createFirstChild('# comaaasent')
        # myDef.children()[-1].erase()

        # print(classline)
        # print( classline.erase() )
        # line = utils.currentLine()
        # line.erase()

        # line.parent().erase()
        # classLine = utils.currentLine().toClass()
              
        # print(classLine.edit() )

        # child = classLine.createFirstChild('"""hello world"""')
        # print(child.depth())
        # child.createFirstChild("dd")
        # child.erase()

        


