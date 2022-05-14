# GBSPConverter
These scripts were developed when attempting to transfer the maps of an old game, written using the Genesis3D engine, to Unreal/Blender/Unity. The BSP File format is shared between id Software's  Quake 2 engine, Valve's Source (GoldSrc) engine, and Genesis3D.

The BSP files are binary files containing information about geometry, which are also stored in a tree structure, from what I understand to decide what to render and what not to render.

## Different BSP versions
The header of a BSP file contains a code identifying it as such, which is `GBSP` for Genesis3D, `IBSP` for Quake and `VBSP` for Valve. The scripts in this repository can help you to convert the meshes in a GBSP file to the IBSP format. Since the way they are stored differs between standards, this is not as simple as changing the code and renaming the file. Luckily, some helpful online sources are available.

Thanks to Max McGuire for the document about the [Quake 2 BSP format](https://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml)
I've also been referencing the Genesis3D source code, to figure out how to read the GBSP file, which can be found in the [RealityFactory Github repo](https://github.com/RealityFactory/Genesis3D).

## Set up
- clone or download this repository
- ensure you have Python 3.x installed
- install Pillow (`pip install pillow`)
- you are now ready to run the scripts
## How to use
```
python gbsp_to_ibsp.py path/to/my_gbsp_file.bsp
```
Optionally, you can also provide an output file path, but if you don't the script should simply append `_ibsp` to the file name of the original file.
```
python gbsp_to_ibsp.py path/to/my_gbsp_file.bsp path/to/output_ibsp.py
```
For my own testing, I also added a script called `read_ibsp.py` to read the header of the IBSP file and show some stats stored therein.
```
python read_ibsp.py path/to/my_ibsp_file.bsp
```

## Next steps
After converting the file, it can be loaded in a tool like [Noesis](https://richwhitehouse.com/index.php?content=inc_projects.php&showproject=91) by Rich Whitehouse, to convert it to a more conventional file format like `.fbx`, `.obj`, `.stl` et cetera.

## Limitations
This is still a work-in-progress, and for now only the mesh is converted. Texture coordinates are transferred as well, but the textures themselves have not been added, neither have the tree structure or the portals and areas. If you'd like to contribute, feel free to fork this repository and create a PR.
