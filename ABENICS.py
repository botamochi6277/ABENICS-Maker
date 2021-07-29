"""
Fusion360 Script to make Special Spherical Gear, ABENICS

Script to make ABENICS with Fusion360.
This script is derived from SpurGear.py which is a sample of Fusion360 written by Brian Ekins
Kazuki Abe, Kenjiro Tadakuma and Riichiro Tadakuma develop ABENICS. 
ABENICS system is patent pending.
You have to pay attention to create and use the gears and application.

Note:
    Default length unit of Fusion360 Script is cm.

    IEEE Paper of ABENICS: https://ieeexplore.ieee.org/document/9415699
    Video :https://www.youtube.com/watch?v=hhDdfiRCQS4
    Gear: https://en.wikipedia.org/wiki/Gear
    Patent: https://jstore.jst.go.jp/nationalPatentDetail.html?pat_id=38455
"""

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_imgInputEnglish = adsk.core.ImageCommandInput.cast(None)
_imgInputMetric = adsk.core.ImageCommandInput.cast(None)
# adsk standard system
_standard = adsk.core.DropDownCommandInput.cast(None)
# common gear parameters
_pressureAngle = adsk.core.DropDownCommandInput.cast(None)
_pressureAngleCustom = adsk.core.ValueCommandInput.cast(None)
_module = adsk.core.ValueCommandInput.cast(None)
_rootFilletRad = adsk.core.ValueCommandInput.cast(None)
_backlash = adsk.core.ValueCommandInput.cast(None)
_diaPitch = adsk.core.ValueCommandInput.cast(None)
_gear_ratio = adsk.core.StringValueCommandInput.cast(None)

# SH Gear
_num_teeth_sh = adsk.core.StringValueCommandInput.cast(None)
# MP Gear
_thickness = adsk.core.ValueCommandInput.cast(None)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
# Engrave
_num_rotation_steps = adsk.core.StringValueCommandInput.cast(None)

# reference
_pitch_diameter_sh = adsk.core.TextBoxCommandInput.cast(None)
_pitch_diameter_mp = adsk.core.TextBoxCommandInput.cast(None)


_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []


_app_name = 'ABENICS'


