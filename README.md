# ccfx

`ccfx` is a comprehensive Python package designed to streamline file and data management, geospatial analysis, and NetCDF file processing for quick prototyping. The library provides versatile tools for file handling, raster and vector manipulation, database connectivity, and data export for geospatial and scientific computing projects.

## Features

1. **File Management**:
   - List, delete, move, and count files within directories.
   - Monitor file count over time in a specific directory.
   - Save, load, and manage Python variables via pickle serialization.

2. **Geospatial Data Processing**:
   - Read, write, and manage raster and vector geospatial data.
   - Clip rasters by bounding boxes and extract raster values at specified coordinates.
   - Create grids of polygons based on shapefile boundaries with user-defined resolutions.
   - Convert coordinates between coordinate reference systems (CRS).
   - Write NumPy arrays to GeoTIFF files with projection and geotransform settings.

3. **NetCDF File Handling**:
   - List available variables and dimensions in NetCDF files.
   - Export NetCDF variables to GeoTIFF format.
   - Calculate sum and average maps from NetCDF data across multiple files.

4. **Database Connectivity**:
   - Access and interact with databases using ODBC and SQLAlchemy for flexible database management.
   - Connect to both SQL Server and SQLite databases.

5. **Progress Tracking and System Info**:
   - Display dynamic progress bars for long-running operations.
   - Check the system’s platform information.
   - Enable or disable warnings programmatically.

6. **Excel and Word File Handling**:
   - Create and modify Excel files using xlsxwriter.
   - Generate Word documents with advanced formatting options using python-docx.

## Installation

Install `ccfx` via pip:
```bash
pip install ccfx
```

## Dependencies

`ccfx` relies on the following libraries:

- **netCDF4**: For working with NetCDF files.
- **gdal**: Required for geospatial raster data manipulation.
- **numpy**: For array processing and numerical operations.
- **pandas**: For data manipulation and analysis.
- **shapely**: Provides geometric operations for spatial data.
- **geopandas**: Extends pandas to handle geospatial data.
- **xlsxwriter**: For creating and writing Excel files.
- **pyodbc**: Enables connectivity to databases through ODBC.
- **sqlalchemy**: Provides SQL toolkit and ORM features for database access.
- **python-docx**: Enables creation and manipulation of Word documents.

These dependencies will be installed automatically when `ccfx` is installed.

## API Reference

### `listFiles(path: str, ext: str = None) -> list`
Lists all files in a directory with a specified extension.

- **Parameters**:
  - `path` (str): The directory to search.
  - `ext` (str, optional): File extension to filter by, e.g., `'txt'`, `'.txt'`, `'*txt'`, or `'*.txt'`.

- **Returns**:
  - `list`: A list of file paths matching the criteria.

### `deleteFile(filePath: str, v: bool = False) -> bool`
Deletes a specified file with optional verbose output.

- **Parameters**:
  - `filePath` (str): Path to the file to be deleted.
  - `v` (bool, optional): If `True`, prints a confirmation message. Defaults to `False`.

- **Returns**:
  - `bool`: `True` if deletion was successful; `False` otherwise.

### `createGrid(shapefile_path: str, resolution: float, useDegree: bool = True) -> tuple`
Generates a grid of polygons from a shapefile at a given resolution.

- **Parameters**:
  - `shapefile_path` (str): Path to the shapefile.
  - `resolution` (float): Resolution of the grid.
  - `useDegree` (bool, optional): If `True`, coordinates are in degrees. Defaults to `True`.

- **Returns**:
  - `tuple`: Contains grid coordinates and metadata.

### `clipRasterByExtent(inFile: str, outFile: str, bounds: tuple) -> str`
Clips a raster to specified bounding box coordinates.

- **Parameters**:
  - `inFile` (str): Path to the input raster file.
  - `outFile` (str): Path to the output clipped raster file.
  - `bounds` (tuple): Bounding box as `(minx, miny, maxx, maxy)`.

- **Returns**:
  - `str`: Path to the clipped raster file.

### `netcdfVariablesList(ncFile: str) -> list`
Lists all variables in a NetCDF file.

- **Parameters**:
  - `ncFile` (str): Path to the NetCDF file.

- **Returns**:
  - `list`: A list of variable names in the file.

### ... And More ...

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License.
