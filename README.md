# ABENICS Maker

![](https://user-images.githubusercontent.com/14128408/127619980-3d9c49f2-a30f-484b-bb3c-cfea265b2f2a.png)

Fusion360 Plugin to create [ABENICS](https://ieeexplore.ieee.org/document/9415699). Blue gear and red one are CS-Gear and MP-Gear, respectively.

This script is derived from SpurGear.py which is a sample script written by Brian Ekins.
Kazuki Abe, Kenjiro Tadakuma and Riichiro Tadakuma develop ABENICS and have a presentation on [YouTube](https://www.youtube.com/watch?v=hhDdfiRCQS4).
ABENICS system is [patent pending](https://www.youtube.com/watch?v=hhDdfiRCQS4).
You have to pay attention to create and use the gears and application.

## Usage

Clone this project in your environment.

```
git clone https://github.com/botamochi6277/ABENICS-Maker.git
```

Run Fusion360 and open **Scripts and Add Ins** tab. Add `ABENICS.py` to **My Scripts** with pushing "+" icon. When you have some troubles to adding, visit [the official instruction page](https://knowledge.autodesk.com/support/fusion-360/troubleshooting/caas/sfdcarticles/sfdcarticles/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html).

<img width="454" alt="ScreenShot 2021-07-30 14 15 51" src="https://user-images.githubusercontent.com/14128408/127620805-5c13ea0c-b9b4-4f21-9a2d-2154df805593.png">

Input parameters and run. You can get gears of ABENICS.

## Parameters

<img width="328" alt="ScreenShot 2021-07-30 22 26 07" src="https://user-images.githubusercontent.com/14128408/127659685-e3026ae5-55a1-4eec-9419-1bdc0bdcf1ed.png">

- Pressure Angle : pressure angle of teeth. It is usually 20 deg.
- Module : module of a gear sketch. it is size of a tooth.
- Backlash : Backlash of the gear. It shrinks the cs-gear sketch and enlarges the sh-cutter sketch.
- Gear Thickness: Thickness of MP-Gear
- Hole Diameter: Hole diameter of MP-Gear
- Num. of teeth of CS-Gear: the number of teeth of CS-Gear
- Gear Ratio: Gear Ratio of CS-Gear/MP-Gear
- Num. of rotation steps: the number of rotation steps for engraving MP-Gear. When it is 36 steps, MP-Gear rotates by 10deg in every step.

## What this code does

This code runs according to the ABENICS Paper. The following list may you help to customize the script

1. Draw a half gear sketch of a SH-Cutter
1. Revolve the sketch profile to make a SH-Cutter body
1. Draw a ring sketch for a MP-Gear
1. Extrude the sketch profiles to make a MP-Gear body
1. Engrave and rotate the MP-Gear with SH-Cutter
1. Remove SH-Cutter
1. Draw a half gear sketch of a CS-gear
1. Revolve the sketch profile to make a CS-Gear body
1. Draw another half gear sketch of CS-gear for intersection
1. Revolve the sketch profile to intersect the CS-Gear body