def defineCommandDialog(inputs, standard, pressureAngle):
    global _standard, _pressureAngle, _pressureAngleCustom, _diaPitch, _module, _rootFilletRad, _thickness, _holeDiam, _backlash, _imgInputEnglish, _imgInputMetric, _errMessage
    # _imgInputEnglish = inputs.addImageCommandInput(
    #     'gearImageEnglish', '', 'Resources/GearEnglish.png')
    # _imgInputEnglish.isFullWidth = True

    _imgInputMetric = inputs.addImageCommandInput(
        'gearImageMetric', '', 'Resources/GearMetric.png')
    _imgInputMetric.isFullWidth = True

    _standard = inputs.addDropDownCommandInput(
        'standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
    # if standard == "English":
    #     _standard.listItems.add('English', True)
    #     _standard.listItems.add('Metric', False)
    #     _imgInputMetric.isVisible = False
    # else:
    # _standard.listItems.add('English', False)
    _standard.listItems.add('Metric', True)
    # _imgInputEnglish.isVisible = False

    _pressureAngle = inputs.addDropDownCommandInput(
        'pressureAngle', 'Pressure Angle', adsk.core.DropDownStyles.TextListDropDownStyle)
    if pressureAngle == '14.5 deg':
        _pressureAngle.listItems.add('14.5 deg', True)
    else:
        _pressureAngle.listItems.add('14.5 deg', False)

    if pressureAngle == '20 deg':
        _pressureAngle.listItems.add('20 deg', True)
    else:
        _pressureAngle.listItems.add('20 deg', False)

    if pressureAngle == '25 deg':
        _pressureAngle.listItems.add('25 deg', True)
    else:
        _pressureAngle.listItems.add('25 deg', False)

    if pressureAngle == 'Custom':
        _pressureAngle.listItems.add('Custom', True)
    else:
        _pressureAngle.listItems.add('Custom', False)


class ABENICS:
    """
    Attributes:
        module (float): module of gears
        pressure_angle (float): pressure angle of gears
        backlash (float): backlash

        diameter_sh (float): diameter of pitch circle of a ball gear
        num_teeth_sh (int): the num. of teeth of the ph-gear as a spurgear

        diameter_mp (float): diameter of pitch circle of the mp-gear
        num_teeth_mp (int): the num. of teeth of the mp-gear 
        diameter_hole_mp (float): hole diameter of the mp-gear
        thickness_mp (float): thickness of the mp-gear

        gear_ratio (float): gear ratio (SH/MP) should be 2.0

    Notes:
        module = diameter / num_teeth
        pitch_angle = 2 * pi / num_teeth

        https://en.wikipedia.org/wiki/Backlash_(engineering)
    """

    def __init__(self, design,
                 module=1.0, pressure_angle=20.0 * math.pi/180.0,
                 num_teeth_sh=40, gear_ratio=2, thickness=4.0, hole_diameter=0.4, backlash=0) -> None:
        # common parameters
        self.module = module
        self.pressure_angle = pressure_angle  # [rad]
        self.backlash = backlash
        self.gear_ratio = gear_ratio

        self.num_teeth_sh = num_teeth_sh

        self.diameter_sh = 0.1*(self.module*self.num_teeth_sh)  # mm->cm
        self.pitch_angle = 2.0*math.pi/self.num_teeth_sh

        self.diameter_mp = self.diameter_sh/self.gear_ratio
        self.num_teeth_mp = int(self.num_teeth_sh/self.gear_ratio)
        self.diameter_hole_mp = hole_diameter
        self.thickness_mp = thickness

        # Create a new component by creating an occurrence.
        self.root_occurrences = design.rootComponent.occurrences

    def print(self):
        print('module : {:0.2f}'.format(self.module))
        print('pressure_angle : {:0.2f} deg'.format(
            self.pressure_angle*(180/math.pi)))
        print('backlash : {:0.2f} mm'.format(10*self.backlash))
        print('gear_ratio : {:0.2f}'.format(self.gear_ratio))
        print('num_teeth_sh : {:0.2f}'.format(self.num_teeth_sh))
        print('diameter_sh : {:0.2f} mm'.format(10*self.diameter_sh))
        print('diameter_mp : {:0.2f} mm'.format(10*self.diameter_mp))

    def make_sh_comp(self):
        mat = adsk.core.Matrix3D.create()
        newOcc = self.root_occurrences.addNewComponent(mat)
        self.sh_comp = adsk.fusion.Component.cast(newOcc.component)

    def make_mp_comp(self):
        mat = adsk.core.Matrix3D.create()
        newOcc = self.root_occurrences.addNewComponent(mat)
        self.mp_comp = adsk.fusion.Component.cast(newOcc.component)

    def draw_tooth(self, sketch, root_diameter, tip_diameter, angle=0):
        base_diameter = self.diameter_sh * math.cos(self.pressure_angle)

        # Calculate points along the involute curve.
        involute_point_count = 15  # resolution
        involuteIntersectionRadius = 0.5 * base_diameter
        involute_points_a = []
        involute_points_a = get_involutePoints(
            base_diameter, tip_diameter, num=involute_point_count)

        # Get the point along the tooth that's at the pitch diameter and then
        # calculate the angle to that point.
        pitch_involute_point = involutePoint(
            0.5*base_diameter, 0.5*self.diameter_sh)
        pitch_point_angle = math.atan(
            pitch_involute_point.y / pitch_involute_point.x)

        # Determine the angle defined by the tooth thickness as measured at
        # the pitch diameter circle.
        # ! this is half circular pitch angle
        tooth_thickness_angle = (2 * math.pi) / (2 * self.num_teeth_sh)

        # Determine the angle needed for the specified backlash.
        backlashAngle = (self.backlash / (0.5*self.diameter_sh)) * .25

        # Determine the angle to rotate the curve.
        rotate_angle = -((0.5*tooth_thickness_angle) +
                         pitch_point_angle - backlashAngle)

        # Rotate the involute so the middle of the tooth lies on the x axis.
        involute_points_a = rotate_points(involute_points_a, rotate_angle)

        # Create a new set of points with a negated y.  This effectively mirrors the original
        # points about the X axis.
        involute_points_b = []
        for i in range(0, involute_point_count):
            involute_points_b.append(adsk.core.Point3D.create(
                involute_points_a[i].x, -involute_points_a[i].y, 0))

        # rotate points by inputted angle
        involute_points_a = rotate_points(
            involute_points_a, angle)
        involute_points_b = rotate_points(
            involute_points_b, angle)

        curve1Dist, curve1Angle = xy2polar(involute_points_a)
        curve2Dist, curve2Angle = xy2polar(involute_points_b)

        sketch.isComputeDeferred = True

        # Create and load an object collection with the points.
        point_set = adsk.core.ObjectCollection.create()
        for i in range(0, involute_point_count):
            point_set.add(involute_points_a[i])

        # Create the first spline.
        spline_a = sketch.sketchCurves.sketchFittedSplines.add(point_set)

        # Add the involute points for the second spline to an ObjectCollection.
        point_set = adsk.core.ObjectCollection.create()
        for i in range(0, involute_point_count):
            point_set.add(involute_points_b[i])

        # Create the second spline.
        spline_b = sketch.sketchCurves.sketchFittedSplines.add(point_set)

        # Draw the arc for the top of the tooth.
        midPoint = adsk.core.Point3D.create((0.5*tip_diameter), 0, 0)
        midPoint = rotate_points(midPoint, angle)

        sketch.sketchCurves.sketchArcs.addByThreePoints(
            spline_a.endSketchPoint, midPoint, spline_b.endSketchPoint)

        # Check to see if involute goes down to the root or not.  If not, then
        # create lines to connect the involute to the root.
        if(base_diameter < root_diameter):
            sketch.sketchCurves.sketchLines.addByTwoPoints(
                spline_b.startSketchPoint, spline_a.startSketchPoint)
        else:
            rootPoint1 = adsk.core.Point3D.create(
                (0.5*root_diameter - 0.001) * math.cos(curve1Angle[0]), (0.5*root_diameter) * math.sin(curve1Angle[0]), 0)
            line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(
                rootPoint1, spline_a.startSketchPoint)

            rootPoint2 = adsk.core.Point3D.create(
                (0.5*root_diameter - 0.001) * math.cos(curve2Angle[0]), (0.5*root_diameter) * math.sin(curve2Angle[0]), 0)
            line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(
                rootPoint2, spline_b.startSketchPoint)

            baseLine = sketch.sketchCurves.sketchLines.addByTwoPoints(
                line1.startSketchPoint, line2.startSketchPoint)

            # Make the lines tangent to the spline so the root fillet will behave correctly.
            line1.isFixed = True
            line2.isFixed = True
            sketch.geometricConstraints.addTangent(spline_a, line1)
            sketch.geometricConstraints.addTangent(spline_b, line2)

    def assign_values(self, **kwargs):
        pass

    def draw_gear(self, sketch, axis_angle=0):
        # https://eow.alc.co.jp/search?q=dedendum
        # https://khkgears.net/new/gear_knowledge/abcs_of_gears-b/basic_gear_terminology_calculation.html
        # what is 20?

        # Tooth depth
        # h = 2.25 * self.module
        addendum = 1.0 * self.module
        dedendum = 1.25 * self.module
        dedendum *= 0.1  # mm->cm

        root_dia = self.diameter_sh - 2 * dedendum
        # root_dia = self.diameter_sh - 2.5*self.module

        baseCircleDia = self.diameter_sh * math.cos(self.pressure_angle)

        # tip diameter
        # outsideDia = (self.num_teeth_sh + 2) / self.diameter_sh
        tip_diameter = self.diameter_sh + 2 * self.module * 0.1
        # tip_diameter = self.diameter_sh + 2 * addendum

        origin = adsk.core.Point3D.create(0, 0, 0)
        # Draw a root fan shape.
        arc_start = adsk.core.Point3D.create(0.5*root_dia, 0, 0)
        arc_end = adsk.core.Point3D.create(-0.5*root_dia, 0, 0)
        arc_start = rotate_points(arc_start, axis_angle)
        arc_end = rotate_points(arc_end, axis_angle)

        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(
            origin, arc_start, math.pi)
        l = sketch.sketchCurves.sketchLines.addByTwoPoints(
            arc_start,
            arc_end)

        # draw tip circle
        c = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 0.5*tip_diameter)
        c.isConstruction = True

        # draw tooth
        for i in range(int(0.5*self.num_teeth_sh)):
            angle = self.pitch_angle * i + 0.5*self.pitch_angle + axis_angle
            self.draw_tooth(sketch,
                            root_diameter=root_dia,
                            tip_diameter=tip_diameter,
                            angle=angle)

        sketch.isComputeDeferred = False

        return sketch, l

    def revolve_ballgear(self, sk, ax_line,
                         operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                         bodies=None):
        # revolve profiles
        revolves = self.sh_comp.features.revolveFeatures
        profile_set = adsk.core.ObjectCollection.create()
        for i in range(len(sk.profiles)):
            profile_set.add(sk.profiles.item(i))
        revInput = revolves.createInput(
            profile_set, ax_line, operation)
        if bodies is not None:
            revInput.participantBodies = bodies
        angle = adsk.core.ValueInput.createByReal(2*math.pi)
        revInput.setAngleExtent(False, angle)
        rev = revolves.add(revInput)
        return rev

    def draw_mp_sketch(self, sketch):
        tip_diameter = self.diameter_mp + 2 * self.module * 0.1

        center = adsk.core.Point3D.create(
            0.5*self.diameter_mp+0.5*self.diameter_sh, 0, 0)
        c = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            center, 0.5*tip_diameter)

        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            center, 0.5*self.diameter_hole_mp)

    def extrude_mp(self, sketch, thickness):
        prof = adsk.fusion.Profile.cast(None)
        # Find the profile that uses both circles.
        for prof in sketch.profiles:
            if prof.profileLoops.count == 2:
                break

        extrudes = self.mp_comp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(thickness)
        # extInput.setDistanceExtent(False, distance)
        extInput.setSymmetricExtent(distance, True)
        mp_extrude = extrudes.add(extInput)
        return mp_extrude

    def engrave(self):
        combines = self.mp_comp.features.combineFeatures
        tool_bodies = adsk.core.ObjectCollection.create()
        tool_bodies.add(self.sh_comp.bRepBodies.item(0))
        combine_input = combines.createInput(
            targetBody=self.mp_comp.bRepBodies.item(0),
            toolBodies=tool_bodies
        )
        combine_input.isKeepToolBodies = True
        combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        return combines.add(combine_input)

    def rotate_gears(self, angle):
        """rotate gear bodies

        Args:
            angle (float): 0--2*math.pi
        """
        z_up = adsk.core.Vector3D.create(0, 0, 1)
        # rotate sh gear
        moves = self.sh_comp.features.moveFeatures
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(self.sh_comp.bRepBodies.item(0))

        tf = adsk.core.Matrix3D.create()
        tf.setToRotation(
            angle=angle/self.gear_ratio,
            axis=z_up,
            origin=adsk.core.Point3D.create(0, 0, 0)
        )

        move_input = moves.createInput(bodies, tf)
        move_sh = moves.add(move_input)

        # rotate mp gear
        moves = self.mp_comp.features.moveFeatures
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(self.mp_comp.bRepBodies.item(0))
        tf = adsk.core.Matrix3D.create()
        x = 0.5 * self.diameter_sh + 0.5*self.diameter_mp
        tf.setToRotation(
            angle=-angle,
            axis=z_up,
            origin=adsk.core.Point3D.create(x, 0, 0)
        )
        move_input = moves.createInput(bodies, tf)
        move_mp = moves.add(move_input)

        return move_sh, move_mp

    def Create():
        # Draw Spurgear for a ball gear
        # Revolve the spurgear sketch around x-axis to create a new body
        # Revolve the spurgear sketch around y-axis

        # Draw Circles for a pinion gear
        # Extrude the sketch to make a new body
        # rotate ball gear and the new body and engrave teeth
        pass


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('adskABENICSPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition(
                'adskABENICSPythonScript', 'ABENICS', 'Creates a ABENICS component', 'Resources/ABENICS')

        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class GearCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Verfies that a value command input has a valid expression and returns the
