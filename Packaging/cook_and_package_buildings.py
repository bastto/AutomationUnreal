import os
import subprocess
import sys
import argparse

# ===CONFIG===
#python cook_and_package_buildings.py --project-root "C:\Path\To\My\UPROJECT_NAME" --uproject "UPROJECT_NAME"
parser = argparse.ArgumentParser(description="Cook and package building assets.")
parser.add_argument("--project-root", required=True, help="Full path to the Unreal project root directory.")
parser.add_argument("--uproject", required=True, help="Name of the .uproject file (with or without .uproject extension).")
args = parser.parse_args()

UE_ROOT = r"C:\Program Files\Epic Games\UE_5.5"  # Path to your Unreal Engine installation
UAT_PATH = os.path.join(UE_ROOT, r"Engine\Build\BatchFiles\RunUAT.bat")
UNREALPAK_PATH_WINDOWS = os.path.join(UE_ROOT, r"Engine\Binaries\Win64\UnrealPak.exe")

PROJECT_ROOT = os.path.abspath(args.project_root)
UPROJECT_NAME = args.uproject if args.uproject.endswith(".uproject") else f"{args.uproject}.uproject"
UPROJECT_PATH = os.path.join(PROJECT_ROOT, UPROJECT_NAME)

COOKED_CONTENT_ROOT = os.path.join(PROJECT_ROOT, r"Saved\Cooked\Windows", os.path.splitext(UPROJECT_NAME)[0], "Content", "Buildings")
PAK_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Saved", "Paks")

# === SETUP ===
os.makedirs(PAK_OUTPUT_DIR, exist_ok=True)

def find_buildings():
    buildings_dir = os.path.join(PROJECT_ROOT, "Content", "Buildings")
    return [f for f in os.listdir(buildings_dir) if os.path.isdir(os.path.join(buildings_dir, f))]

def cook_building(building_id):
    print(f"Cooking building {building_id}...")

    asset_dir = f"/Game/Buildings/{building_id}"

    cmd = [
        UAT_PATH,
        "BuildCookRun",
        f"-project={UPROJECT_PATH}",
        "-noP4",
        "-targetplatform=Win64",
        f"-cookdir={asset_dir}",
        "-skipstage",
        "-compressed",
        "-unversioned"
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Failed to cook building: {building_id}")
        sys.exit(1)
    print(f"Cooked: {building_id}")

def create_file_list(building_id):
    cooked_dir = os.path.join(COOKED_CONTENT_ROOT, building_id)
    file_list_path = os.path.join(PAK_OUTPUT_DIR, f"{building_id}_files.txt")

    with open(file_list_path, "w", encoding="utf-8") as file_list:
        for root, _, files in os.walk(cooked_dir):
            for file in files:
                abs_path = os.path.join(root, file).replace("\\", "/")
                rel_path = os.path.relpath(abs_path, COOKED_CONTENT_ROOT).replace("\\", "/")
                unreal_path = f"../../../{os.path.splitext(UPROJECT_NAME)[0]}/Content/Buildings/{rel_path}"
                file_list.write(f'"{abs_path}" "{unreal_path}"\n')

    return file_list_path

def package_building(building_id):
    file_list = create_file_list(building_id)
    pak_path = os.path.join(PAK_OUTPUT_DIR, f"{building_id}.pak")
    print(f"Packaging {building_id} -> {pak_path}")

    cmd = [
        UNREALPAK_PATH_WINDOWS,
        pak_path,
        f"-create={file_list}",
        "-compress"
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Failed to pak building: {building_id}")
        sys.exit(1)
    print(f"Packaged: {building_id}")

def main():
    buildings = find_buildings()
    print(f"Found {len(buildings)} buildings to process.\n")

    for b in buildings:
        cook_building(b)
        package_building(b)

    print("\n All done!")

if __name__ == "__main__":
    main()
