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
from osgeo import gdal



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
    '''
    return os.path.splitext(filePath)[1]


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
                print(f"\t> Moving file \n\t - {src_file}\n\t - to {dest_file}")
            shutil.move(src_file, dest_file)

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


def getFileBaseName(filePath:str, extension:bool = False) -> str:
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
    with open(source, 'rb') as src:
        with open(destination, 'wb') as dest: dest.write(src.read())
    
    if v: print(f'> {source} copied to \t - {destination}')


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
    if count == end: print()



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

ignoreWarnings()
