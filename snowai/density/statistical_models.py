
"""
Created on Tue Jan  17 11:15 2024

This script contains codes to compute snow density using three statistical models:

    1. Sturm et al. (2010) - DOI: https://doi.org/10.1175/2010JHM1202.1
    2. Jonas et al. (2009) - DOI: https://doi.org/10.1016/j.jhydrol.2009.09.021
    3. Pistochi A. (2016) - DOI: https://doi.org/10.1016/j.ejrh.2016.03.004

Author: Ibrahim Alabi
Email: ibrahimolalekana@u.boisestate.edu
Institution: Boise State University
"""

## Import libraries
import datetime
import numpy as np
import pandas as pd
from ..utils.xgboost_utils import validate_DOY
from ..utils.jonas_model_utils import jonas_model_params, validate_month
from ..utils.sturm_model_utils import sturm_model_params, validate_snow_class, validate_SturmDOY



class SturmDensity:

    """
    A class for computing snow density using the Sturm Equation.
    """

    def __init__(self, return_type: str = 'numpy'):
        """Initialize the SturmDensity class."""
        
        self.return_type = return_type

    def rho(self, h: np.ndarray, doy: np.ndarray, rho_max: int, rho_0: int, k1: int, k2: int) -> np.ndarray:

        """
        A function to compute snow density using the Sturm Equation.

        Parameters:
        ===========
            * h (np.ndarray): The snow depth in cm.
            * doy (np.ndarray): The day of the year. See link to original paper in the preamble for more information on how to compute doy. 
            * rho_max (float): A constant in g/cm^3. See link to original paper in the preamble.
            * rho_0 (float): A constant in g/cm^3. See link to original paper in the preamble.
            * k1 (float): A constant. See link to original paper in the preamble.
            * k2 (float): A constant. See link to original paper in the preamble.

        Returns:
        ========
            * np.ndarray: The function returns the snow density in kg/m^3.
        """

        density_est = (rho_max - rho_0) * (1 - np.exp(-k1 * h - k2 * doy)) + rho_0
        return density_est

    def predict(
        self,
        data: pd.DataFrame, 
        snow_depth: str, 
        DOY: str, 
        snow_class: str
    ) -> float:

        """
        A function to compute snow density using the Sturm Equation.

        Parameters:
        ===========
            * data (pd.DataFrame): Input dataset containing the required columns.
            * snow_depth (str): Column name for snow depth in cm.
            * DOY (str): The column name for the day of the year.  See link to original paper in the preamble for more information on how to compute DOY. 
            * snow_class (str): The column name for the snow type. Must be one of 'alpine', 'maritime', 'prairie', 'tundra' or 'taiga'.

        Returns:
        ========
            * np.ndarray or pd.Series: The snow density in g/cm^3
        """


        # TODO: Remove the first check in the final package.

        if pd.isna(DOY):
            return np.nan

        snow_class = validate_snow_class(snow_class)
        DOY = validate_SturmDOY(DOY)

        if DOY is np.nan or snow_class is np.nan:
            return np.nan


        density = self.rho(
                h=snow_depth,
                doy=DOY,
                rho_max=sturm_model_params[snow_class]['rho_max'],
                rho_0=sturm_model_params[snow_class]['rho_0'],
                k1=sturm_model_params[snow_class]['k1'],
                k2=sturm_model_params[snow_class]['k2']
            )
        
        return density
    
class JonasDensity:

    """
    A class for computing snow density using the Jonas Model.
    """

    def __init__(self):
        pass

    def rho(self, h, a, b):

        """
        A function to compute snow density using the Jonas Model.

        Parameters:
        ===========
            * h (float): The snow depth in meters.
            * a (float): A constant.
            * b (float): A constant.

        Returns:
        ========
            * The function returns the snow density in kg/m^3.
        """

        density_est = (a * h) + b
        return density_est

    def predict(
        self, 
        snow_depth: float,
        month: str,
        elevation: float
    ) -> float:

        """
        A function to compute snow density using the Jonas Model.

        Parameters:
        ===========
            * snow_depth (float): The snow depth in meters.
            * month (str): The month. Must be one of 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov' or 'dec'.
            * elevation (float): The elevation in meters.

        Returns:
        ========
            * The function returns the snow density in g/cm^3.
        """
        
        if elevation < 1400:
            elevation_ = '<1400m'
        elif elevation >= 1400 and elevation < 2000:
            elevation_ = '[1400, 2000)m'
        else:
            elevation_ = '>=2000m'

        month = validate_month(month)

        a = jonas_model_params[month][elevation_]['a']
        b = jonas_model_params[month][elevation_]['b']

        if a is None or b is None:
            return np.nan

        else:
            density = self.rho(
                h=snow_depth,
                a=a,
                b=b
            )
    
        
        return density/1000
    
class PistochiDensity:

    def __init__(self):
        pass

    def predict(self, DOY: int | float | str | pd.Timestamp | datetime.datetime) -> float:

        """
        A function to compute snow density using the Pistochi Model.

        Parameters:
        ===========
            * DOY (int | float | str | pd.Timestamp | datetime.datetime): The day of the year.

        Returns:
        ========
            * The function returns the snow density in g/cm^3.
        """
        DOY = validate_DOY(DOY, origin=11)
        density_est = 200 + (DOY + 61)
        return density_est/1000    