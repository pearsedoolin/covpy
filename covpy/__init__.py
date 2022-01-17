"""
This module allows for easy collection of data from the CDC.
The results are formatted in pandas, making them easier to view and analyze.

Todo:
    * Add 'per_capita' keyword
"""

import datetime
from numpy import sort, unique
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


class DataCollector:
    """ The DataCollector class for getting covid19 data from the ECDC

        The data is stored in the instance of the class so
        that it is not downloaded multiple times.
    """

    def __init__(self):
        self._df = pd.DataFrame()
        self._df_date = None
        self._cases_df = None


    def _get_df(self, force_new=False):
        """ Checks if data has already been downloaded for today's date, and
        if is has not been, it is downloaded.

        Args:
        lookback (int): The number of days to look back for data if today's
                        data is not available.

        force_new (bool): Force data to be redownloaded from the ECDC's website
        """
        today = datetime.date.today()

        if (force_new or self._df.empty or self._df_date != today):
            url = "https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide.xlsx"
            self._df = pd.read_excel(url)
            self._df_date = today


    def get_covid19_cases(self, cumulative=False, force_new=False):
        """Gets the confirmed cases data

        Args:
        cumulative (bool): Get the cumulative number of cases instead of the daily cases.
        force_new (bool): Force data to be redownloaded from the ECDC's website

        Returns:
        cases_df: Pandas dataframe containing the daily covid19 data for each country
                    since the outbreak began
        """

        self._get_df(force_new=force_new)
        days = sort(unique(self._df['dateRep']))
        cases_df = pd.DataFrame(index=days)

        for country in unique(self._df['countriesAndTerritories']):
            country_df = self._df.loc[self._df['countriesAndTerritories'] == country][['dateRep', 'cases']]
            country_df = country_df.set_index('dateRep')

            #remove duplicate indexes
            country_df = country_df.groupby(country_df.index).agg({'cases':sum})
            country_df = country_df.reindex(days, fill_value=0)

            if cumulative:
                cases_df[country] = country_df["cases"].cumsum()
            else:
                cases_df[country] = country_df["cases"]
        cases_df["World"] = cases_df[list(cases_df)].sum(axis=1)
        return cases_df

    def get_covid19_deaths(self, cumulative=False, force_new=False):
        """Gets the confirmed deaths data

        Args:
        cumulative (bool): Get the cumulative number of deaths instead of the daily deaths.
        force_new (bool): Force data to be redownloaded from the ECDC's website

        Returns:
        cases_df: Pandas dataframe containing the daily covid19 deaths for each country
                    since the outbreak began
        """
        self._get_df(force_new=force_new)
        days = sort(unique(self._df['dateRep']))
        deaths_df = pd.DataFrame(index=days)

        for country in unique(self._df['countriesAndTerritories']):
            country_df = self._df.loc[self._df['countriesAndTerritories'] == country][['dateRep', 'deaths']]
            country_df = country_df.set_index('dateRep')

            #remove duplicate indexes
            country_df = country_df.groupby(country_df.index).agg({'deaths':sum})
            country_df = country_df.reindex(days, fill_value=0)
            if cumulative:
                deaths_df[country] = country_df["deaths"].cumsum()
            else:
                deaths_df[country] = country_df["deaths"]
        deaths_df["World"] = deaths_df[list(deaths_df)].sum(axis=1)

        return deaths_df
