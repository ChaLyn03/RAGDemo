# NXOpen Python (simulated export)
# Part: WidgetHousing_v1

import NXOpen
import NXOpen.Features

def main():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work

    # Units: (common enum usage)
    part_units = NXOpen.Part.Units.Millimeters

    # --- Block / Extrude-ish feature (builder signature presence) ---
    blockBuilder = workPart.Features.CreateBlockFeatureBuilder(None)
    blockBuilder.Type = NXOpen.Features.BlockFeatureBuilder.Types.OriginAndEdgeLengths
    blockBuilder.SetOriginAndLengths(
        NXOpen.Point3d(0.0, 0.0, 0.0),
        "120.0", "80.0", "35.0"  # length/width/height expressions
    )
    blockFeature = blockBuilder.CommitFeature()
    blockBuilder.Destroy()

    # --- Hole feature ---
    holeBuilder = workPart.Features.CreateHoleBuilder(None)
    holeBuilder.Diameter.RightHandSide = "6.0"
    holeBuilder.Depth.RightHandSide = "12.0"
    holeFeature = holeBuilder.CommitFeature()
    holeBuilder.Destroy()

    # --- Fillet (edge blend) ---
    edgeBlendBuilder = workPart.Features.CreateEdgeBlendBuilder(None)
    edgeBlendBuilder.Radius.RightHandSide = "1.5"
    edgeBlendFeature = edgeBlendBuilder.CommitFeature()
    edgeBlendBuilder.Destroy()

    # Material mention (often in comments/strings or library calls)
    mat_note = "Material: 6061-T6 aluminum"
    # Tolerance mention (comment/string)
    tol_note = "Mounting interface tolerance: ±0.05 mm"
    torque_note = "Torque M5 screws to 4.5 N·m"

if __name__ == "__main__":
    main()
