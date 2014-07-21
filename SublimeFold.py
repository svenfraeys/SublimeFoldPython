############
#
# SublimeFold
# 
# Intelligent Folding System for Python
#
# author : sven.fr
#
############
import sublime
import sublime_plugin

from .CodeManipulator import *
# from .CodeManipulator import *
VERBOSE = 0

def log(message,verbose=1):
    '''print a message with verbose limit
    '''
    if verbose <= VERBOSE:
        print('%s:%s' % (verbose, message) )
    
def fold_getters_setters():
    '''return if the fold getters and setters is active or not
    '''
    settings = sublime.load_settings("FoldPython.sublime-settings")
    return settings.get('fold_getters_setters')


# sublime commands
class FLineTextCommand(sublime_plugin.TextCommand):
    '''text command shared functionality
    '''
    def selectRegions(self, regions):
        '''select the regions
        '''
        view = self.view
        sel = view.sel()

        sel.clear()
        for region in regions:
            sel.add(region)

        if len(regions) > 0:
            view.show(regions[0])

class FoldShowDocumentationCommand(FLineTextCommand):
    '''show all doc strings of selected lines
    '''
    def run(self, edit):
        log('FoldShowDocumentation',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)
            documnentationRegion = line.documentationRegion()

            if documnentationRegion:
                contentRegion = line.contentRegion()
                contentNoDocumentation = sublime.Region(documnentationRegion.b , contentRegion.b )
                regions.append( contentNoDocumentation )

                hasFolded = view.fold(contentNoDocumentation)

                if not hasFolded:
                    view.unfold(contentRegion)
                    view.fold(contentNoDocumentation)
            else:
                contentRegion = line.contentRegion()
                view.fold(contentRegion)

class FoldDeleteDoubleEmptyLinesCommand(FLineTextCommand):
    '''show all doc strings of selected lines
    Still need to finish this
    '''
    def run(self, edit):
        log('FoldDeleteDoubleEmptyLines',1)
        view = self.view
        sel = view.sel()

        loop = True
        while loop:
            emptyFound = 0
            lines = FLineUtils(view).lines()
            for line in lines:
                lineIsEmpty = line.isEmpty()
                if lineIsEmpty:
                    emptyFound += 1

class FoldGoToSiblingUpCommand(FLineTextCommand):
    '''go one sibling up, if no sibling go to parent
    '''
    def run(self, edit):
        log('FoldGoToSiblingUpCommand',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)
            
            siblingUp = line.siblingUp()

            if siblingUp is None:
                siblingUp = line.parent()

            log(siblingUp,1)
            
            if siblingUp:
                siblingUpGoToRegion = siblingUp.goToRegion()
                regions.append(siblingUpGoToRegion)
            else:
                # go back to original
                regions.append(region)

        self.selectRegions(regions)
        
class FoldGoToSiblingDownCommand(FLineTextCommand):
    '''go one sibling down, if no sibling go to adult
    '''
    def run(self, edit):
        log('FoldGoToSiblingDownCommand',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)
            siblingDown = line.siblingDown()

            if siblingDown is None:
                siblingDown = line.adultDown()



            log(siblingDown,1)
            
            if siblingDown:
                siblingDownGoToRegion = siblingDown.goToRegion()
                regions.append(siblingDownGoToRegion)
            else:
                # go back to original
                regions.append(region)

        self.selectRegions(regions)

class FoldGoToSiblingsInverseCommand(FLineTextCommand):
    '''select all the invert siblings
    '''
    def run(self, edit):
        log('FoldGoToSiblingsInverseCommand',1)
        view = self.view
        sel = view.sel()
        regions = []

        # loop regions
        selectRegions = view.sel()
        for region in selectRegions:
            line = FLine(view, region)
            
            siblings = line.siblings()

            log(siblings,1)
            if len(siblings) > 0:
                # add each region of the siblign
                for sibling in siblings:
                    siblingGoToRegion = sibling.goToRegion()
                    add = True

                    for region in selectRegions:
                        if region == siblingGoToRegion:
                            add = False

                    if add:
                        regions.append( siblingGoToRegion )

        # apply selection
        self.selectRegions(regions)

