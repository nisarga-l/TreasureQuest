# Fusion 360 Python script
# Parametric recreation of the sailboat shown in the reference image.
# Run from Fusion 360: Utilities -> Add-Ins -> Scripts and Add-Ins -> Scripts -> +
#
# The model is built in millimetres. Change the parameters in the first section
# if you want to scale the boat while keeping the same proportions.

import adsk.core
import adsk.fusion
import traceback

# ---------------- PARAMETERS ----------------
HULL_LENGTH = 280.0
HULL_WIDTH = 92.0
HULL_HEIGHT = 48.0

DECK_LENGTH = 265.0
DECK_WIDTH = 82.0
DECK_THICKNESS = 5.0

MAST_HEIGHT = 205.0
MAST_RADIUS = 3.5
MAST_X = -5.0

# Sail positions and thickness
SAIL_THICKNESS = 1.5
LEFT_SAIL_TOP_X = -12.0
LEFT_SAIL_BOTTOM_X = -128.0
LEFT_SAIL_TOP_Z = 195.0
LEFT_SAIL_BOTTOM_Z = 52.0

RIGHT_SAIL_TOP_X = -2.0
RIGHT_SAIL_BOTTOM_X = 128.0
RIGHT_SAIL_TOP_Z = 195.0
RIGHT_SAIL_BOTTOM_Z = 52.0

KEEL_LENGTH = 105.0
KEEL_WIDTH = 7.0
KEEL_DEPTH = 22.0

SUPPORT_HEIGHT = 42.0
SUPPORT_RADIUS = 4.0

# ---------------- HELPERS ----------------
def mm(v):
    return v

def p3(x, y, z):
    return adsk.core.Point3D.create(mm(x), mm(y), mm(z))

def add_polygon_sketch(root, name, points):
    sketches = root.sketches
    sketch = sketches.add(root.xYConstructionPlane)
    sketch.name = name

    lines = sketch.sketchCurves.sketchLines
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]
        lines.addByTwoPoints(p3(a[0], a[1], a[2]), p3(b[0], b[1], b[2]))
    return sketch

def profile_from_sketch(sketch):
    # Return the first closed profile in the sketch.
    if sketch.profiles.count == 0:
        raise RuntimeError("No closed profile was created in sketch: " + sketch.name)
    return sketch.profiles.item(0)

def extrude_profile(root, profile, distance, operation, name):
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(profile, operation)
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(distance))
    feat = extrudes.add(inp)
    feat.name = name
    return feat

def add_cylinder(root, x, y, z, radius, height, name):
    # Cylinder sketch on XY plane, then extrude.
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = name + "_Sketch"
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        p3(x, y, z), radius
    )
    prof = profile_from_sketch(sketch)
    return extrude_profile(
        root, prof, height,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        name
    )

def create_vertical_triangle_sail(root, name, a, b, c, thickness):
    # Create a sail in the XZ plane.
    # We create the triangle as a planar sketch on the XZ plane and extrude
    # symmetrically in Y.
    plane = root.xZConstructionPlane
    sketch = root.sketches.add(plane)
    sketch.name = name + "_Sketch"

    lines = sketch.sketchCurves.sketchLines

    # On XZ plane, sketch coordinates are represented by Point3D(x,0,z).
    pts = [p3(a[0], 0, a[1]), p3(b[0], 0, b[1]), p3(c[0], 0, c[1])]
    for i in range(3):
        lines.addByTwoPoints(pts[i], pts[(i + 1) % 3])

    prof = profile_from_sketch(sketch)
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    inp.setSymmetricExtent(
        adsk.core.ValueInput.createByReal(thickness), True
    )
    feat = extrudes.add(inp)
    feat.name = name
    return feat

def create_vertical_quad_sail(root, name, points, thickness):
    plane = root.xZConstructionPlane
    sketch = root.sketches.add(plane)
    sketch.name = name + "_Sketch"
    lines = sketch.sketchCurves.sketchLines

    pts = [p3(x, 0, z) for x, z in points]
    for i in range(len(pts)):
        lines.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])

    prof = profile_from_sketch(sketch)
    extrudes = root.features.extrudeFeatures
    inp = extrudes.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    inp.setSymmetricExtent(
        adsk.core.ValueInput.createByReal(thickness), True
    )
    feat = extrudes.add(inp)
    feat.name = name
    return feat

