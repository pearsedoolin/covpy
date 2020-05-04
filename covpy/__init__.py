"""
This module allows for easy collection of data from the CDC.
The results are formatted in pandas, making them easier to view and analyze.

Todo:
    * Add 'per_capita' keyword
"""

import datetime
from urllib.error import HTTPError
from numpy import sort, unique
import pandas as pd

class DataCollector:
    """ The DataCollector class for getting covid19 data from the ECDC

        The data is stored in the instance of the class so
        that it is not downloaded multiple times.
    """

    def __init__(self):
        self._df = pd.DataFrame()
        self._df_date = None
        self._cases_df = None


    def __get_df__(self, lookback=7, force_new=False):
        """ Checks if data has already been downloaded for today's date, and
        if is has not been, it is downloaded.

        Args:
        lookback (int): The number of days to look back for data if today's
                        data is not available.

        force_new (bool): Force data to be redownloaded from the ECDC's website
        """
        today = datetime.date.today()

        if (force_new or (self._df.empty or self._df_date != today)):
            for _ in range(lookback):
                try:
                    day = today.strftime("%Y-%m-%d")
                    url = "https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-%s.xlsx"%day
                    self._df = pd.read_excel(url)
                    self._df_date = today
                except HTTPError:
                    today -= datetime.timedelta(days=1)

    def get_covid19_cases(self, cumulative=False, force_new=False):
        """Gets the confirmed cases data

        Args:
        cumulative (bool): Get the cumulative number of cases instead of the daily cases.
        force_new (bool): Force data to be redownloaded from the ECDC's website

        Returns:
        cases_df: Pandas dataframe containing the daily covid19 data for each country
                    since the outbreak began
        """

        self.__get_df__(force_new=force_new)
        days = sort(unique(self._df['DateRep']))
        cases_df = pd.DataFrame(index=days)

        for country in unique(self._df['Countries and territories']):
            country_df = self._df.loc[self._df['Countries and territories'] == country][['DateRep', 'Cases']]
            country_df = country_df.set_index('DateRep')

            #remove duplicate indexes
            country_df = country_df.groupby(country_df.index).agg({'Cases':sum})
            country_df = country_df.reindex(days, fill_value=0)
            if cumulative:
                cases_df[country] = country_df["Cases"].cumsum()
            else:
                cases_df[country] = country_df["Cases"]
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
        self.__get_df__(force_new=force_new)
        days = sort(unique(self._df['DateRep']))
        deaths_df = pd.DataFrame(index=days)

        for country in unique(self._df['Countries and territories']):
            country_df = self._df.loc[self._df['Countries and territories'] == country][['DateRep', 'Deaths']]
            country_df = country_df.set_index('DateRep')

            #remove duplicate indexes
            country_df = country_df.groupby(country_df.index).agg({'Deaths':sum})
            country_df = country_df.reindex(days, fill_value=0)
            if cumulative:
                deaths_df[country] = country_df["Deaths"].cumsum()
            else:
                deaths_df[country] = country_df["Deaths"]
        deaths_df["World"] = deaths_df[list(deaths_df)].sum(axis=1)

        return deaths_df