class FoldGoToSiblingsCommand(FLineTextCommand):
    '''select all siblings and itself
    '''
    def run(self, edit):
        log('FoldGoToParent',1)
        view = self.view
        sel = view.sel()
        regions = []

        # loop regions
        for region in ( view.sel()):
            line = FLine(view, region)
            
            siblings = line.siblings()

            

            if len(siblings) > 0:
                # add each region of the siblign
                for sibling in siblings:
                    regions.append( sibling.goToRegion() )

            # if the current has childs also add it
            if line.hasChildren():
                regions.append(line.goToRegion() )

        # apply selection
        self.selectRegions(regions)

class FoldGoToParent(FLineTextCommand):
    '''select the parent parent
    '''
    def run(self, edit):
        log('FoldGoToParent',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)
            
            parent = line.parent()
            
            if parent:
                parentGoToRegion = parent.goToRegion()
                regions.append(parentGoToRegion)
            else:
                # go back to original
                regions.append(region)

        self.selectRegions(regions)

class FoldNewSibling(FLineTextCommand):
    '''create a new sibling
    '''
    def run(self, edit):
        log('FoldNewSibling',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel() ):
            line = FLine(view, region)

            if not line.hasChildren():
                line = line.parent()

            if line == None:
                continue

            region = line.region()
            lineRegion = view.line(region)
            lineString = view.substr( lineRegion )
            typeToCreate = lineString.strip().split(' ')[0]

            

            if line is None:
                continue

            depth = line.depth()
            line
            tabString = line.tabString()
            contentRegion = line.contentRegion()
            # region = sublime.Region( contentRegion.b, contentRegion.b )
            # regions.append(region)
            # point = sublime.Point(contentRegion.b)
            point = contentRegion.b

            insertString = '\n\n' + tabString * depth + typeToCreate 
            view.insert(edit, point, insertString)

            endInsert = point + len(insertString)

            region = sublime.Region(endInsert, endInsert)
            regions.append(region)
    
        self.selectRegions(regions)
        # launch auto complete
        view.run_command("auto_complete")

class FoldGoToTopSibling(FLineTextCommand):
    '''go to the top sibling
    '''
    def run(self, edit):
        log('FoldGoToTopSibling',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)
            
            siblings = line.siblingsUp()
            topSibling = None
            if len(siblings) > 0:
                topSibling = siblings[-1]

            if topSibling is None:
                topSibling = line.parent()

            if topSibling:
                siblingGoToRegion = topSibling.goToRegion()
                regions.append(siblingGoToRegion)
            else:
                # go back to original
                regions.append(region)

        self.selectRegions(regions)

class FoldGoToBottomSibling(FLineTextCommand):
    '''go to the bottom sibling
    '''
    def run(self, edit):
        log('FoldGoToTopSibling',1)
        view = self.view
        sel = view.sel()
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)
            
            siblings = line.siblingsDown()
            sibling = None
            if len(siblings) > 0:
                sibling = siblings[-1]

            # no sibling go to next adult
            if sibling is None:
                sibling = line.adultDown()

            if sibling:
                siblingGoToRegion = sibling.goToRegion()
                regions.append(siblingGoToRegion)
            else:
                # go back to original
                regions.append(region)

        self.selectRegions(regions)
        
class FoldFoldContent(FLineTextCommand):
    '''fold the content
    '''
    def run(self, edit):
        log('FoldFoldContent',1)
        view = self.view
        sel = view.sel()
        
        regions = []
        blackListRegions = []   # all regions that do not need actions anymore
        for region in ( view.sel()):
            line = FLine(view, region)

            # go for parent if active line does not have children
            if not line.hasChildren():
                line = line.parent()


            if line is None:
                continue

            # get full region of line
            lineRegion = view.line( line.region() )
            line = FLine(view, lineRegion )

            if lineRegion in blackListRegions:
                continue

            # getter setter folding
            pythonLine = FPythonLine()
            pythonLine.setData(line.data() )
            setterDown = pythonLine.setterDown()
            getterUp = pythonLine.getterUp()

            if setterDown and fold_getters_setters():
                # if it has a setter down
                blackListRegions.append( setterDown.region() )
                contentRegions = pythonLine.foldGetterSetterRegions()
            elif getterUp and fold_getters_setters():
                # if it has a getter up
                getterUpPythonLine = FPythonLine()
                getterUpPythonLine.setData(getterUp.data() )
                blackListRegions.append( getterUp.region() )
                contentRegions = getterUpPythonLine.foldGetterSetterRegions()

                # getter will take over the final result
                line = getterUpPythonLine
            else:
                # default content region
                contentRegions = [line.contentRegion()]

            if contentRegions:
                totalAllreadyFolded = True

                for contentRegion in contentRegions:
                    hasFolded = view.fold(contentRegion)
                    if hasFolded:
                        totalAllreadyFolded = False


                # if can not fold, go to parent
                if totalAllreadyFolded:
                    parentLine = line.parent()
                    if parentLine:
                        line = parentLine

                if line:
                    regions.append( line.goToRegion() )

        
        self.selectRegions(regions)

