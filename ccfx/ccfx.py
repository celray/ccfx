'''
This module contains functions to speed general python prototyping and development.

Author     : Celray James CHAWANDA
Email      : celray@chawanda.com
Date       : 2024-09-11
License    : MIT

Repository : https://github.com/celray/ccfx
'''

# imports
import os, sys
import glob
import warnings
from netCDF4 import Dataset
from osgeo import gdal, osr
import numpy
from genericpath import exists
import shutil
import platform
import pickle
import time
from shapely.geometry import box, Point
import geopandas, pandas
from osgeo import gdal, ogr, osr
import py7zr
import subprocess
import multiprocessing
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TALB, TIT2, TRCK, TDRC, TCON, APIC, COMM, USLT, TPE2, TCOM, TPE3, TPE4, TCOP, TENC, TSRC, TBPM
from concurrent.futures import ThreadPoolExecutor
import math
import requests
from tqdm import tqdm
import yt_dlp
from typing import Optional

# functions
def listFiles(path: str, ext: str = None) -> list:
    '''
    List all files in a directory with a specific extension
    path: directory
    ext: extension (optional), variations allowed like 'txt', '.txt', '*txt', '*.txt'
    '''

    if ext is None:
        ext = '*'
    else:
        ext = ext.lstrip('*')  
        if not ext.startswith('.'):
            ext = '.' + ext  

    pattern = os.path.join(path, f'*{ext}')

    if not os.path.isdir(path):
        print(f'! Warning: {path} is not a directory')
        return []

    return glob.glob(pattern)

def getExtension(filePath:str) -> str:
    '''
    Get the extension of a file
    filePath: file path

    return: file extension without the dot
    '''
    return os.path.splitext(filePath)[1].lstrip('.')


def getMp3Metadata(fn, imagePath=None):
    '''
    This function takes a path to mp3 and returns a dictionary with
    the following keys:
    - artist, album, title, track number, year, genre
    '''
    metadata = {}
    
    try:
        audio = MP3(fn, ID3=ID3)
        
        if 'TPE1' in audio.tags: metadata['artist'] = str(audio.tags['TPE1'])
        else: metadata['artist'] = "Unknown Artist"
            
        if 'TALB' in audio.tags: metadata['album'] = str(audio.tags['TALB'])
        else: metadata['album'] = "Unknown Album"
            
        if 'TIT2' in audio.tags: metadata['title'] = str(audio.tags['TIT2'])
        else: metadata['title'] = os.path.basename(fn).replace('.mp3', '')
            
        if 'TRCK' in audio.tags: metadata['track_number'] = str(audio.tags['TRCK'])
        else: metadata['track_number'] = "0"
            
        if 'TDRC' in audio.tags: metadata['year'] = str(audio.tags['TDRC'])
        else: metadata['year'] = "Unknown Year"
            
        if 'TCON' in audio.tags: metadata['genre'] = str(audio.tags['TCON'])
        else: metadata['genre'] = "Unknown Genre"

        if imagePath is not None:
            foundImage = False
            if audio.tags:
                for tagKey in audio.tags.keys():
                    if tagKey.startswith("APIC:"):
                        with open(imagePath, 'wb') as img_file:
                            img_file.write(audio.tags[tagKey].data)
                        foundImage = True
                        break
            if not foundImage:
                print("No image found in metadata.")
    
    except Exception as e:
        print(f"Error extracting metadata from {fn}: {e}")
        # Set default values if extraction fails
        metadata = {
            'artist': "Unknown Artist",
            'album': "Unknown Album",
            'title': os.path.basename(fn).replace('.mp3', ''),
            'track_number': "0",
            'year': "Unknown Year",
            'genre': "Unknown Genre"
        }
    return metadata
    

def guessMimeType(imagePath):
    ext = os.path.splitext(imagePath.lower())[1]
    if ext in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    elif ext == '.png':
        return 'image/png'
    return 'image/png'


def downloadYoutubeVideo(url: str, dstDir: str, audioOnly: bool = False, dstFileName: Optional[str] = None ) -> str:
    """
    Download from YouTube via yt-dlp.

    Args:
        url: YouTube URL
        dstDir: output directory (created if missing)
        audioOnly: if True, extract MP3
        dstFileName: exact filename (with extension). If None, uses title.

    Returns: Full path to downloaded file.
    """
    os.makedirs(dstDir, exist_ok=True)

    if dstFileName is None:
        template = os.path.join(dstDir, "%(title)s.%(ext)s")
    else:
        template = os.path.join(dstDir, dstFileName)

    opts = {"outtmpl": template}

    if audioOnly:
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        # prefer a single MP4 file (progressive), fallback to any best if none
        opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    with yt_dlp.YoutubeDL(opts) as ytdl:
        info = ytdl.extract_info(url, download=True)

    # determine final filename
    if dstFileName:
        final = dstFileName
    else:
        ext = "mp3" if audioOnly else info.get("ext", "mp4")
        title = info.get("title", "video")
        final = f"{title}.{ext}"

    return os.path.join(dstDir, final)


