# ABENICS Maker

![](https://user-images.githubusercontent.com/14128408/127619980-3d9c49f2-a30f-484b-bb3c-cfea265b2f2a.png)

Fusion360 Plugin to create [ABENICS](https://ieeexplore.ieee.org/document/9415699). Blue gear and red one are SH-Gear and MP-Gear, respectively.

This script is derived from SpurGear.py which is a sample script written by Brian Ekins.
Kazuki Abe, Kenjiro Tadakuma and Riichiro Tadakuma develop ABENICS and have a presentation on [YouTube](https://www.youtube.com/watch?v=hhDdfiRCQS4).
ABENICS system is [patent pending](https://www.youtube.com/watch?v=hhDdfiRCQS4).
You have to pay attention to create and use the gears and application.

## Usage

Clone this project in your environment.

```
git clone https://github.com/botamochi6277/ABENICS-Maker.git
```

Run Fusion360 and open **Scripts and Add Ins** tab. Add `ABENICS.py` to **My Scripts**

<img width="454" alt="ScreenShot 2021-07-30 14 15 51" src="https://user-images.githubusercontent.com/14128408/127620805-5c13ea0c-b9b4-4f21-9a2d-2154df805593.png">

Input parameters and run.

## Parameters

<img width="328" alt="ScreenShot 2021-07-30 17 25 59" src="https://user-images.githubusercontent.com/14128408/127624691-662746b4-a959-4983-a1af-d36855d3c392.png">

- Pressure Angle : pressure angle of teeth. It is usually 20 deg.
- Module : module of a gear sketch. it is size of a tooth.
- Backlash : Backlash of the gear.
- Gear Thickness: Thickness of MP-Gear
- Hole Diameter: Hole diameter of MP-Gear
- Num. of teeth of SH-Gear: the number of teeth of SH-Gear
- Gear Ratio: Gear Ratio of SH-Gear/MP-Gear
- Num. of rotation steps: the number of rotation steps for engraving MP-Gear. When it is 36 steps, MP-Gear rotates by 10deg in every step.

## Process

1. Draw a half gear sketch of a SH-gear
1. Revolve the sketch profile to make a SH-Gear body
1. Draw a ring sketch for a MP-Gear
1. Extrude the sketch profiles to make a MP-Gear body
1. Engrave and rotate the MP-Gear
1. Draw a half gear sketch of SH-gear
1. Revolve the sketch profile to intersect the SH-Gear body