class FoldFoldDepth(FLineTextCommand):
    '''show everything exept the given depth
    '''
    def run(self, edit, depth = 0):
        '''run
        '''
        log('FoldFoldDepth',1)
        
        view = self.view
        sel = view.sel()
        foldRegions = []
        regions = []
        linesToFold = []
        linesToUnFold = [] # the root contents we will unfold

        # collect al lines to fold and unfold
        for region in ( view.sel()):
            line = FLine(view, region)

            # go for parent if active line does not have children

            if not line.hasChildren():
                line = line.parent()

            if line is None:
                continue

            linesToUnFold.append(line)

            linesForChildren = [line] # the lines that we will have to fold
            for i in range(depth):
                linesForChildrenLoop = []
                for lineForChildren in linesForChildren:
                    lineChilds = lineForChildren.children()
                    linesForChildrenLoop += lineChilds
                linesForChildren = linesForChildrenLoop

            linesToFold += linesForChildren

        if depth != 0:
            for line in linesToUnFold:
                contentRegion = line.contentRegion()

                if contentRegion:
                    pass
                    view.unfold(contentRegion)

        log('linesToFold=%s' % linesToFold, 4)
        for line in linesToFold:
            contentRegion = line.contentRegion()

            if contentRegion:
                foldRegions.append(contentRegion)
                # hasFolded = view.fold(contentRegion)
        log('foldRegions=%s' % foldRegions, 4)
        view.fold(foldRegions)
        # self.selectRegions(regions)

class FoldEnterContentCommand(FLineTextCommand):
    '''start editing in the content
    '''
    def run(self, edit):
        log('FoldEnterContentCommand',1)
        view = self.view
        sel = view.sel()
        regions = []

        for region in ( view.sel()):
            line = FLine(view, region)
            if not line.hasChildren():
                line = line.parent()
            contentRegion = line.contentRegion()
            if contentRegion:
                view.unfold(contentRegion)
                regions.append(sublime.Region(contentRegion.b , contentRegion.b ) )

        if len(regions) > 0:
            self.selectRegions(regions)
            
class FoldUnfoldContent(FLineTextCommand):
    '''unfold the content of selected regions
    '''
    def run(self, edit):
        log('FoldUnfoldContent',1)
        view = self.view
        sel = view.sel()
        foldRegions = []
        lines = []
        extraRegionsToSelect = []

        for region in ( view.sel()):
            line = FLine(view, region)
            lines.append(line)

            # getter setter folding
            pythonLine = FPythonLine()

            pythonLine.setData(line.data() )
            contentRegions = []

            # get full region of line
            pythonLine = FPythonLine(view, view.line( region ) )

            setterDown = pythonLine.setterDown()
            getterUp = pythonLine.getterUp()
            if setterDown and fold_getters_setters():
                contentRegions = pythonLine.foldGetterSetterRegions()
                # extraRegionsToSelect.append(setterDown.goToRegion() )
            elif getterUp and fold_getters_setters():
                getterUpPythonLine = FPythonLine(view, getterUp.region() )
                contentRegions = getterUpPythonLine.foldGetterSetterRegions()
            else:
                contentRegions = [line.contentRegion()]
            if contentRegions:
                foldRegions += contentRegions

        hasUnfolded = view.unfold(foldRegions)

        # nothing to unfold, go inside the first child

        if not hasUnfolded:
            linesToGoTo = []
            for line in lines:
                childs = line.children()
                # add first child
                if len(childs) > 0:
                    for child in childs:
                        if len(child.children()) > 0:
                            linesToGoTo.append(child)
                            break

            if len(linesToGoTo) > 0:
                goToRegions = []
                for line in linesToGoTo:
                    goToRegion = line.goToRegion()
                    goToRegions.append(goToRegion)

                sel.clear()

                for region in goToRegions:
                    sel.add(region)
        else:
            if len(extraRegionsToSelect) > 0:
                view.sel().add_all(extraRegionsToSelect)