# ---------------- MAIN ----------------
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # New design
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent
        root.name = "Reference_Sailboat"

        # ---------- HULL ----------
        # Three closed polygon profiles at different heights.
        # This gives the hull a tapered, boat-like body.
        hull_profiles = []

        z_levels = [0.0, 22.0, HULL_HEIGHT]
        length_factors = [0.72, 0.94, 1.0]
        width_factors = [0.55, 0.88, 1.0]

        for i, z in enumerate(z_levels):
            L = HULL_LENGTH * length_factors[i]
            W = HULL_WIDTH * width_factors[i]

            # pointed bow at +X and slightly pointed stern at -X
            pts = [
                (-L/2, -W/2, z),
                (-L/2 + 28, -W/2, z),
                (L/2 - 30, -W/2, z),
                (L/2, 0, z),
                (L/2 - 30, W/2, z),
                (-L/2 + 28, W/2, z),
                (-L/2, W/2, z)
            ]

            sk = root.sketches.add(root.xYConstructionPlane)
            sk.name = "Hull_Profile_%d" % i
            # Move sketch plane to the required Z using a construction plane
            # is more complicated; instead create each profile on XY and move
            # its profile sketch.
            sk.moveToComponent(
                adsk.core.Matrix3D.create()
            )

            # Recreate the profile using sketch lines at z=0 and then move
            # the sketch entity along Z.
            lines = sk.sketchCurves.sketchLines
            for j in range(len(pts)):
                a = pts[j]
                b = pts[(j+1) % len(pts)]
                lines.addByTwoPoints(
                    adsk.core.Point3D.create(a[0], a[1], 0),
                    adsk.core.Point3D.create(b[0], b[1], 0)
                )

            # Move the sketch to its Z level.
            mat = adsk.core.Matrix3D.create()
            mat.translation = adsk.core.Vector3D.create(0, 0, z)
            sk.transform = mat
            hull_profiles.append(sk)

        # Loft hull
        lofts = root.features.loftFeatures
        loft_input = lofts.createInput(
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        loft_input.isSolid = True
        for sk in hull_profiles:
            loft_input.loftSections.add(profile_from_sketch(sk))
        hull = lofts.add(loft_input)
        hull.name = "Main_Hull"

        # ---------- DECK ----------
        deck_pts = [
            (-DECK_LENGTH/2, -DECK_WIDTH/2),
            (DECK_LENGTH/2 - 28, -DECK_WIDTH/2),
            (DECK_LENGTH/2, 0),
            (DECK_LENGTH/2 - 28, DECK_WIDTH/2),
            (-DECK_LENGTH/2, DECK_WIDTH/2)
        ]
        deck_sk = root.sketches.add(root.xYConstructionPlane)
        deck_sk.name = "Deck_Sketch"
        dlines = deck_sk.sketchCurves.sketchLines
        for i in range(len(deck_pts)):
            a = deck_pts[i]
            b = deck_pts[(i+1) % len(deck_pts)]
            dlines.addByTwoPoints(
                p3(a[0], a[1], HULL_HEIGHT),
                p3(b[0], b[1], HULL_HEIGHT)
            )

        deck = extrude_profile(
            root, profile_from_sketch(deck_sk), DECK_THICKNESS,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            "Deck"
        )

        # ---------- MAST ----------
        mast_sk = root.sketches.add(root.xYConstructionPlane)
        mast_sk.name = "Mast_Sketch"
        mast_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p3(MAST_X, 0, HULL_HEIGHT + DECK_THICKNESS),
            MAST_RADIUS
        )
        mast = extrude_profile(
            root, profile_from_sketch(mast_sk), MAST_HEIGHT,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            "Mast"
        )

        # ---------- KEEL / CENTER FIN ----------
        keel_sk = root.sketches.add(root.xZConstructionPlane)
        keel_sk.name = "Keel_Sketch"
        klines = keel_sk.sketchCurves.sketchLines
        keel_points = [
            (-KEEL_LENGTH/2, HULL_HEIGHT),
            (KEEL_LENGTH/2, HULL_HEIGHT),
            (KEEL_LENGTH/2 - 20, -KEEL_DEPTH),
            (-KEEL_LENGTH/2 + 20, -KEEL_DEPTH)
        ]
        for i in range(len(keel_points)):
            a = keel_points[i]
            b = keel_points[(i+1) % len(keel_points)]
            klines.addByTwoPoints(
                p3(a[0], 0, a[1]),
                p3(b[0], 0, b[1])
            )

        keel_prof = profile_from_sketch(keel_sk)
        keel_ext = root.features.extrudeFeatures.createInput(
            keel_prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        keel_ext.setSymmetricExtent(
            adsk.core.ValueInput.createByReal(KEEL_WIDTH), True
        )
        keel = root.features.extrudeFeatures.add(keel_ext)
        keel.name = "Center_Keel"

        # ---------- TWO UNDER-HULL SUPPORTS ----------
        # These reproduce the two visible dark supports/legs in the reference.
        for idx, x in enumerate([-72.0, 72.0]):
            sk = root.sketches.add(root.xYConstructionPlane)
            sk.name = "Support_%d_Sketch" % (idx+1)
            sk.sketchCurves.sketchCircles.addByCenterRadius(
                p3(x, 0, -SUPPORT_HEIGHT), SUPPORT_RADIUS
            )
            # The sketch is at XY=0; use the profile and extrude upward/downward.
            prof = profile_from_sketch(sk)
            ext = root.features.extrudeFeatures.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            ext.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(SUPPORT_HEIGHT)
            )
            support = root.features.extrudeFeatures.add(ext)
            support.name = "Under_Hull_Support_%d" % (idx+1)

        # ---------- SAILS ----------
        # Large left sail: four-sided curved-looking silhouette.
        left_sail = create_vertical_quad_sail(
            root, "Large_Left_Sail",
            [
                (MAST_X, HULL_HEIGHT + DECK_THICKNESS),
                (LEFT_SAIL_BOTTOM_X, LEFT_SAIL_BOTTOM_Z),
                (LEFT_SAIL_BOTTOM_X + 18, LEFT_SAIL_TOP_Z - 25),
                (LEFT_SAIL_TOP_X, LEFT_SAIL_TOP_Z)
            ],
            SAIL_THICKNESS
        )

        # Right sail: triangular sail.
        right_sail = create_vertical_triangle_sail(
            root, "Right_Sail",
            (RIGHT_SAIL_TOP_X, RIGHT_SAIL_TOP_Z),
            (RIGHT_SAIL_BOTTOM_X, RIGHT_SAIL_BOTTOM_Z),
            (MAST_X, HULL_HEIGHT + DECK_THICKNESS),
            SAIL_THICKNESS
        )

        # ---------- SIMPLE BOOM ----------
        # Horizontal boom crossing the lower part of both sails.
        boom_sk = root.sketches.add(root.xZConstructionPlane)
        boom_sk.name = "Boom_Sketch"
        boom_sk.sketchCurves.sketchCircles.addByCenterRadius(
            p3(MAST_X, 0, 72.0), 2.5
        )
        boom_prof = profile_from_sketch(boom_sk)
        boom_ext = root.features.extrudeFeatures.createInput(
            boom_prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        boom_ext.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(110.0)
        )
        boom = root.features.extrudeFeatures.add(boom_ext)
        boom.name = "Boom"

        # ---------- APPEARANCES ----------
        # Try to assign simple contrasting appearances.
        def set_appearance(entity, appearance_name):
            try:
                lib = app.materials
                # Appearance library is more reliable through the active library.
                for i in range(lib.count):
                    item = lib.item(i)
                    if appearance_name.lower() in item.name.lower():
                        entity.appearance = item
                        return
            except:
                pass

        set_appearance(hull, "Aluminum")
        set_appearance(deck, "Aluminum")
        set_appearance(mast, "Black")
        set_appearance(keel, "Black")
        set_appearance(left_sail, "White")
        set_appearance(right_sail, "White")

        ui.messageBox(
            "Sailboat created successfully.\\n\\n"
            "Main bodies: hull, deck, mast, keel, two sails, boom and supports.\\n"
            "All dimensions are editable at the top of this script."
        )

    except:
        if ui:
            ui.messageBox("ERROR:\\n" + traceback.format_exc())

def stop(context):
    try:
        adsk.terminate()
    except:
        pass
