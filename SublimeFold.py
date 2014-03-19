############
#
# SublimeFold
# 
# Intelligent Folding System for Python
#
# author : sven.fr
#
#
############
import sublime, sublime_plugin

VERBOSE = 0

def log(message,verbose=1):
    '''print a message with verbose limit
    '''
    if verbose <= VERBOSE:
        print('%s:%s' % (verbose, message) )

def all_lines(view):
    '''return all lines in given view
    '''
    totalRegion = sublime.Region( 0, view.size() )
    lineRegions = view.lines(totalRegion)
    lines = []

    for lineRegion in lineRegions:
        line = FLine(view, lineRegion)
        lines.append(line)

    return lines

class FLine():
    '''line in sublime
    '''
    def __init__(self, view, region):
        '''initiates the line extracter
        '''
        tabSize = view.settings().get("tab_size")
        tabsToSpaces = view.settings().get("translate_tabs_to_spaces")
        self._tabString = None

        if tabsToSpaces:
            self._tabString = ' ' * tabSize
        else:
            self._tabString = '\t'

        self._view = view
        self._region = region
        
    def tabString(self):
        '''return the tabString
        '''
        return self._tabString

    def toClass(self):
        '''go to the class
        '''
        pass

    def toMethod(self):
        '''go to the method
        '''
        pass

    def isClass(self):
        '''check if this is class definition
        '''
        if self.lineString().find('class ') != -1:
            return True
        return False

    def isEmpty(self):
        '''check if it is empty line
        '''
        if self.lineString().strip() == '':
            return True
        else:
            return False

    def region(self):
        '''get region
        '''
        return self._region
    
    def set(self, value):
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

    def spaceDepth(self):
        '''return the depth of the selected line
        '''
        view = self.view()
        region = self.region()
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
        view = self.view()
        region = self.region()
        lineRegion = view.line(region)
        lineString = view.substr( lineRegion )
        log('lineString=%s' % lineString, 6)

        counter = 0
        for i in lineString.split('\t'):
            if i == '':
                counter += 1
            else:
                break
        return counter

    def depth(self):
        '''return the depth of the region
        '''
        view = self.view()

        tabSize = view.settings().get("tab_size")
        tabsToSpaces = view.settings().get("translate_tabs_to_spaces")

        if tabsToSpaces:
            return int(self.spaceDepth() / 4)
        else:
            return int(self.tabDepth() )

    def lineString(self):
        '''return the line as string
        '''
        view = self.view()
        region = self.region()
        lineRegion = view.line(region)
        return view.substr ( lineRegion )

    def goToRegion(self):
        '''return the region of the beginning of the line
        '''
        view = self.view()

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
        view = self.view()
        region = self.region()
        lineRegion = view.line(region)
        endLineBefore = lineRegion.b + 1

        maxRange = view.size()
        if endLineBefore >= maxRange:
            return None

        lineDownRegion = view.line( sublime.Region( endLineBefore, endLineBefore) )

        return FLine(view, lineDownRegion)

    def lineUp(self):
        '''get the one line up
        '''
        view = self.view()
        region = self.region()
        lineRegion = view.line(region)
        endLineBefore = lineRegion.a -1

        if endLineBefore < 0:
            return None

        lineBeforeRegion = view.line( sublime.Region( endLineBefore, endLineBefore) )

        return FLine(view, lineBeforeRegion)

    def grandChildren(self):
        '''return the grand child
        '''
        depth = self.depth()
        linedownDepth = None
        lineDown = self
        loop = True
        children = []

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
        depth = self.depth()
        linedownDepth = None
        lineDown = self
        loop = True
        children = []

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
        depth = self.depth()
        linedownDepth = None
        lineDown = self
        loop = True
        children = []

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
        children = self.grandChildren()
        lastChild = None
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
        depth = self.depth()
        lineupDepth = None
        lineUp = self
        loop = True
        parent = None

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
        depth = self.depth()
        lineupDepth = None
        lineUp = self
        loop = True
        parent = None

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
        depth = self.depth()
        lineupDepth = None
        lineDown = self
        loop = True
        parent = None

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
        loop = True
        siblingDown = self
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
        depth = self.depth()
        lineupDepth = None
        lineDown = self
        loop = True
        parent = None

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
        view = self.view()
        region = self.region()
        start = None
        end = None

        lineDown = self.lineDown()
        lineDownRegion = lineDown.region()
        lineDownString = view.substr( lineDownRegion )
        docSign = "'''"

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
    '''
    def run(self, edit):
        log('FoldDeleteDoubleEmptyLines',1)
        view = self.view
        sel = view.sel()

        loop = True
        while loop:
            emptyFound = 0
            lines = all_lines(view)
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
        for region in ( view.sel()):
            line = FLine(view, region)

            if not line.hasChildren():
                line = line.parent()

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
        foldRegions = []
        regions = []
        for region in ( view.sel()):
            line = FLine(view, region)

            # go for parent if active line does not have children
            if not line.hasChildren():
                line = line.parent()


            if line is None:
                continue

            contentRegion = line.contentRegion()

            if contentRegion:
                foldRegions.append(contentRegion)
                hasFolded = view.fold(contentRegion)

                # if can not fold, go to parent
                if hasFolded is False:
                    parentLine = line.parent()
                    if parentLine:
                        line = parentLine

                if line:
                    regions.append( line.goToRegion() )

        # view.fold(foldRegions)
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
        for region in ( view.sel()):
            line = FLine(view, region)
            lines.append(line)
            contentRegion = line.contentRegion()
            if contentRegion:
                foldRegions.append(contentRegion)

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
            print(len(lineD) )
            
            # for child in line.children():
                # print(child)


# sublime.active_window().active_view().run_command(cmd='Fold_go_to_sibling_down')
# sublime.log_commands(False)
# path = '/home/sven.fr'
# sublime.active_window().run_command('prompt_add_folder', {"dirs" : [path] } )