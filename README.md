# ccfx

`ccfx` is a comprehensive Python package designed to streamline file and data management, geospatial analysis, NetCDF file processing, database interactions, document generation, and multimedia handling for rapid prototyping and development workflows.

## Features

1.  **File Management**:
    *   List, delete, move, copy, and count files/directories.
    *   Monitor file count over time.
    *   Save, load, and manage Python variables via pickle serialization.
    *   Compress directories to `.7z` archives.
    *   Read/write text files with encoding support.
    *   Download files from URLs with resume and multi-connection support.

2.  **Geospatial Data Processing**:
    *   Read, write, clip (by extent/feature), resample, reproject, merge, and rasterize raster data (GeoTIFF, NetCDF).
    *   Read, write, and clip vector data (Shapefile, GeoPackage).
    *   Create grids of polygons based on shapefile boundaries.
    *   Convert coordinates between Coordinate Reference Systems (CRS).
    *   Extract raster values at specific coordinates.
    *   Convert point lists to GeoDataFrames.
    *   Get vector layer bounds.

3.  **NetCDF File Handling**:
    *   List variables and dimensions.
    *   Export NetCDF variables to GeoTIFF format (single or multiple bands).
    *   Calculate sum and average maps from NetCDF data across multiple files.
    *   Rename variables using CDO (if available).

4.  **Database Connectivity**:
    *   **MS SQL Server**: Connect, list databases/tables, read tables (including spatial data into GeoDataFrames), write DataFrames/GeoDataFrames to tables, drop tables.
    *   **SQLite**: Connect, create/rename/drop tables, read tables (as dict, specific columns), insert data (rows, dicts, partial dicts), update values, dump tables to CSV.

5.  **Document & Spreadsheet Handling**:
    *   **Excel**: Create `.xlsx` files, add sheets, write data (including dates), set column widths, add scatter plot charts.
    *   **Word**: Create `.docx` files, add headings, paragraphs (with alignment), list items, formatted text (bold/italic), images, page breaks, set margins.

6.  **Multimedia & Web**:
    *   Read and write MP3 metadata (ID3 tags), including album art.
    *   Download videos/audio from YouTube using `yt-dlp`.

7.  **Data Analysis & Utilities**:
    *   Calculate timeseries statistics (NSE, KGE, PBIAS, LNSE, R2, RMSE, MAE, MSE, MAPE, alpha, beta) with resampling options.
    *   Display dynamic progress bars.
    *   Check system platform information.
    *   Enable or disable warnings programmatically.
    *   Set the working directory.

## Installation

Install `ccfx` via pip:
```bash
pip install ccfx
```

## Dependencies

`ccfx` relies on the following libraries:

*   **gdal**: For geospatial raster and vector data manipulation.
*   **numpy**: For array processing and numerical operations.
*   **pandas**: For data manipulation and analysis.
*   **geopandas**: Extends pandas to handle geospatial vector data.
*   **shapely**: Provides geometric objects and operations.
*   **netCDF4**: For working with NetCDF files.
*   **xlsxwriter**: For creating and writing Excel `.xlsx` files.
*   **python-docx**: Enables creation and manipulation of Word `.docx` documents.
*   **pyodbc**: Enables connectivity to databases through ODBC (e.g., MS SQL Server).
*   **sqlalchemy**: Provides SQL toolkit and ORM features for database access (used with MS SQL).
*   **py7zr**: For creating `.7z` archives.
*   **mutagen**: For reading and writing MP3 metadata (ID3 tags).
*   **requests**: For downloading files via HTTP.
*   **tqdm**: For displaying progress bars.
*   **yt-dlp**: For downloading YouTube content.
*   **matplotlib** (Optional, often used with geospatial/data analysis): For plotting.

These dependencies should be installed automatically when `ccfx` is installed via pip, but GDAL might require manual installation steps depending on your OS.

## API Reference (Selected Functions)

### File Management (`ccfx.py`)

*   **`listFiles(path: str, ext: str = None) -> list`**: Lists files in a directory, optionally filtering by extension.
*   **`deleteFile(filePath: str, v: bool = False) -> bool`**: Deletes a specified file.
*   **`deletePath(path: str, v: bool = False) -> bool`**: Deletes a directory and its contents.
*   **`createPath(pathName, v = False)`**: Creates a directory path if it doesn't exist.
*   **`copyFile(source: str, destination: str, v: bool = True)`**: Copies a single file.
*   **`copyDirectory(source: str, destination: str, recursive=True, v=True, filter=[])`**: Copies a directory's contents.
*   **`moveDirectoryFiles(srcDir: str, destDir: str, v: bool = False) -> bool`**: Moves files and subdirectories from source to destination.
*   **`pythonVariable(filename, option, variable=None)`**: Saves ('dump') or loads ('load') Python variables using pickle.
*   **`compressTo7z(input_dir: str, output_file: str)`**: Compresses a directory into a .7z file.
*   **`downloadFile(url, save_path, exists_action='resume', num_connections=5, v=False)`**: Downloads a file from a URL with advanced options.
*   **`listAllFiles(folder, extension="*")`**: Recursively lists all files in a folder and its subfolders.

### Geospatial (`ccfx.py`)