def setMp3Metadata(fn, metadata, imagePath=None):
    '''
    This function takes a path to an mp3 and a metadata dictionary,
    then writes that metadata to the file's ID3 tags.
    
    The metadata dictionary should have these keys:
    - artist, album, title, track_number, year, genre
    
    Additionally, an optional imagePath parameter can be provided to
    attach album artwork from a PNG or JPEG file.
    
    Alternatively, you can include an 'imagePath' key in the metadata
    dictionary instead of using the separate parameter.
    '''
    try:
        # Try to load existing ID3 tags or create new ones if they don't exist
        try:
            audio = ID3(fn)
        except:
            audio = ID3()
            
        # Set artist
        if 'artist' in metadata and metadata['artist']: audio['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
        if 'album' in metadata and metadata['album']: audio['TALB'] = TALB(encoding=3, text=metadata['album'])
        if 'title' in metadata and metadata['title']: audio['TIT2'] = TIT2(encoding=3, text=metadata['title'])
        if 'track_number' in metadata and metadata['track_number']: audio['TRCK'] = TRCK(encoding=3, text=metadata['track_number'])
        if 'year' in metadata and metadata['year']: audio['TDRC'] = TDRC(encoding=3, text=metadata['year'])
        if 'genre' in metadata and metadata['genre']: audio['TCON'] = TCON(encoding=3, text=metadata['genre'])
        if 'comment' in metadata and metadata['comment']: audio['COMM'] = COMM(encoding=3, text=metadata['comment'])
        if 'lyrics' in metadata and metadata['lyrics']: audio['USLT'] = USLT(encoding=3, text=metadata['lyrics'])
        if 'publisher' in metadata and metadata['publisher']: audio['TPUB'] = TPE2(encoding=3, text=metadata['publisher'])
        if 'composer' in metadata and metadata['composer']: audio['TCOM'] = TCOM(encoding=3, text=metadata['composer'])
        if 'conductor' in metadata and metadata['conductor']: audio['TPE3'] = TPE3(encoding=3, text=metadata['conductor'])
        if 'performer' in metadata and metadata['performer']: audio['TPE4'] = TPE4(encoding=3, text=metadata['performer'])
        if 'copyright' in metadata and metadata['copyright']: audio['TCOP'] = TCOP(encoding=3, text=metadata['copyright'])
        if 'encoded_by' in metadata and metadata['encoded_by']: audio['TENC'] = TENC(encoding=3, text=metadata['encoded_by'])
        if 'encoder' in metadata and metadata['encoder']: audio['TENC'] = TENC(encoding=3, text=metadata['encoder'])
        if 'isrc' in metadata and metadata['isrc']: audio['TSRC'] = TSRC(encoding=3, text=metadata['isrc'])
        if 'bpm' in metadata and metadata['bpm']: audio['TBPM'] = TBPM(encoding=3, text=metadata['bpm'])
        # Check if image path is in metadata dictionary and not provided as parameter
        if imagePath is None and 'imagePath' in metadata:
            imagePath = metadata['imagePath']
        
        # Attach image if provided
        if imagePath and os.path.exists(imagePath):
            with open(imagePath, 'rb') as img_file:
                img_data = img_file.read()
                
            # Determine image MIME type
            mime = guessMimeType(imagePath)
                
            # Create APIC frame for album artwork
            audio['APIC'] = APIC(
                encoding=3,         # UTF-8 encoding
                mime=mime,          # MIME type of the image
                type=3,             # 3 means 'Cover (front)'
                desc='Cover',       # Description
                data=img_data       # The image data
            )
                
        # Save changes to the file
        audio.save(fn)
        return True
    
    except Exception as e:
        print(f"Error writing metadata to {fn}: {e}")
        return False


def deleteFile(filePath:str, v:bool = False) -> bool:
    '''
    Delete a file
    filePath: file path
    v: verbose (default is True)

    return: True if the file is deleted, False otherwise
    '''

    deleted = False
    if os.path.exists(filePath):
        try:
            os.remove(filePath)
            deleted = True
        except:
            print(f'! Could not delete {filePath}')
            deleted = False
        if v:
            print(f'> {filePath} deleted')
    else:
        if v:
            print(f'! {filePath} does not exist')
        deleted = False
    
    return deleted

def deletePath(path:str, v:bool = False) -> bool:
    '''
    Delete a directory

    path: directory
    v: verbose (default is True)

    return: True if the directory is deleted, False otherwise
    '''
    deleted = False
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            deleted = True
        except:
            print(f'! Could not delete {path}')
            deleted = False
        if v:
            print(f'> {path} deleted')
    else:
        if v:
            print(f'! {path} does not exist')
        deleted = False


def downloadChunk(url, start, end, path):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def downloadFile(url, save_path, exists_action='resume', num_connections=5, v=False):
    if v:
        print(f"\ndownloading {url}")
    fname = getFileBaseName(url, extension=True)
    save_dir = os.path.dirname(save_path)
    save_fname = "{0}/{1}".format(save_dir, fname)

    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # Handle existing file
    if os.path.exists(save_fname):
        if exists_action == 'skip':
            if v:
                print(f"File exists, skipping: {save_fname}")
            return
        elif exists_action == 'overwrite':
            os.remove(save_fname)
        # 'resume' is handled below

    # Get file size
    response = requests.head(url)
    file_size = int(response.headers.get('content-length', 0))

    # Resume download if file exists and exists_action is 'resume'
    initial_pos = 0
    if exists_action == 'resume' and os.path.exists(save_fname):
        initial_pos = os.path.getsize(save_fname)
        if initial_pos >= file_size:
            if v:
                print(f"File already completed: {save_fname}")
            return

    # Calculate chunk sizes
    chunk_size = math.ceil((file_size - initial_pos) / num_connections)
    chunks = []
    for i in range(num_connections):
        start = initial_pos + (i * chunk_size)
        end = min(start + chunk_size - 1, file_size - 1)
        chunks.append((start, end))

    # Download chunks in parallel
    temp_files = [f"{save_fname}.part{i}" for i in range(num_connections)]
    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        futures = []
        for i, (start, end) in enumerate(chunks):
            futures.append(
                executor.submit(downloadChunk, url, start, end, temp_files[i])
            )
        
        # Wait for all downloads to complete with progress bar
        with tqdm(total=file_size-initial_pos, initial=initial_pos, unit='B', 
                 unit_scale=True, desc=fname) as pbar:
            completed = initial_pos
            while completed < file_size:
                current = sum(os.path.getsize(f) for f in temp_files if os.path.exists(f))
                pbar.update(current - completed)
                completed = current

    # Merge chunks
    with open(save_fname, 'ab' if initial_pos > 0 else 'wb') as outfile:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                with open(temp_file, 'rb') as infile:
                    outfile.write(infile.read())
                os.remove(temp_file)


def mergeRasterTiles(tileList:list, outFile:str) -> str:
    '''
    Merge raster tiles into one raster file
    tileList: list of raster files
    outFile: output raster file
    '''
    gdal.Warp(outFile, tileList)
    return outFile

def mergeRasterFiles(tileList:list, outFile:str) -> str:
    '''
    this function is an alias for mergeRasterTiles
    '''
    return mergeRasterTiles(tileList, outFile)


def systemPlatform() -> str:
    '''
    Get the system platform
    '''
    return platform.system()

def progressBar(count, total, message=""):
    percent = int(count / total * 100)
    filled = int(percent / 2)
    bar = '█' * filled + '░' * (50 - filled)
    print(f'\r{message} |{bar}| {percent}% [{count}/{total}]', end='', flush=True)
    if count == total:
        print()

def fileCount(path:str = "./", extension:str = ".*", v:bool = True) -> int:
    '''
    get the number of files in a directory with a specific extension
    path: directory
    ext: extension
    v: verbose (default is True)
    '''
    count = len(listFiles(path, extension))
    if v:
        print(f'> there are {count} {extension if not extension ==".*" else ""} files in {path}')
    return count

def resampleRaster(inFile:str, outFile:str, resolution:float, dstSRS = None, resamplingMethod = 'bilinear', replaceOutput:bool = True, v:bool = True) -> str:
    '''
    Resample a raster file
    inFile: input raster file
    outFile: output raster file
    resolution: resolution in the same units as the input raster
    v: verbose (default is True)
    available resample types:
        'nearest', 'bilinear', 'cubic', 'cubicspline', 'lanczos', 'average', 'mode', 'max', 'min', 'med', 'q1', 'q3'
    
    return: output raster file path
    '''

    resamleTypes = {
        'nearest': gdal.GRA_NearestNeighbour,
        'bilinear': gdal.GRA_Bilinear,
        'cubic': gdal.GRA_Cubic,
        'cubicspline': gdal.GRA_CubicSpline,
        'lanczos': gdal.GRA_Lanczos,
        'average': gdal.GRA_Average,
        'mode': gdal.GRA_Mode,
        'max': gdal.GRA_Max,
        'min': gdal.GRA_Min,
        'med': gdal.GRA_Med,
        'q1': gdal.GRA_Q1,
        'q3': gdal.GRA_Q3
    }

    if not os.path.exists(inFile):
        print(f'! {inFile} does not exist')
        return None
    
    if os.path.exists(outFile):
        if replaceOutput:
            os.remove(outFile)
        else:
            print(f'! {outFile} already exists')      
            return None
    
    if v:
        print(f'> resampling {inFile} to {outFile} at {resolution}')
    
    ds = gdal.Open(inFile)
    if dstSRS is None: gdal.Warp(outFile, ds, xRes=resolution, yRes=resolution, resampleAlg=resamleTypes[resamplingMethod])
    else: gdal.Warp(outFile, ds, xRes=resolution, yRes=resolution, resampleAlg=resamleTypes[resamplingMethod], dstSRS=dstSRS)

    ds = None
    return outFile

def watchFileCount(path:str="./", extension:str = ".*", interval:float = 0.2, duration = 3, v:bool = True) -> None:
    '''
    Watch the number of files in a directory with a specific extension
    path: directory
    extension: extension
    interval: time interval in seconds
    duration: duration in minutes
    v: verbose (default is True)
    '''

    duration *= 60
    count = 0
    end = time.time() + duration
    while time.time() < end:
        count = fileCount(path, extension, False)
        sys.stdout.write(f'\r\t> {count} {extension if not extension ==".*" else ""} files in {path}   ')
        sys.stdout.flush()
        time.sleep(interval)
    
    return None


def pythonVariable(filename, option, variable=None):
    '''
    option: save, load or open

    '''
    if ((option == "save") or (option == "dump")) and (variable is None):
        print("\t! please specify a variable")

    if (option == "save") or (option == "dump"):
        createPath(os.path.dirname(filename))
        with open(filename, 'wb') as f:
            pickle.dump(variable, f)

    if (option == "load") or (option == "open"):
        with open(filename, "rb") as f:
            variable = pickle.load(f)

    return variable


def listFolders(path:str) -> list:
    '''
    List all folders in a directory
    path: directory 
    (use './' for current directory and always use forward slashes)
    '''
    if not path.endswith('/'):
        path += '/'
    
    if os.path.exists(path):
        return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    else:
        return []

def readFrom(filename, decode_codec = None, v=False):
    '''
    a function to read ascii files
    '''
    try:
        if not decode_codec is None: g = open(filename, 'rb')
        else: g = open(filename, 'r')
    except:
        print("\t! error reading {0}, make sure the file exists".format(filename))
        return

    file_text = g.readlines()
    if not decode_codec is None: file_text = [line.decode(decode_codec) for line in file_text]
    if v: print("\t> read {0}".format(getFileBaseName(filename, extension=True)))
    g.close
    return file_text


def pointsToGeodataframe(point_pairs_list, columns = ['latitude', 'longitude'], auth = "EPSG", code = '4326', out_shape = '', format = 'gpkg', v = False, get_geometry_only = False):
    df = pandas.DataFrame(point_pairs_list, columns = columns)
    geometry = [Point(xy) for xy in zip(df['latitude'], df['longitude'])]

    if get_geometry_only:
        return geometry[0]

    gdf = geopandas.GeoDataFrame(point_pairs_list, columns = columns, geometry=geometry)
    drivers = {'gpkg': 'GPKG', 'shp': 'ESRI Shapefile'}

    gdf = gdf.set_crs(f'{auth}:{code}')
    
    if out_shape != '':
        if v: print(f'creating shapefile {out_shape}')
        gdf.to_file(out_shape, driver=drivers[format])
    
    return gdf


def readFile(filename, decode_codec = None, v=False):
    return readFrom(filename, decode_codec, v)

def writeTo(filename, file_text, encode_codec = None, v=False) -> bool:
    '''
    a function to write ascii files
    '''
    try:
        if not encode_codec is None: g = open(filename, 'wb')
        else: g = open(filename, 'w')
    except:
        print("\t! error writing to {0}".format(filename))
        return False

    createPath(os.path.dirname(filename))

    if not encode_codec is None: file_text = [line.encode(encode_codec) for line in file_text]
    g.writelines(file_text)
    g.close
    if v: print("\t> wrote {0}".format(getFileBaseName(filename, extension=True)))
    return True

def writeToFile(filename, file_text, encode_codec = None, v=False) -> bool:
    return writeTo(filename, file_text, encode_codec, v)

def writeFile(filename, file_text, encode_codec = None, v=False) -> bool:
    return writeTo(filename, file_text, encode_codec, v)

def createPath(pathName, v = False):
    '''
    this function creates a directory if it does not exist
    pathName: the path to create
    v: verbose (default is False)
    '''
    if pathName == '':
        return './'

    if pathName.endswith('\\'): pathName = pathName[:-1]
    if not pathName.endswith('/'): pathName += '/'

    if not os.path.isdir(pathName):
        os.makedirs(pathName)
        if v: print(f"\t> created path: {pathName}")
    if pathName.endswith("/"): pathName = pathName[:-1]
    return pathName


def renameNetCDFvariable(input_file: str, output_file: str, old_var_name: str, new_var_name: str, v = False) -> None:
    """
    Renames a variable in a NetCDF file using CDO if it exists.
    If the variable does not exist, the file is copied without modification.
    
    :param input_file: Path to the input NetCDF file
    :param output_file: Path to the output NetCDF file
    :param old_var_name: Name of the variable to rename
    :param new_var_name: New name for the variable
    """
    try:
        # Check if the variable exists in the input file using `cdo showname`
        result = subprocess.run(
            ["cdo", "showname", input_file],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if the old variable name is in the output
        if old_var_name in result.stdout:
            # Rename the variable using `cdo chname`
            subprocess.run(
                ["cdo", f"chname,{old_var_name},{new_var_name}", input_file, output_file],
                check=True
            )
            if v: print(f"Variable '{old_var_name}' renamed to '{new_var_name}' in '{output_file}'.")
        else:
            # Copy the file without renaming
            shutil.move(input_file, output_file)
            if v: print(f"Variable '{old_var_name}' not found; '{input_file}' moved to '{output_file}' without modification.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

def compressTo7z(input_dir: str, output_file: str):
    """
    Compresses the contents of a directory to a .7z archive with maximum compression.
    
    :param input_dir: Path to the directory to compress
    :param output_file: Output .7z file path
    """
    # Create the .7z archive with LZMA2 compression
    with py7zr.SevenZipFile(output_file, 'w', filters=[{'id': py7zr.FILTER_LZMA2, 'preset': 9}]) as archive:
        # Add each item in the input directory, avoiding the top-level folder in the archive
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to the archive with a relative path to avoid including the 'tmp' folder itself
                archive.write(file_path, arcname=os.path.relpath(file_path, start=input_dir))


def moveDirectory(srcDir:str, destDir:str, v:bool = False) -> bool:
    '''
    this function moves all files from srcDir to destDir
    srcDir: the source directory
    destDir: the destination directory
    return: True if the operation is successful, False otherwise
    '''
    # Ensure both directories exist
    if not os.path.isdir(srcDir):
        print("! source directory does not exist")
        return False
    
    if not os.path.isdir(destDir):
        createPath(f"{destDir}/")

    # Get a list of all files in the source directory
    files = [f for f in os.listdir(srcDir) if os.path.isfile(os.path.join(srcDir, f))]
    
    # Move each file to the destination directory
    for file in files:
        src_path = os.path.join(srcDir, file)
        dest_path = os.path.join(destDir, file)
        if v:
            print(f"\t> moving {src_path} to {dest_path}")
        shutil.move(src_path, dest_path)
    
    return True


def moveDirectoryFiles(srcDir: str, destDir: str, v: bool = False) -> bool:
    '''
    This function moves all files from srcDir to destDir one at a time.
    It also moves empty directories at the end to ensure no empty folders remain in srcDir.
    srcDir: the source directory
    destDir: the destination directory
    v: verbose flag for printing actions
    return: True if the operation is successful, False otherwise
    '''
    # Ensure both directories exist
    if not os.path.isdir(srcDir):
        print("! Source directory does not exist")
        return False

    if not os.path.isdir(destDir):
        os.makedirs(destDir, exist_ok=True)

    # Walk through the directory tree
    for root, dirs, files in os.walk(srcDir, topdown=True):
        # Compute the relative path from the source directory
        rel_path = os.path.relpath(root, srcDir)
        # Compute the destination root path
        dest_root = os.path.join(destDir, rel_path) if rel_path != '.' else destDir

        # Create destination directories if they don't exist
        if not os.path.exists(dest_root):
            os.makedirs(dest_root, exist_ok=True)

        # Move files
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            if v:
                print(f"\t> Moving file \n\t - {src_file}\n\t     to {dest_file}")
            try:
                shutil.move(src_file, dest_file)
            except Exception as e:
                print(f"! Error moving file: {e}")

    return True


def clipRasterByExtent(inFile: str, outFile: str, bounds: tuple) -> str:
    '''
    Clips a raster using GDAL translate
    inFile: input raster path
    outFile: output path
    bounds: tuple (minx, miny, maxx, maxy)
    return: output path
    '''
    ds = gdal.Open(inFile)
    gdal.Translate(outFile, ds, projWin=[bounds[0], bounds[3], bounds[2], bounds[1]])
    ds = None
    return outFile

def clipVectorByExtent(inFile: str, outFile: str, bounds: tuple) -> str:
    '''
    Clips a vector using GeoPandas
    inFile: input vector path
    outFile: output path
    bounds: tuple (minx, miny, maxx, maxy)
    return: output path
    '''
    # Load the vector file as a GeoDataFrame
    gdf = geopandas.read_file(inFile)
    bbox = box(bounds[0], bounds[1], bounds[2], bounds[3])
    clipped = gdf.clip(bbox)
    clipped.to_file(outFile)
    
    return outFile

def reprojectRaster(inFile: str, outFile: str, dstProjection: str, resamplingMethod: str = 'mode') -> str:
    '''
    Reprojects a raster to a new projection
    inFile: input raster path
    outFile: output raster path
    dstProjection: target projection in "AUTH:CODE" format (e.g., "EPSG:3395")
    resamplingMethod: resampling method to use (default is 'mode')
    return: output path
    '''
    # Open the input raster
    ds = gdal.Open(inFile)
    
    # Define resampling method
    resampling_methods = {
        'nearest': gdal.GRA_NearestNeighbour,
        'bilinear': gdal.GRA_Bilinear,
        'cubic': gdal.GRA_Cubic,
        'cubicspline': gdal.GRA_CubicSpline,
        'lanczos': gdal.GRA_Lanczos,
        'average': gdal.GRA_Average,
        'mode': gdal.GRA_Mode,
        'max': gdal.GRA_Max,
        'min': gdal.GRA_Min,
        'med': gdal.GRA_Med,
        'q1': gdal.GRA_Q1,
        'q3': gdal.GRA_Q3
    }
    
    resampling = resampling_methods.get(resamplingMethod, gdal.GRA_Mode)
    gdal.Warp(outFile, ds, dstSRS=dstProjection, resampleAlg=resampling)
    ds = None
    
    return outFile

def rasterizeRaster(inFile: str, outFile: str, targetField: str, targetResolution: float) -> str:
    '''
    Rasterizes a vector layer to a raster file
    inFile: input vector file path
    outFile: output raster file path
    targetField: the field in the vector layer to use as the raster value
    targetResolution: resolution of the output raster (in units of the vector CRS)
    return: output raster path
    '''
    # Open the vector file
    vector_ds = ogr.Open(inFile)
    layer = vector_ds.GetLayer()
    
    # Get the extent of the vector layer
    x_min, x_max, y_min, y_max = layer.GetExtent()
    
    # Calculate the raster size based on target resolution
    x_res = int((x_max - x_min) / targetResolution)
    y_res = int((y_max - y_min) / targetResolution)
    
    # Create the raster dataset
    target_ds = gdal.GetDriverByName('GTiff').Create(outFile, x_res, y_res, 1, gdal.GDT_Int16)
    target_ds.SetGeoTransform((x_min, targetResolution, 0, y_max, 0, -targetResolution))
    
    # Set the projection from the vector layer
    srs = layer.GetSpatialRef()
    target_ds.SetProjection(srs.ExportToWkt())
    
    # Set the no-data value to -999
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(-999)

    # Rasterize the vector layer
    gdal.RasterizeLayer(target_ds, [1], layer, options=["ATTRIBUTE=" + targetField])
    
    # Close the datasets
    band = None
    target_ds = None
    vector_ds = None
    
    return outFile


def getVectorBounds(grid_gdf: geopandas.GeoDataFrame) -> tuple:
    '''
    This function gets the bounds of a GeoDataFrame
    grid_gdf: GeoDataFrame

    return: minx, miny, maxx, maxy
    '''
    # Initialize min and max values with extreme values
    minx, miny = numpy.inf, numpy.inf
    maxx, maxy = -numpy.inf, -numpy.inf

    # Iterate through each geometry in the GeoDataFrame
    for geom in grid_gdf.geometry:
        # Get bounds for each geometry (minx, miny, maxx, maxy)
        geom_minx, geom_miny, geom_maxx, geom_maxy = geom.bounds
        
        # Update the global min/max for x and y
        minx = min(minx, geom_minx)
        miny = min(miny, geom_miny)
        maxx = max(maxx, geom_maxx)
        maxy = max(maxy, geom_maxy)

    return minx, miny, maxx, maxy

def ignoreWarnings(ignore:bool = True, v:bool = False) -> None:
    '''
    Ignore warnings
    ignore: True to ignore warnings, False to show warnings
    v: verbose (default is False)
    
    returns: None
    '''
    if ignore:
        warnings.filterwarnings("ignore")
        if v: print("warnings ignored")
    else:
        warnings.filterwarnings("default")
        if v: print("warnings not ignored")
    return None


def createGrid(shapefile_path: str, resolution: float, useDegree: bool=True) -> tuple:
    '''
    This function creates a grid of polygons based on a shapefile
    shapefile_path: path to the shapefile
    resolution: resolution of the grid
    useDegree: use degree (default is True)

    return: xx, yy, polygons, within_mask, gdf.crs, minx, miny
    '''
    # Read the shapefile
    gdf = geopandas.read_file(shapefile_path)

    if useDegree:
        gdf = gdf.to_crs(epsg=4326)
    
    # Get the bounds of the shapefile
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Create a grid based on the bounds and resolution
    x = numpy.arange(minx, maxx, resolution)
    y = numpy.arange(miny, maxy, resolution)
    xx, yy = numpy.meshgrid(x, y)
    
    # Create polygons for each grid cell, arranged in 2D array
    grid_shape = xx.shape
    polygons = numpy.empty(grid_shape, dtype=object)
    for i in range(grid_shape[0]):
        for j in range(grid_shape[1]):
            x0, y0 = xx[i, j], yy[i, j]
            x1, y1 = x0 + resolution, y0 + resolution
            polygons[i, j] = box(x0, y0, x1, y1)
    
    # Flatten the polygons for GeoDataFrame creation
    flat_polygons = polygons.ravel()
    
    # Create a GeoDataFrame from the grid
    grid_gdf = geopandas.GeoDataFrame({'geometry': flat_polygons}, crs=gdf.crs)

    minx, miny, maxx, maxy = grid_gdf.total_bounds
    print("   minx:", minx, "miny:", miny, "maxx:", maxx, "maxy:", maxy)

    minx, miny, maxx, maxy = getVectorBounds(grid_gdf)
    # Add a column to indicate if the cell intersects with the original shapefile
    grid_gdf['within'] = grid_gdf.intersects(gdf.unary_union)
    
    # Reshape the 'within' mask to grid shape
    within_mask = grid_gdf['within'].values.reshape(grid_shape)
    
    # Save the grid
    reprojectedGrid = grid_gdf.to_crs(epsg=4326)

    grid_gdf.to_file("generatedGrid4326.gpkg", driver="GPKG")
    reprojectedGrid.to_file("generatedGrid.gpkg", driver="GPKG")
    
    return xx, yy, polygons, within_mask, gdf.crs, minx, miny

def setHomeDir(path:str) -> str:
    '''
    Set the working directory to location of script that imported this function
    '''
    homeDir = os.path.dirname(os.path.realpath(path))
    os.chdir(homeDir)

    return homeDir

def listDirectories(path:str) -> list:
    '''
    List all directories in a directory
    path : directory
    '''
    return listFolders(path)


def netcdfVariablesList(ncFile:str) -> list:
    '''
    List all variables in a NetCDF file
    ncFile: NetCDF file
    '''
    nc = Dataset(ncFile)
    return list(nc.variables.keys())

def netcdfVariableDimensions(ncFile: str, variable: str) -> dict:
    '''
    Get available bands (e.g., time, level, depth) for a given variable in a NetCDF file.
    
    ncFile: NetCDF file (str)
    variable: Name of the variable (str)
    
    Returns:
    A dictionary with dimension names and their sizes (e.g., time steps or levels).
    '''
    # Open the NetCDF file
    nc = Dataset(ncFile)
    
    # Check if the variable exists in the file
    if variable not in nc.variables:
        raise ValueError(f"Variable '{variable}' not found in {ncFile}")
    
    # Access the variable
    var = nc.variables[variable]
    
    # Get dimensions associated with the variable
    dimensions = var.dimensions
    
    # Create a dictionary with dimension names and their sizes
    bands_info = {}
    for dim in dimensions:
        bands_info[dim] = len(nc.dimensions[dim])
    
    return bands_info

def netcdfExportTif(ncFile: str, variable: str, outputFile: str = None, band: int = None, v:bool = True) -> gdal.Dataset:
    '''
    Export a variable from a NetCDF file to a GeoTiff file
    ncFile: NetCDF file
    variable: variable to export
    outputFile: GeoTiff file (optional)
    band: Band number to export (optional, return all bands if not specified)
    '''
    input_string = f'NETCDF:"{ncFile}":{variable}"'
    
    if v: print(f'> Exporting {variable} from {ncFile} to {outputFile}')
    if outputFile:
        if not os.path.exists(outputFile):
            dirName = os.path.dirname(outputFile)
            if not os.path.exists(dirName):
                os.makedirs(dirName)
        if band:
            dataset = gdal.Translate(outputFile, input_string, bandList=[band])
        else:
            dataset = gdal.Translate(outputFile, input_string)
    else:
        if band:
            dataset = gdal.Translate('', input_string, format='MEM', bandList=[band])
        else:
            dataset = gdal.Translate('', input_string, format='MEM')
    
    return dataset


def getFileBaseName(filePath:str, extension:bool = True) -> str:
    '''
    Get the base name of a file
    filePath: file path
    extension: include extension
    '''
    baseName = os.path.basename(filePath)
    if extension:
        return baseName
    else:
        return os.path.splitext(baseName)[0]

def netcdfAverageMap(ncFiles:list, variable:str, band:int = 1) -> numpy.ndarray:
    sum_array = netcdfSumMaps(ncFiles, variable, band=band)
    return sum_array / len(ncFiles)

def netcdfSumMaps(ncFiles:list, variable:str, band:int = 1) -> numpy.ndarray:
    sum_array = None
    for ncFile in ncFiles:
        dataset = netcdfExportTif(ncFile, variable, band=band, v=False)
        data = dataset.GetRasterBand(1)
        data = data.ReadAsArray()
        if sum_array is None:
            sum_array = numpy.zeros_like(data, dtype=numpy.float32)
        sum_array += data
    return sum_array


def tiffWriteArray(array: numpy.ndarray, outputFile: str, 
                     geoTransform: tuple = (0, 1, 0, 0, 0, -1), 
                     projection: str = 'EPSG:4326',
                     noData:float = None,
                     v:bool = False) -> gdal.Dataset:
    '''
    Write a numpy array to a GeoTIFF file
    array         : numpy array to write
    outputFile    : output GeoTIFF file
    geoTransform  : GeoTransform tuple (default is (0, 1, 0, 0, 0, -1)) 
                    example: (originX, pixelWidth, 0, originY, 0, -pixelHeight)
    projection    : Projection string (default is 'EPSG:4326')
    '''
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(outputFile, array.shape[1], array.shape[0], 1, gdal.GDT_Float32)
    
    # Set GeoTransform
    out_ds.SetGeoTransform(geoTransform)
    
    # Set Projection
    srs = osr.SpatialReference()
    srs.SetFromUserInput(projection)
    out_ds.SetProjection(srs.ExportToWkt())

    # Write array to band
    out_band = out_ds.GetRasterBand(1)
    # Set NoData
    if noData:
        out_band.SetNoDataValue(noData)
    
    out_band.WriteArray(array)
    out_band.FlushCache()
    
    if v:
        print(f'> Array written to {outputFile}')
    return out_ds

def copyFile(source:str, destination:str, v:bool = True) -> None:
    '''
    Copy a file from source to destination
    source: source file
    destination: destination file
    '''
    if not exists(os.path.dirname(destination)): createPath(f"{os.path.dirname(destination)}/")
    with open(source, 'rb') as src:
        with open(destination, 'wb') as dest: dest.write(src.read())
    
    if v: print(f'> {source} copied to \t - {destination}')


def copyDirectory(source:str, destination:str, recursive = True, v:bool = True, filter = []) -> None:
    '''
    Copy a directory from source to destination
    source: source directory
    destination: destination directory
    recursive: copy subdirectories (default is True)
    v: verbose (default is True)
    filter: list of file extensions to filter out
    '''
    if not exists(destination): os.makedirs(destination)

    itemCount = None
    counter = 1

    if recursive:
        if len(filter) > 0:
            itemCount = len([fn for fn in listAllFiles(source) if not getExtension(fn) in filter])
        else:
            itemCount = len(listAllFiles(source))
    else:
        if len(filter) > 0:
            itemCount = len([fn for fn in listFiles(source) if not getExtension(fn) in filter])
        else:
            itemCount = len(listFiles(source))


    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            if recursive: copyDirectory(s, d, recursive, v, filter)
        else:
            if len(filter) > 0:
                if not getExtension(s) in filter:
                    copyFile(s, d, v = False)
                    counter += 1
                    if v: showProgress(counter, itemCount, f'copying {getFileBaseName(item)}\t\t', barLength=50)
            else:
                copyFile(s, d, v = False)
                if v: showProgress(counter, itemCount, f'copying {getFileBaseName(item)}\t\t', barLength=50)
                counter += 1
    print()


def copyFolder(source:str, destination:str, v:bool = True) -> None:
    '''
    this function is an alias for copyDirectory
    '''
    copyDirectory(source, destination, v)


def convertCoordinates(lon, lat, srcEPSG, dstCRS) -> tuple:
    """
    this function converts coordinates from one CRS to another
    
    lon: longitude
    lat: latitude
    srcEPSG: source CRS
    dstCRS: destination CRS
    
    return: tuple (new_lon, new_lat)
    """
    gdf = geopandas.GeoDataFrame(geometry=[Point(lon, lat)], crs=f"{srcEPSG.upper()}")
    gdf_converted = gdf.to_crs(dstCRS.upper())
    new_lon, new_lat = gdf_converted.geometry.x[0], gdf_converted.geometry.y[0]
    return (new_lon, new_lat)


def extractRasterValue(rasterPath: str, lat: float, lon: float, coordProj: str = 'EPSG:4326') -> float:
    """
    Extract raster value at given coordinates.
    
    Args:
        rasterPath (str): Path to the raster file
        lat (float): Latitude of the point
        lon (float): Longitude of the point
        coordProj (str): Projection of input coordinates (default: 'EPSG:4326')
    
    Returns:
        float: Raster value at the specified coordinates
    """
    # Open raster dataset
    if not exists(rasterPath): raise ValueError(f"Raster file not found: {rasterPath}")
    
    ds = gdal.Open(rasterPath)
    if ds is None: raise ValueError(f"Could not open raster file: {rasterPath}")
    
    # Check if raster has projection
    raster_proj = ds.GetProjection()
    if not raster_proj:
        raise ValueError("Raster has no projection information")
    
    # Convert coordinates to raster projection
    x, y = convertCoordinates(lon, lat, coordProj, raster_proj)
    
    # Get geotransform parameters and calculate pixel coordinates
    geotransform = ds.GetGeoTransform()
    px = int((x - geotransform[0]) / geotransform[1])
    py = int((y - geotransform[3]) / geotransform[5])
    
    # Check if within bounds
    if px < 0 or px >= ds.RasterXSize or py < 0 or py >= ds.RasterYSize:
        print(f"! point ({lat}, {lon}) is outside raster bounds")
        ds = None
        return None
    
    # Get value at pixel
    value = ds.GetRasterBand(1).ReadAsArray(px, py, 1, 1)[0][0]
    ds = None
    
    return float(value)


def getRasterValue(rasterPath: str, lat: float, lon: float, coordProj: str = 'EPSG:4326') -> float:
    '''
    this function is a wrapper for extractRasterValue
    '''
    return extractRasterValue(rasterPath, lat, lon, coordProj)


def isBetween(number:float, a:float, b:float) -> bool:
    '''
    this function returns True if number is between a and b
    it also takes care if the user swaps a and b
    '''
    if a > b: a, b = b, a
    return a <= number <= b

def showProgress(count: int, end: int, message: str, barLength: int = 100) -> None:
    '''
    Display a progress bar
    count: current count
    end: end count
    message: message to display
    barLength: length of the progress bar
    '''
    percent = int(count / end * 100)
    percentStr = f'{percent:03.1f}'
    filled = int(barLength * count / end)
    bar = '█' * filled + '░' * (barLength - filled)
    print(f'\r{bar}| {percentStr}% [{count}/{end}] | {message}       ', end='', flush=True)
    if count == end:
        print(f'\r{bar}| {percentStr}% [{count}/{end}]                          ', end='', flush=True)
        print()


def listAllFiles(folder, extension="*"):
    list_of_files = []
    # Getting the current work directory (cwd)
    thisdir = folder

    # r=root, d=directories, f = files
    for r, d, f in os.walk(thisdir):
        for file in f:
            if extension == "*":
                list_of_files.append(os.path.join(r, file))
            elif "." in extension:
                if file.endswith(extension[1:]):
                    list_of_files.append(os.path.join(r, file))
                    # print(os.path.join(r, file))
            else:
                if file.endswith(extension):
                    list_of_files.append(os.path.join(r, file))
                    # print(os.path.join(r, file))

    return list_of_files


def clipFeatures(inputFeaturePath:str, boundaryFeature:str, outputFeature:str, keepOnlyTypes = None, v = False) -> geopandas.GeoDataFrame:
    '''
    keepOnlyTypes = ['MultiPolygon', 'Polygon', 'Point', etc]
    
    '''
    mask_gdf = geopandas.read_file(boundaryFeature)
    input_gdf = geopandas.read_file(inputFeaturePath)

    outDir = os.path.dirname(outputFeature)
    createPath(f"{outDir}/")
    out_gdf = input_gdf.clip(mask_gdf.to_crs(input_gdf.crs))

    if not keepOnlyTypes is None:
        out_gdf = out_gdf[out_gdf.geometry.apply(lambda x : x.type in keepOnlyTypes)]

    out_gdf.to_file(outputFeature)

    if v:
        print("\t  - clipped feature to " + outputFeature)
    return out_gdf



def createPointGeometry(coords: list, proj: str = "EPSG:4326") -> geopandas.GeoDataFrame:
    '''
    Convert list of coordinate tuples to GeoDataFrame
    coords: list of tuples (lat, lon, *labels)
    proj: projection string e.g. "EPSG:4326"
    return: GeoDataFrame
    '''
    data = []
    geoms = []
    max_labels = max(len(coord) - 2 for coord in coords)
    
    for coord in coords:
        lat, lon = coord[0], coord[1]
        labels = coord[2:] if len(coord) > 2 else []
        geoms.append(Point(lon, lat))  # Note: Point takes (x,y) = (lon,lat)
        data.append(labels)
        
    df = pandas.DataFrame(data)
    df.columns = [f'label{i+1}' for i in range(len(df.columns))]
    gdf = geopandas.GeoDataFrame(df, geometry=geoms, crs=proj)
    gdf.reset_index(inplace=True)
    return gdf

def calculateTimeseriesStats(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> dict:
    '''
    Calculate statistics for a timeseries

    the assumed dataframe structure is:
        date - DateTime
        observed - float
        simulated - float
        
    Parameters:
        data: pandas.DataFrame
            DataFrame containing the timeseries data
        observed: str
            name of the observed column
        simulated: str
            name of the simulated column
        resample: str
            if specified, the data will be resampled to the specified frequency
            available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    Returns:
        dict: Dictionary containing the following statistics:
            NSE: Nash-Sutcliffe Efficiency
            KGE: Kling-Gupta Efficiency
            PBIAS: Percent Bias
            LNSE: Log Nash-Sutcliffe Efficiency
            R2: R-squared
            RMSE: Root Mean Square Error
            MAE: Mean Absolute Error
            MSE: Mean Square Error
            MAPE: Mean Absolute Percentage Error
            alpha: Ratio of standard deviations
            beta: Ratio of means
    '''

    options = {'H': '1H', 'D': '1D', 'M': '1M', 'Y': '1Y'}

    if resample:
        if resample not in options:
            raise ValueError(f"Invalid resample option. Choose from {list(options.keys())}")
        if not 'date' in data.columns:
            for col in data.columns:
                if data[col].dtype == 'datetime64[ns]':
                    data = data.set_index(col).resample(options[resample]).mean()
                    break
            else:
                raise ValueError("No datetime column found for resampling.")
        else:
            data = data.set_index('date').resample(options[resample]).mean()

    # Auto-detect columns if not specified
    if not observed and not simulated:
        datetime_cols = [col for col in data.columns if data[col].dtype == 'datetime64[ns]']
        if datetime_cols:
            data = data.drop(datetime_cols, axis=1)
        
        if len(data.columns) == 2:
            observed = data.columns[0]
            simulated = data.columns[1]
        else:
            raise ValueError("Could not automatically detect observed and simulated columns")
    elif not observed or not simulated:
        raise ValueError("Both observed and simulated columns must be specified if one is specified")

    # Extract data
    obs = data[observed].values
    sim = data[simulated].values

    # Remove any rows where either observed or simulated is NaN
    mask = ~(numpy.isnan(obs) | numpy.isnan(sim))
    obs = obs[mask]
    sim = sim[mask]

    if len(obs) == 0:
        raise ValueError("No valid data points after removing NaN values")

    # Calculate statistics with error handling
    try:
        # Nash-Sutcliffe Efficiency (NSE)
        denominator = numpy.sum((obs - numpy.mean(obs)) ** 2)
        nse = 1 - numpy.sum((obs - sim) ** 2) / denominator if denominator != 0 else numpy.nan

        # Kling-Gupta Efficiency (KGE) components
        r = numpy.corrcoef(obs, sim)[0, 1]
        obs_std = numpy.std(obs)
        sim_std = numpy.std(sim)
        obs_mean = numpy.mean(obs)
        sim_mean = numpy.mean(sim)
        
        alpha = sim_std / obs_std if obs_std != 0 else numpy.nan
        beta = sim_mean / obs_mean if obs_mean != 0 else numpy.nan
        
        # KGE calculation
        if not any(numpy.isnan([r, alpha, beta])):
            kge = 1 - numpy.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
        else:
            kge = numpy.nan

        # Percent Bias (PBIAS)
        pbias = 100 * numpy.sum(sim - obs) / numpy.sum(obs) if numpy.sum(obs) != 0 else numpy.nan

        # Log Nash-Sutcliffe Efficiency (LNSE)
        eps = 0.0001
        log_obs = numpy.log(obs + eps)
        log_sim = numpy.log(sim + eps)
        log_denominator = numpy.sum((log_obs - numpy.mean(log_obs)) ** 2)
        lnse = 1 - numpy.sum((log_obs - log_sim) ** 2) / log_denominator if log_denominator != 0 else numpy.nan

        # R-squared (R2)
        r2 = r ** 2 if not numpy.isnan(r) else numpy.nan

        # Root Mean Square Error (RMSE)
        rmse = numpy.sqrt(numpy.mean((obs - sim) ** 2))

        # Mean Absolute Error (MAE)
        mae = numpy.mean(numpy.abs(obs - sim))

        # Mean Square Error (MSE)
        mse = numpy.mean((obs - sim) ** 2)

        # Mean Absolute Percentage Error (MAPE)
        with numpy.errstate(divide='ignore', invalid='ignore'):
            mape = numpy.mean(numpy.abs((obs - sim) / obs) * 100)
            mape = numpy.nan if numpy.isinf(mape) else mape

    except Exception as e:
        print(f"Warning: Error in statistical calculations: {str(e)}")
        return {stat: numpy.nan for stat in ['NSE', 'KGE', 'PBIAS', 'LNSE', 'R2', 'RMSE', 'MAE', 'MSE', 'MAPE', 'alpha', 'beta']}

    return {
        'NSE': nse,
        'KGE': kge,
        'PBIAS': pbias,
        'LNSE': lnse,
        'R2': r2,
        'RMSE': rmse,
        'MAE': mae,
        'MSE': mse,
        'MAPE': mape,
        'alpha': alpha,
        'beta': beta
    }


def getNSE(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the NSE

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        NSE value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['NSE']

def getKGE(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the KGE

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        KGE value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['KGE']

def getPBIAS(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the PBIAS

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        PBIAS value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['PBIAS']


def getLNSE(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the LNSE

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        LNSE value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['LNSE']

def getR2(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the R2

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        R2 value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['R2']

def getRMSE(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the RMSE

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        RMSE value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['RMSE']

def getMAE(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the MAE

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        MAE value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['MAE']

def getMSE(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> float:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return the MSE

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: float
        MSE value
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats['MSE']

def getTimeseriesStats(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> dict:
    '''
    this function is a wrapper for calculateTimeseriesStats specifically to return all stats

    data: pandas.DataFrame
        DataFrame containing the timeseries data
    observed: str
        name of the observed column
    simulated: str
        name of the simulated column
    resample: str
        if specified, the data will be resampled to the specified frequency
        available options: 'H' (hourly), 'D' (daily), 'M' (monthly), 'Y' (yearly)

    return: dict
        dictionary containing all stats
    '''
    stats = calculateTimeseriesStats(data, observed, simulated, resample)

    return stats

ignoreWarnings()