# value if it does.  Otherwise it returns False.  This works around a
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager

        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(
                valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def setInitialUnit(design):
    defaultUnits = design.unitsManager.defaultLengthUnits

    # Determine whether to use inches or millimeters as the intial default.
    global _units
    if defaultUnits == 'in' or defaultUnits == 'ft':
        _units = 'in'
    else:
        _units = 'mm'

# Event handler for the commandCreated event.


def AssignEvents(cmd):
    onExecute = GearCommandExecuteHandler()
    cmd.execute.add(onExecute)
    _handlers.append(onExecute)

    onInputChanged = GearCommandInputChangedHandler()
    cmd.inputChanged.add(onInputChanged)
    _handlers.append(onInputChanged)

    onValidateInputs = GearCommandValidateInputsHandler()
    cmd.validateInputs.add(onValidateInputs)
    _handlers.append(onValidateInputs)

    onDestroy = GearCommandDestroyHandler()
    cmd.destroy.add(onDestroy)
    _handlers.append(onDestroy)


class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        """notify command information

        system call this method just after executing this script
        """
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox(
                    'A Fusion design must be active when invoking this command.')
                return()

            defaultUnits = des.unitsManager.defaultLengthUnits

            # Determine whether to use inches or millimeters as the initial default.
            global _units
            # if defaultUnits == 'in' or defaultUnits == 'ft':
            #     _units = 'in'
            # else:
            _units = 'mm'

            # Define the default values and get the previous values from the attributes.
            # if _units == 'in':
            #     standard = 'English'
            # else:
            standard = 'Metric'
            standardAttrib = des.attributes.itemByName(_app_name, 'standard')
            if standardAttrib:
                standard = standardAttrib.value

            # if standard == 'English':
            #     _units = 'in'
            # else:
            _units = 'mm'

            pressureAngle = '20 deg'  # initial value
            pressureAngleAttrib = des.attributes.itemByName(
                _app_name, 'pressureAngle')
            if pressureAngleAttrib:
                pressureAngle = pressureAngleAttrib.value

            pressureAngleCustom = 20 * (math.pi/180.0)
            pressureAngleCustomAttrib = des.attributes.itemByName(
                _app_name, 'pressureAngleCustom')
            if pressureAngleCustomAttrib:
                pressureAngleCustom = float(pressureAngleCustomAttrib.value)

            metricModule = '1'
            moduleAttrib = des.attributes.itemByName(_app_name, 'module')
            if moduleAttrib:
                metricModule = moduleAttrib.value

            backlash = '0'
            backlashAttrib = des.attributes.itemByName(_app_name, 'backlash')
            if backlashAttrib:
                backlash = backlashAttrib.value

            rootFilletRad = str(0)
            rootFilletRadAttrib = des.attributes.itemByName(
                _app_name, 'rootFilletRad')
            if rootFilletRadAttrib:
                rootFilletRad = rootFilletRadAttrib.value

            thickness = str(0.5 * 4)
            thicknessAttrib = des.attributes.itemByName(
                _app_name, 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value

            holeDiam = str(0.4)
            holeDiamAttrib = des.attributes.itemByName(_app_name, 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            num_teeth_sh = '40'
            num_teeth_sh_attr = des.attributes.itemByName(
                _app_name, 'num_teeth_sh')
            if num_teeth_sh_attr:
                num_teeth_sh = num_teeth_sh_attr.value

            gear_ratio = '2'
            gear_ratio_attr = des.attributes.itemByName(
                _app_name, 'gear_ratio')
            if gear_ratio_attr:
                gear_ratio = gear_ratio_attr.value

            num_rotation_steps = '36'
            num_rotation_steps_attr = des.attributes.itemByName(
                _app_name, 'num_rotation_steps')
            if num_rotation_steps_attr:
                num_rotation_steps = num_rotation_steps_attr.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _standard, _pressureAngle, _pressureAngleCustom, _diaPitch, _module, _rootFilletRad, _thickness, _holeDiam, _backlash, _imgInputMetric, _errMessage
            global _num_teeth_sh, _gear_ratio, _num_rotation_steps
            # Define the command dialog.
            defineCommandDialog(inputs, standard, pressureAngle)

            _pressureAngleCustom = inputs.addValueInput(
                'pressureAngleCustom', 'Custom Angle', 'deg', adsk.core.ValueInput.createByReal(pressureAngleCustom))
            if pressureAngle != 'Custom':
                _pressureAngleCustom.isVisible = False

            _module = inputs.addValueInput(
                'module', 'Module', '', adsk.core.ValueInput.createByReal(float(metricModule)))

            # if standard == 'English':
            #     _module.isVisible = False
            # elif standard == 'Metric':
            #     _diaPitch.isVisible = False

            _backlash = inputs.addValueInput(
                'backlash', 'Backlash', _units, adsk.core.ValueInput.createByReal(float(backlash)))

            _rootFilletRad = inputs.addValueInput(
                'rootFilletRad', 'Root Fillet Radius', _units, adsk.core.ValueInput.createByReal(float(rootFilletRad)))
            # hide rootfillet to avoid confusion
            # todo: activate root fillet
            _rootFilletRad.isVisible = False

            _thickness = inputs.addValueInput(
                'thickness', 'Gear Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _holeDiam = inputs.addValueInput(
                'holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _num_teeth_sh = inputs.addStringValueInput(
                'num_teeth_sh', 'Num Teeth of SH-Gear', num_teeth_sh)

            _gear_ratio = inputs.addValueInput(
                'gear_ratio', 'Gear Ratio', '', adsk.core.ValueInput.createByReal(float(gear_ratio)))

            _num_rotation_steps = inputs.addStringValueInput(
                'num_rotation_steps', 'Num Rotation Steps to Engrave', num_rotation_steps)

            # dependant variables
            global _pitch_diameter_sh, _pitch_diameter_mp
            _pitch_diameter_sh = inputs.addTextBoxCommandInput(
                'pitch_diameter_sh', 'SP-Gear Diameter', '', 1, True)
            _pitch_diameter_mp = inputs.addTextBoxCommandInput(
                'pitch_diameter_mp', 'MP-Gear Diameter', '', 1, True)

            _errMessage = inputs.addTextBoxCommandInput(
                'errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            AssignEvents(cmd)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def SaveValueAsAttributes(attribs):
    """
    Args:
        attribs : attributes, adsk.fusion.Design.cast(_app.activeProduct).attributes
    """
    # if _standard.selectedItem.name == 'English':
    #     diaPitch = _module.value*2.54
    # elif _standard.selectedItem.name == 'Metric':
    #     diaPitch = 25.4 / _module.value

    attribs.add(_app_name, 'standard', _standard.selectedItem.name)
    attribs.add(_app_name, 'pressureAngle',
                _pressureAngle.selectedItem.name)
    attribs.add(_app_name, 'pressureAngleCustom',
                str(_pressureAngleCustom.value))
    attribs.add(_app_name, 'module', str(_module.value))
    attribs.add(_app_name, 'rootFilletRad', str(_rootFilletRad.value))
    attribs.add(_app_name, 'backlash', str(_backlash.value))
    attribs.add(_app_name, 'gear_ratio', str(_gear_ratio.value))

    # SH Gear
    attribs.add(_app_name, 'num_teeth_sh', str(_num_teeth_sh.value))

    # MP Gear
    attribs.add(_app_name, 'thickness', str(_thickness.value))
    attribs.add(_app_name, 'holeDiam', str(_holeDiam.value))

    attribs.add(_app_name, 'num_rotation_steps',
                str(_num_rotation_steps.value))
# Event handler for the execute event.


class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        """
        system executes this method when you press the [run] button
        """
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # if _standard.selectedItem.name == 'English':
            #     diaPitch = _diaPitch.value*25.4
            # elif _standard.selectedItem.name == 'Metric':
            #     diaPitch = _module.value

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            SaveValueAsAttributes(attribs)

            # Get the current values.
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)

            rootFilletRad = _rootFilletRad.value
            num_teeth = int(_num_teeth_sh.value)
            num_rotation_steps = int(_num_rotation_steps.value)

            # Create the gear.
            # gearComp = drawGear(des, diaPitch, numTeeth, thickness,
            #                     rootFilletRad, pressureAngle, backlash, holeDiam)

            abenics = ABENICS(design=des,
                              module=_module.value,
                              pressure_angle=pressureAngle,
                              num_teeth_sh=num_teeth,
                              gear_ratio=_gear_ratio.value,
                              thickness=_thickness.value,
                              hole_diameter=_holeDiam.value,
                              backlash=_backlash.value)
            abenics.print()

            abenics.make_sh_comp()
            # Create a new sketch.
            sketches = abenics.sh_comp.sketches
            xyPlane = abenics.sh_comp.xYConstructionPlane

            # SH Gear 1
            baseSketch = sketches.add(xyPlane)
            sk, ax_line = abenics.draw_gear(baseSketch)
            abenics.revolve_ballgear(sk, ax_line)

            # MP Gear
            abenics.make_mp_comp()
            sketches = abenics.mp_comp.sketches
            xyPlane = abenics.mp_comp.xYConstructionPlane
            mp_sketch = sketches.add(xyPlane)
            abenics.draw_mp_sketch(mp_sketch)
            abenics.extrude_mp(mp_sketch, abenics.thickness_mp)

            # Engrave MP-Gear and rotate both gears
            delta_angle = (2*math.pi) / num_rotation_steps
            for i in range(num_rotation_steps):
                timelineGroups = des.timeline.timelineGroups
                e = abenics.engrave()
                sh, mp = abenics.rotate_gears(delta_angle)
                timelineGroup = timelineGroups.add(
                    e.timelineObject.index, mp.timelineObject.index)
                if i == 0:
                    first_group = timelineGroup

            last_group = timelineGroup

            # this will be fail
            try:
                timelineGroups = des.timeline.timelineGroups
                timelineGroup = timelineGroups.add(
                    first_group.index,
                    last_group.index)
            except:
                pass

            # SH Gear 2
            # reset rotation
            sh_angle = -2*math.pi/(abenics.gear_ratio+1.0e-9)
            moves = abenics.sh_comp.features.moveFeatures
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(abenics.sh_comp.bRepBodies.item(0))
            tf = adsk.core.Matrix3D.create()
            tf.setToRotation(
                angle=sh_angle,
                axis=adsk.core.Vector3D.create(0, 0, 1),
                origin=adsk.core.Point3D.create(0, 0, 0)
            )
            move_input = moves.createInput(bodies, tf)
            move_sh = moves.add(move_input)
            # intersect gear
            sketches = abenics.sh_comp.sketches
            xyPlane = abenics.sh_comp.xYConstructionPlane
            i_sketch = sketches.add(xyPlane)
            sk, ax_line = abenics.draw_gear(i_sketch, axis_angle=0.5*math.pi)
            # bodies = adsk.core.ObjectCollection.create()
            # bodies.add(abenics.sh_comp.bRepBodies.item(0))
            rev_feature = abenics.revolve_ballgear(
                sk, ax_line,
                operation=adsk.fusion.FeatureOperations.IntersectFeatureOperation,
                bodies=[abenics.sh_comp.bRepBodies.item(0)])

            abenics.sh_comp.name = 'SH_Gear'
            abenics.mp_comp.name = 'MP_Gear'
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the inputChanged event.
class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        """
        system call this method when values in input-boxes change.
        """
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            global _units
            if changedInput.id == 'standard':
                pass

            des = adsk.fusion.Design.cast(_app.activeProduct)

            d_sh = _module.value*int(_num_teeth_sh.value)
            d_mp = d_sh/(_gear_ratio.value+1.0e-9)
            d_mp = round(d_mp, 2)
            _pitch_diameter_sh.text = '{:0.2f} mm'.format(d_sh)
            _pitch_diameter_mp.text = '{:0.2f} mm'.format(d_mp)
            # _pitch_diameter_sh.text = des.unitsManager.formatInternalValue(
            #     0.1*d_sh, _units, True)
            # _pitch_diameter_mp.text = des.unitsManager.formatInternalValue(
            #     0.1*d_mp, _units, True)

            if changedInput.id == 'pressureAngle':
                if _pressureAngle.selectedItem.name == 'Custom':
                    _pressureAngleCustom.isVisible = True
                else:
                    _pressureAngleCustom.isVisible = False
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            """system may call this after InputChangedEvent
            """
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)

            _errMessage.text = ''

            # Verify that at least 4 teeth are specified.
            if not _num_teeth_sh.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:
                numTeeth = int(_num_teeth_sh.value)

            if numTeeth < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
                eventArgs.areInputsValid = False
                return

            # _pitch_diameter_mp.text : "400 mm"
            pd = _pitch_diameter_mp.text.split(' ')
            pitch_diameter = float(pd[0])
            dedendum = 1.25 * _module.value
            dedendum *= 0.1  # mm->cm

            rootDia = pitch_diameter - (2 * dedendum)

            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)
            baseCircleDia = pitch_diameter * math.cos(pressureAngle)
            baseCircleCircumference = 2 * math.pi * (baseCircleDia / 2)

            des = adsk.fusion.Design.cast(_app.activeProduct)

            result = getCommandInputValue(_holeDiam, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                holeDiam = result[1]

            if holeDiam >= (rootDia - 0.01):
                _errMessage.text = 'The center hole diameter is too large.  It must be less than ' + \
                    des.unitsManager.formatInternalValue(
                        rootDia - 0.01, _units, True)
                eventArgs.areInputsValid = False
                return

            toothThickness = baseCircleCircumference / (numTeeth * 2)
            if _rootFilletRad.value > toothThickness * .4:
                _errMessage.text = 'The root fillet radius is too large.  It must be less than ' + \
                    des.unitsManager.formatInternalValue(
                        toothThickness * .4, _units, True)
                eventArgs.areInputsValid = False
                return
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def _isArrayLike(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__len__')


def get_involutePoints(bd, od, num=15):
    # Calculate points along the involute curve.
    """
        Args:
            bd (float) : base circle diameter
            od (float) : outside circle diameter
        """
    # involuteIntersectionRadius
    # r = 0.5 * bd
    points = []
    involute_size = 0.5 * (od - bd)  # height
    for i in range(0, num):
        r = (0.5*bd) + ((involute_size / (num - 1)) * i)
        p = involutePoint(0.5 * bd, r)
        points.append(p)
    return points


def xy2polar(points):
    """
    convert position in xy-coordinate sys. to r-theta one

    Args:
        points (list) : list of adsk.core.Point3D
    Returns:
        list: distances from origin
        list: angles from x-axis
    """
    distances = []
    angles = []
    count = len(points)
    for i in range(0, count):
        distances.append(math.sqrt(
            points[i].x * points[i].x + points[i].y * points[i].y))
        angles.append(
            math.atan2(points[i].y, points[i].x))

    return distances, angles


def rotate_points(points, angle, center=None):

    cos_val = math.cos(angle)
    sin_val = math.sin(angle)

    rotated_points = list()

    if not _isArrayLike(points):
        points = [points]

    for i in range(len(points)):
        p = adsk.core.Point3D.create(0, 0, 0)
        p.x = points[i].x
        p.y = points[i].y
        if center is not None:
            p.x -= center.x
            p.y -= center.y
        x = p.x*cos_val - p.y*sin_val
        y = p.x*sin_val + p.y*cos_val
        if center is not None:
            x += center.x
            y += center.y
        p.x = x
        p.y = y
        rotated_points.append(p)

    if len(rotated_points) == 1:
        return rotated_points[0]

    return rotated_points


def involutePoint(baseCircleRadius, distFromCenterToInvolutePoint):
    try:
        # Calculate the other side of the right-angle triangle defined by the base circle and the current distance radius.
        # This is also the length of the involute chord as it comes off of the base circle.
        triangleSide = math.sqrt(
            math.pow(distFromCenterToInvolutePoint, 2) - math.pow(baseCircleRadius, 2))

        # Calculate the angle of the involute.
        alpha = triangleSide / baseCircleRadius

        # Calculate the angle where the current involute point is.
        theta = alpha - math.acos(baseCircleRadius /
                                  distFromCenterToInvolutePoint)

        # Calculate the coordinates of the involute point.
        x = distFromCenterToInvolutePoint * math.cos(theta)
        y = distFromCenterToInvolutePoint * math.sin(theta)

        # Create a point to return.
        return adsk.core.Point3D.create(x, y, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Builds a spur gear.
def drawGear(design, diametralPitch, numTeeth, thickness, rootFilletRad, pressureAngle, backlash, holeDiam):
    try:
        # The diametral pitch is specified in inches but everthing
        # here expects all distances to be in centimeters, so convert
        # for the gear creation.
        diametralPitch = diametralPitch / 2.54

        # Compute the various values for a gear.
        pitchDia = numTeeth / diametralPitch

        # addendum = 1.0 / diametralPitch
        if (diametralPitch < (20 * (math.pi/180))-0.000001):
            dedendum = 1.157 / diametralPitch
        else:
            circularPitch = math.pi / diametralPitch
            if circularPitch >= 20:
                dedendum = 1.25 / diametralPitch
            else:
                dedendum = (1.2 / diametralPitch) + (.002 * 2.54)

        rootDia = pitchDia - (2 * dedendum)

        baseCircleDia = pitchDia * math.cos(pressureAngle)
        outsideDia = (numTeeth + 2) / diametralPitch

        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)
        newComp = adsk.fusion.Component.cast(newOcc.component)

        # Create a new sketch.
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        baseSketch = sketches.add(xyPlane)

        # Draw a circle for the base.
        baseSketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), rootDia/2.0)

        # Draw a circle for the center hole, if the value is greater than 0.
        prof = adsk.fusion.Profile.cast(None)
        if holeDiam - (_app.pointTolerance * 2) > 0:
            baseSketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(0, 0, 0), holeDiam/2.0)

            # Find the profile that uses both circles.
            for prof in baseSketch.profiles:
                if prof.profileLoops.count == 2:
                    break
        else:
            # Use the single profile.
            prof = baseSketch.profiles.item(0)

        # Extrude the circle to create the base of the gear.

        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(thickness)
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion.
        baseExtrude = extrudes.add(extInput)

        # Create a second sketch for the tooth.
        toothSketch = sketches.add(xyPlane)

        # Calculate points along the involute curve.
        involutePointCount = 15
        involuteIntersectionRadius = baseCircleDia / 2.0
        involutePoints = []
        involuteSize = (outsideDia - baseCircleDia) / 2.0
        for i in range(0, involutePointCount):
            involuteIntersectionRadius = (
                baseCircleDia / 2.0) + ((involuteSize / (involutePointCount - 1)) * i)
            newPoint = involutePoint(
                baseCircleDia / 2.0, involuteIntersectionRadius)
            involutePoints.append(newPoint)

        # Get the point along the tooth that's at the pictch diameter and then
        # calculate the angle to that point.
        pitchInvolutePoint = involutePoint(baseCircleDia / 2.0, pitchDia / 2.0)
        pitchPointAngle = math.atan(
            pitchInvolutePoint.y / pitchInvolutePoint.x)

        # Determine the angle defined by the tooth thickness as measured at
        # the pitch diameter circle.
        toothThicknessAngle = (2 * math.pi) / (2 * numTeeth)

        # Determine the angle needed for the specified backlash.
        backlashAngle = (backlash / (pitchDia / 2.0)) * .25

        # Determine the angle to rotate the curve.
        rotateAngle = -((toothThicknessAngle/2) +
                        pitchPointAngle - backlashAngle)

        # Rotate the involute so the middle of the tooth lies on the x axis.
        cosAngle = math.cos(rotateAngle)
        sinAngle = math.sin(rotateAngle)
        for i in range(0, involutePointCount):
            newX = involutePoints[i].x * cosAngle - \
                involutePoints[i].y * sinAngle
            newY = involutePoints[i].x * sinAngle + \
                involutePoints[i].y * cosAngle
            involutePoints[i] = adsk.core.Point3D.create(newX, newY, 0)

        # Create a new set of points with a negated y.  This effectively mirrors the original
        # points about the X axis.
        involute2Points = []
        for i in range(0, involutePointCount):
            involute2Points.append(adsk.core.Point3D.create(
                involutePoints[i].x, -involutePoints[i].y, 0))

        curve1Dist = []
        curve1Angle = []
        for i in range(0, involutePointCount):
            curve1Dist.append(math.sqrt(
                involutePoints[i].x * involutePoints[i].x + involutePoints[i].y * involutePoints[i].y))
            curve1Angle.append(
                math.atan(involutePoints[i].y / involutePoints[i].x))

        curve2Dist = []
        curve2Angle = []
        for i in range(0, involutePointCount):
            curve2Dist.append(math.sqrt(
                involute2Points[i].x * involute2Points[i].x + involute2Points[i].y * involute2Points[i].y))
            curve2Angle.append(
                math.atan(involute2Points[i].y / involute2Points[i].x))

        toothSketch.isComputeDeferred = True

        # Create and load an object collection with the points.
        pointSet = adsk.core.ObjectCollection.create()
        for i in range(0, involutePointCount):
            pointSet.add(involutePoints[i])

        # Create the first spline.
        spline1 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

        # Add the involute points for the second spline to an ObjectCollection.
        pointSet = adsk.core.ObjectCollection.create()
        for i in range(0, involutePointCount):
            pointSet.add(involute2Points[i])

        # Create the second spline.
        spline2 = toothSketch.sketchCurves.sketchFittedSplines.add(pointSet)

        # Draw the arc for the top of the tooth.
        midPoint = adsk.core.Point3D.create((outsideDia / 2), 0, 0)
        toothSketch.sketchCurves.sketchArcs.addByThreePoints(
            spline1.endSketchPoint, midPoint, spline2.endSketchPoint)

        # Check to see if involute goes down to the root or not.  If not, then
        # create lines to connect the involute to the root.
        if(baseCircleDia < rootDia):
            toothSketch.sketchCurves.sketchLines.addByTwoPoints(
                spline2.startSketchPoint, spline1.startSketchPoint)
        else:
            rootPoint1 = adsk.core.Point3D.create(
                (rootDia / 2 - 0.001) * math.cos(curve1Angle[0]), (rootDia / 2) * math.sin(curve1Angle[0]), 0)
            line1 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(
                rootPoint1, spline1.startSketchPoint)

            rootPoint2 = adsk.core.Point3D.create(
                (rootDia / 2 - 0.001) * math.cos(curve2Angle[0]), (rootDia / 2) * math.sin(curve2Angle[0]), 0)
            line2 = toothSketch.sketchCurves.sketchLines.addByTwoPoints(
                rootPoint2, spline2.startSketchPoint)

            baseLine = toothSketch.sketchCurves.sketchLines.addByTwoPoints(
                line1.startSketchPoint, line2.startSketchPoint)

            # Make the lines tangent to the spline so the root fillet will behave correctly.
            line1.isFixed = True
            line2.isFixed = True
            toothSketch.geometricConstraints.addTangent(spline1, line1)
            toothSketch.geometricConstraints.addTangent(spline2, line2)

        toothSketch.isComputeDeferred = False

        # Extrude the tooth.

        # Get the profile defined by the tooth.
        prof = toothSketch.profiles.item(0)

        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.JoinFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(thickness)
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion.
        toothExtrude = extrudes.add(extInput)

        baseFillet = None
        if rootFilletRad > 0:
            # Find the edges between the base cylinder and the tooth.

            # Get the outer cylindrical face from the base extrusion by checking the number
            # of edges and if it's 2 get the other one.
            cylFace = baseExtrude.sideFaces.item(0)
            if cylFace.edges.count == 2:
                cylFace = baseExtrude.sideFaces.item(1)

            # Get the two linear edges, which are the connection between the cylinder and tooth.
            edges = adsk.core.ObjectCollection.create()
            for edge in cylFace.edges:
                if isinstance(edge.geometry, adsk.core.Line3D):
                    edges.add(edge)

            # Create a fillet input to be able to define the input needed for a fillet.
            fillets = newComp.features.filletFeatures
            filletInput = fillets.createInput()

            # Define that the extent is a distance extent of 5 cm.
            radius = adsk.core.ValueInput.createByReal(rootFilletRad)
            filletInput.addConstantRadiusEdgeSet(edges, radius, False)

            # Create the extrusion.
            baseFillet = fillets.add(filletInput)

        # Create a pattern of the tooth extrude and the base fillet.
        circularPatterns = newComp.features.circularPatternFeatures
        entities = adsk.core.ObjectCollection.create()
        entities.add(toothExtrude)
        if baseFillet:
            entities.add(baseFillet)
        cylFace = baseExtrude.sideFaces.item(0)
        patternInput = circularPatterns.createInput(entities, cylFace)
        numTeethInput = adsk.core.ValueInput.createByString(str(numTeeth))
        patternInput.quantity = numTeethInput
        patternInput.patternComputeOption = adsk.fusion.PatternComputeOptions.IdenticalPatternCompute
        pattern = circularPatterns.add(patternInput)

        # Create an extra sketch that contains a circle of the diametral pitch.
        diametralPitchSketch = sketches.add(xyPlane)
        diametralPitchCircle = diametralPitchSketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), pitchDia/2.0)
        diametralPitchCircle.isConstruction = True
        diametralPitchCircle.isFixed = True

        # Group everything used to create the gear in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        pitchSketchIndex = diametralPitchSketch.timelineObject.index
        # ui.messageBox("Indices: " + str(newOccIndex) + ", " + str(pitchSketchIndex))
        timelineGroup = timelineGroups.add(newOccIndex, pitchSketchIndex)
        timelineGroup.name = 'Spur Gear'

        # Add an attribute to the component with all of the input values.  This might
        # be used in the future to be able to edit the gear.
        gearValues = {}
        gearValues['diametralPitch'] = str(diametralPitch * 2.54)
        gearValues['numTeeth'] = str(numTeeth)
        gearValues['thickness'] = str(thickness)
        gearValues['rootFilletRad'] = str(rootFilletRad)
        gearValues['pressureAngle'] = str(pressureAngle)
        gearValues['holeDiam'] = str(holeDiam)
        gearValues['backlash'] = str(backlash)
        attrib = newComp.attributes.add(_app_name, 'Values', str(gearValues))

        newComp.name = 'Spur Gear (' + str(numTeeth) + ' teeth)'
        return newComp
    except Exception as error:
        _ui.messageBox("drawGear Failed : " + str(error))
        return None