class FoldGoToChildren(FLineTextCommand):
    '''selet all children of selected regions
    '''
    def run(self, edit):
        log('FoldGoToChildren',1)
        view = self.view
        sel = view.sel()
        regions = []
        totalChildren = 0
        originalRegions = []

        for region in ( view.sel()):
            line = FLine(view, region)
            
            children = line.children()
            
            for child in children:
                if not child.hasChildren():
                    continue
                childGoToRegion = child.goToRegion()
                regions.append(childGoToRegion)
            totalChildren += len(children)

            if not line.hasChildren():
                # go back to original
                originalRegions.append(region)

        if totalChildren > 0:
            sel.clear()
            for region in regions:
                sel.add(region)

            if len(regions) > 0:
                view.show(regions[0])
        else:
            if len(originalRegions) > 0:
                sel.clear()

                for region in originalRegions:
                    sel.add(region)
                    
                if len(regions) > 0:
                    view.show(originalRegions[0])

class FoldSelectZeroParentsCommand(FLineTextCommand):
    '''select all parents on 0 depth
    '''
    def run(self, edit):
        log('FoldSelectZeroParents',1)
        view = self.view
        sel = view.sel()
        lineDown = FLine( view, sublime.Region(0,0) )
        loop = True
        toSelect = []
        while loop:
            if lineDown is None:
                loop = False
                break

            if not lineDown.isEmpty():
                if lineDown.depth() == 0:
                    if lineDown.hasChildren():
                        toSelect.append(lineDown)

            lineDown = lineDown.lineDown()

        if len(toSelect) > 0:
            regions = []
            for lineDown in toSelect:
                startRegion = lineDown.goToRegion()
                regions.append(startRegion)

            sel.clear()
            for region in regions:
                sel.add(region)

            if len(regions) > 0:
                view.show(regions[0])

class FoldGoToImport(FLineTextCommand):
    '''go to import section
    '''
    def run(self, edit):
        view = self.view
        sel = view.sel()
        lineDown = FLine( view, sublime.Region(0,0) )
        loop = True
        toSelect = []
        while loop:
            if lineDown is None:
                loop = False
                break

            lineDown = lineDown.lineDown()

            if lineDown == None:
                break

            if lineDown.lineString().find("import ") != -1:
                startRegion = lineDown.goToRegion()
                self.selectRegions([startRegion])
                break

class FoldGoToQuickPanel(FLineTextCommand):
    '''show a quick panel
    '''
    visibleParents = []
    def handleSelect(self, index):
        log('index=%s' % index, 6)

        if index == -1:
            return

        
        selectedLine = self.visibleParents[index]

        self.selectRegions( [selectedLine.goToRegion()] )


    def run(self, edit):
        view = self.view
        visibleRegion = view.visible_region()
        log('visibleRegion=%s' % visibleRegion, 6)
        line = view.line(visibleRegion.a)

        # firstLineRegion = sublime.Region(line)
        # log('firstLineRegion=%s' % firstLineRegion, 6)

        lineDown = FLine( view, line )

        loop = True
        toSelect = []

        visibleParentLines = []
        while loop:
            if lineDown is None:
                loop = False
                break

            if not visibleRegion.contains( lineDown.region() ):
                loop = False
                break

            if len(lineDown.children()) > 0 and not lineDown.isEmpty():
                log(lineDown.lineString(),3)
                visibleParentLines.append(lineDown)

            lineDown = lineDown.lineDown()

        optionList = [line.lineString() for line in visibleParentLines]
        self.visibleParents = visibleParentLines
        sublime.active_window().show_quick_panel(optionList, self.handleSelect)
    
class PythonlineCommand(FLineTextCommand):
    '''test command
    '''
    def run(self, edit):
        view = self.view

        # return
        # for attr in dir(view): log('view.%s' % (attr) , 6)
        
        for region in ( view.sel()):
            line = FLine(view, region)
            lineD = line.children()
            print( len(lineD) )
            
            # for child in line.children():
                # print(child)


# sublime.active_window().active_view().run_command(cmd='Fold_go_to_sibling_down')
# sublime.log_commands(False)
# path = '/home/sven.fr'
# sublime.active_window().run_command('prompt_add_folder', {"dirs" : [path] } )

# view = sublime.active_window().active_view()
