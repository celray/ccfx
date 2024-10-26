#!/bin/python3

'''
a module to easily create microsoft excel documents from python

Author  : Celray James CHAWANDA
Email   : celray.chawanda@outlook.com
Licence : MIT 2023
Repo    : https://github.com/celray

Date    : 2023-07-20
'''

# imports

import os
import platform
import xml.etree.ElementTree as ET
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

# classes
class excel:
    def __init__(self, path):
        self.path = path
        self.sheet_names = {}
        self.book = None
        self.chart_names = []
        self.date_format = None

    def create(self):
        self.create_path(os.path.dirname(self.path))
        self.book = xlsxwriter.Workbook(self.path)

    def addSheet(self, sheet_name):
        if self.book is None:
            self.create()
        self.sheet_names[sheet_name] = self.book.add_worksheet(sheet_name)

    def setDateFormat(self, format_string='dd/mm/yyyy'):
        self.date_format = self.book.add_format({'num_format': format_string})

    def writeDate(self, sheet_name, row, column, datetime_obj):
        if self.date_format is None:
            self.set_date_format()
            
        self.sheet_names[sheet_name].write_datetime(
            row, column, datetime_obj, self.date_format)

    def write(self, sheet_name, row, column, value):
        self.sheet_names[sheet_name].write(row, column, value)

    def setColumnWidth(self, sheet_name, column_names, width=12):
        '''
        column_names: list
        '''
        if isinstance(column_names, str):
            self.sheet_names[sheet_name].set_column(
                "{col}:{col}".format(col=column_names), width)
        else:
            for column in column_names:
                self.sheet_names[sheet_name].set_column(
                    "{col}:{col}".format(col=column), width)

    def addFigure(self, sheet_name, x_src_sheet_name, x_start, x_end, y_src_sheet_name, y_start, y_end, position_cell="E2", chart_type='subtype',
                subtype='straight', title='-', size = [1, 1], width = 720, height = 576, marker_type = 'automatic', x_axis_name = "", y_axis_name = "",
                gridlines_visible = False, xmin = 0, ymin = 0, xmax = None, ymax = None):
        '''
        x_start example : "E3"
        marker_type     : automatic, none, square, diamond, triangle, x, star, short_dash, long_dash, circle, plus
        '''
        chart = self.book.add_chart({'type': 'scatter', })
        chart.set_size({'width': width, 'height': height})
        # axis options
        chart.set_x_axis({
            'name': x_axis_name,
            'min': xmin, 'max': xmax,
            'major_gridlines': {
                    'visible': gridlines_visible,
                },
        })

        chart.set_y_axis({
            'name': y_axis_name,
            'min': ymin, 'max': ymax,
            'major_gridlines': {
                    'visible': gridlines_visible,
                },
        })


        self.sheet_names[sheet_name].insert_chart(
            position_cell, chart, {'x_scale': size[1], 'y_scale': size[0]})
        chart.add_series({
            'categories': '={sht}!{strt_x}:{end_x}'.format(sht=x_src_sheet_name, strt_x=x_start, end_x=x_end),
            'values': '={sht}!{strt_y}:{end_y}'.format(sht=y_src_sheet_name, strt_y=y_start, end_y=y_end),
            'name': title,
            'marker': {'type': marker_type},
            # 'trendline': {'type': 'linear'},
        })
        chart.set_legend({'position': 'bottom'})

    def writeColumn(self, sheet_name, target_cell, content_list):
        '''target_cell eg = A1'''
        self.sheet_names[sheet_name].write_column(target_cell, content_list)

    def getPlatform():
        """Returns: Windows or Linux"""
        return platform.system()


    def open(self):
        if self.getPlatform() == "Windows":
            os.startfile(os.path.abspath(self.path))
        else:
            os.system(f"open {self.path}")

    def toAlphaNumeric(self, row, column):
        return xl_rowcol_to_cell(row, column)

    def save(self):
        continue_ = True
        while continue_:
            try:
                self.book.close()
                continue_ = False
            except:
                print("\t! Error writing the Excel file, make sure it is closed")
                answer = input("\t> retry? (y/n): ")
                continue_ = True if answer == "y" else False


    def createPath(self, path_name, v = False):
        path_name = os.path.dirname(path_name)
        if path_name == '':
            path_name = './'
        if not os.path.isdir(path_name):
            os.makedirs(path_name)
            if v:
                print(f"\t> created path: {path_name}")
        
        return path_name