*   **`createGrid(shapefile_path: str, resolution: float, useDegree: bool = True) -> tuple`**: Generates a grid of polygons based on a shapefile extent.
*   **`clipRasterByExtent(inFile: str, outFile: str, bounds: tuple) -> str`**: Clips a raster using bounding box coordinates.
*   **`clipVectorByExtent(inFile: str, outFile: str, bounds: tuple) -> str`**: Clips a vector file using bounding box coordinates.
*   **`clipFeatures(inputFeaturePath:str, boundaryFeature:str, outputFeature:str, keepOnlyTypes = None, v = False) -> geopandas.GeoDataFrame`**: Clips input features by a boundary feature.
*   **`resampleRaster(inFile:str, outFile:str, resolution:float, dstSRS = None, resamplingMethod = 'bilinear', replaceOutput:bool = True, v:bool = True) -> str`**: Resamples a raster to a new resolution and optionally CRS.
*   **`reprojectRaster(inFile: str, outFile: str, dstProjection: str, resamplingMethod: str = 'mode') -> str`**: Reprojects a raster to a new CRS.
*   **`mergeRasterTiles(tileList:list, outFile:str) -> str`**: Merges multiple raster files into one.
*   **`rasterizeRaster(inFile: str, outFile: str, targetField: str, targetResolution: float) -> str`**: Rasterizes a vector layer based on an attribute field.
*   **`extractRasterValue(rasterPath: str, lat: float, lon: float, coordProj: str = 'EPSG:4326') -> float`**: Extracts the raster value at a specific point.
*   **`convertCoordinates(lon, lat, srcEPSG, dstCRS) -> tuple`**: Converts coordinates between CRSs.
*   **`tiffWriteArray(array: numpy.ndarray, outputFile: str, geoTransform: tuple, projection: str, noData:float = None, v:bool = False) -> gdal.Dataset`**: Writes a NumPy array to a GeoTIFF file.
*   **`pointsToGeodataframe(point_pairs_list, columns = ['latitude', 'longitude'], auth = "EPSG", code = '4326', out_shape = '', format = 'gpkg', v = False, get_geometry_only = False)`**: Converts a list of point coordinates to a GeoDataFrame.

### NetCDF (`ccfx.py`)

*   **`netcdfVariablesList(ncFile: str) -> list`**: Lists variables in a NetCDF file.
*   **`netcdfVariableDimensions(ncFile: str, variable: str) -> dict`**: Gets dimensions and their sizes for a NetCDF variable.
*   **`netcdfExportTif(ncFile: str, variable: str, outputFile: str = None, band: int = None, v:bool = True) -> gdal.Dataset`**: Exports a NetCDF variable (optionally a specific band) to GeoTIFF.
*   **`netcdfAverageMap(ncFiles:list, variable:str, band:int = 1) -> numpy.ndarray`**: Calculates the average map from a variable across multiple NetCDF files.
*   **`netcdfSumMaps(ncFiles:list, variable:str, band:int = 1) -> numpy.ndarray`**: Calculates the sum map from a variable across multiple NetCDF files.
*   **`renameNetCDFvariable(input_file: str, output_file: str, old_var_name: str, new_var_name: str, v = False)`**: Renames a variable in a NetCDF file using CDO.

### Database (`mssqlConnection.py`, `sqliteConnection.py`)

*   **`mssql_connection(server, username, password, driver, ...)`**: Class for MS SQL Server interactions.
    *   `connect()`, `listDatabases()`, `listTables()`, `readTable()`, `connectDB()`, `dataframeToSql()`, `dropTable()`, `close()`
*   **`sqliteConnection(sqlite_database, connect=False)`**: Class for SQLite interactions.
    *   `connect()`, `createTable()`, `renameTable()`, `deleteTable()`, `readTableAsDict()`, `insertDict()`, `insertRow()`, `updateValue()`, `dumpCSV()`, `commitChanges()`, `closeConnection()`

### Document/Spreadsheet (`word.py`, `excel.py`)

*   **`word_document(path)`**: Class for creating Word documents.
    *   `addHeading()`, `addParagraph()`, `addListItem()`, `addText()`, `addImage()`, `addPageBreak()`, `setMargins()`, `save()`
*   **`excel(path)`**: Class for creating Excel spreadsheets.
    *   `create()`, `addSheet()`, `write()`, `writeDate()`, `setColumnWidth()`, `addFigure()`, `writeColumn()`, `save()`, `open()`

### Multimedia & Web (`ccfx.py`)

*   **`getMp3Metadata(fn, imagePath=None)`**: Extracts ID3 metadata from an MP3 file.
*   **`setMp3Metadata(fn, metadata, imagePath=None)`**: Writes ID3 metadata (including album art) to an MP3 file.
*   **`downloadYoutubeVideo(url: str, dstDir: str, audioOnly: bool = False, dstFileName: Optional[str] = None ) -> str`**: Downloads video or audio from a YouTube URL.

### Data Analysis & Utilities (`ccfx.py`)

*   **`calculateTimeseriesStats(data:pandas.DataFrame, observed:str = None, simulated:str = None, resample:str = None ) -> dict`**: Calculates various statistics between observed and simulated timeseries. (Wrappers like `getNSE`, `getKGE`, etc., are also available).
*   **`progressBar(count, total, message="")`**: Displays a simple console progress bar.
*   **`showProgress(count: int, end: int, message: str, barLength: int = 100)`**: Displays a more detailed console progress bar.
*   **`ignoreWarnings(ignore:bool = True, v:bool = False)`**: Suppresses or enables Python warnings.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. Ensure code is well-documented and includes tests where applicable.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
