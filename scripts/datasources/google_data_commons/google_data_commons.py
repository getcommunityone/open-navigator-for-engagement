"""
Google Data Commons Integration for Jurisdiction Enrichment

Uses Google Data Commons Knowledge Graph API to enrich jurisdiction data with:
- Demographics (population, age, gender, race/ethnicity)
- Economic indicators (income, employment, poverty)
- Education levels
- Health insurance coverage
- Housing characteristics

Installation:
    pip install datacommons datacommons-pandas

Documentation:
    https://docs.datacommons.org/api/
    https://datacommons.org/tools/statvar

Citation:
    Google LLC. Data Commons. https://datacommons.org/
"""
from typing import List, Dict, Any, Optional
import pandas as pd
from loguru import logger

try:
    import datacommons as dc
    import datacommons_pandas as dcpd
    DATACOMMONS_AVAILABLE = True
except ImportError:
    logger.warning("datacommons not installed. Run: pip install datacommons datacommons-pandas")
    DATACOMMONS_AVAILABLE = False


class DataCommonsClient:
    """
    Client for enriching jurisdiction data with Google Data Commons variables.
    
    Replaces manual U.S. Census API calls with simplified Data Commons API.
    """
    
    # Standard statistical variables for jurisdictions
    DEMOGRAPHIC_VARS = [
        "Count_Person",                                          # Total population
        "Count_Person_Male",                                     # Male population
        "Count_Person_Female",                                   # Female population
        "Median_Age_Person",                                     # Median age
        "Count_Person_WhiteAlone",                              # White population
        "Count_Person_BlackOrAfricanAmericanAlone",             # Black population
        "Count_Person_HispanicOrLatino",                        # Hispanic/Latino
        "Count_Person_AsianAlone",                              # Asian population
    ]
    
    ECONOMIC_VARS = [
        "Median_Income_Household",                              # Median household income
        "UnemploymentRate_Person",                              # Unemployment rate
        "Count_Person_BelowPovertyLevelInThePast12Months",     # Poverty count
        "Median_Earnings_Person",                               # Median earnings
    ]
    
    EDUCATION_VARS = [
        "Count_Person_EducationalAttainmentBachelorsDegreeOrHigher",  # College graduates
        "Count_Person_EducationalAttainmentHighSchoolGraduateOrHigher",  # HS graduates
    ]
    
    HEALTH_VARS = [
        "Count_Person_WithHealthInsurance",                     # Insured population
        "Count_Person_NoHealthInsurance",                       # Uninsured population
    ]
    
    HOUSING_VARS = [
        "Median_Price_SoldHome",                                # Median home price
        "Count_HousingUnit",                                    # Total housing units
        "Count_Household",                                      # Total households
    ]
    
    ALL_VARS = (
        DEMOGRAPHIC_VARS + 
        ECONOMIC_VARS + 
        EDUCATION_VARS + 
        HEALTH_VARS + 
        HOUSING_VARS
    )
    
    def __init__(self):
        """Initialize the Data Commons client."""
        if not DATACOMMONS_AVAILABLE:
            raise ImportError(
                "datacommons package not installed. "
                "Install with: pip install datacommons datacommons-pandas"
            )
    
    def get_place_dcid(self, fips_code: str, place_type: str = "County") -> str:
        """
        Convert FIPS code to Data Commons ID (DCID).
        
        Args:
            fips_code: 5-digit FIPS code (state+county) or 7-digit (state+place)
            place_type: "County" or "City"
        
        Returns:
            DCID like "geoId/01073" for Jefferson County, AL
        
        Examples:
            >>> client = DataCommonsClient()
            >>> client.get_place_dcid("01073", "County")
            'geoId/01073'
            >>> client.get_place_dcid("0107000", "City")  # Birmingham, AL
            'geoId/0107000'
        """
        return f"geoId/{fips_code}"
    
    def enrich_jurisdiction(
        self,
        fips_code: str,
        variables: Optional[List[str]] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Enrich a jurisdiction with Data Commons variables.
        
        Args:
            fips_code: 5-digit (county) or 7-digit (city) FIPS code
            variables: List of statistical variables (default: ALL_VARS)
            year: Optional year filter (default: most recent)
        
        Returns:
            Dictionary of {variable: value}
        
        Example:
            >>> client = DataCommonsClient()
            >>> data = client.enrich_jurisdiction("01073")  # Jefferson County, AL
            >>> print(data["Median_Income_Household"])
            65000
        """
        if variables is None:
            variables = self.ALL_VARS
        
        dcid = self.get_place_dcid(fips_code)
        
        try:
            # Get latest observation for each variable
            observations = dc.get_stat_value(dcid, variables)
            
            result = {
                "fips_code": fips_code,
                "dcid": dcid,
                "data_source": "Google Data Commons",
                "retrieval_date": pd.Timestamp.now().isoformat(),
            }
            
            # Add statistical variables
            for var in variables:
                result[var] = observations.get(var)
            
            return result
            
        except Exception as e:
            logger.error(f"Error enriching {fips_code}: {e}")
            return {"fips_code": fips_code, "error": str(e)}
    
    def enrich_jurisdictions_bulk(
        self,
        fips_codes: List[str],
        variables: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Enrich multiple jurisdictions in bulk.
        
        Args:
            fips_codes: List of FIPS codes
            variables: List of statistical variables
        
        Returns:
            DataFrame with one row per jurisdiction
        
        Example:
            >>> client = DataCommonsClient()
            >>> fips_codes = ["01073", "01089", "01097"]  # 3 AL counties
            >>> df = client.enrich_jurisdictions_bulk(fips_codes)
            >>> print(df[["fips_code", "Count_Person", "Median_Income_Household"]])
        """
        if variables is None:
            variables = self.ALL_VARS
        
        dcids = [self.get_place_dcid(fips) for fips in fips_codes]
        
        try:
            # Use datacommons_pandas for efficient bulk retrieval
            df = dcpd.build_multivariate(
                dcids=dcids,
                stat_vars=variables
            )
            
            # Add FIPS codes
            df["fips_code"] = fips_codes
            df["data_source"] = "Google Data Commons"
            df["retrieval_date"] = pd.Timestamp.now().isoformat()
            
            return df
            
        except Exception as e:
            logger.error(f"Error enriching bulk jurisdictions: {e}")
            return pd.DataFrame({"error": [str(e)]})
    
    def get_time_series(
        self,
        fips_code: str,
        variables: Optional[List[str]] = None,
        start_year: int = 2010,
        end_year: int = 2023
    ) -> pd.DataFrame:
        """
        Get time series data for a jurisdiction.
        
        Args:
            fips_code: FIPS code
            variables: Statistical variables (default: economic indicators)
            start_year: Start year
            end_year: End year
        
        Returns:
            DataFrame with time series (date index)
        
        Example:
            >>> client = DataCommonsClient()
            >>> df = client.get_time_series("01073", start_year=2015)
            >>> df.plot(y="Median_Income_Household")
        """
        if variables is None:
            variables = self.ECONOMIC_VARS
        
        dcid = self.get_place_dcid(fips_code)
        
        try:
            df = dcpd.build_time_series(
                place=dcid,
                stat_vars=variables
            )
            
            # Filter by year range
            df = df.loc[f"{start_year}":f"{end_year}"]
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting time series for {fips_code}: {e}")
            return pd.DataFrame({"error": [str(e)]})
    
    def search_variables(self, query: str) -> List[Dict[str, str]]:
        """
        Search for available statistical variables.
        
        Args:
            query: Search query (e.g., "income", "education", "health")
        
        Returns:
            List of {dcid, name, description}
        
        Example:
            >>> client = DataCommonsClient()
            >>> vars = client.search_variables("dental health")
            >>> for v in vars:
            ...     print(v["dcid"], v["name"])
        """
        try:
            results = dc.search_statvar(query, max_results=50)
            return [
                {
                    "dcid": r.dcid,
                    "name": getattr(r, 'name', r.dcid),
                    "description": getattr(r, 'description', '')
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching variables: {e}")
            return []


def example_usage():
    """Example usage of Data Commons integration."""
    client = DataCommonsClient()
    
    # Example 1: Enrich a single county
    print("Example 1: Jefferson County, AL (FIPS 01073)")
    data = client.enrich_jurisdiction("01073")
    print(f"Population: {data.get('Count_Person')}")
    print(f"Median Income: ${data.get('Median_Income_Household')}")
    print(f"Unemployment Rate: {data.get('UnemploymentRate_Person')}%")
    print()
    
    # Example 2: Bulk enrich multiple counties
    print("Example 2: Top 3 AL counties by population")
    fips_codes = ["01073", "01089", "01097"]  # Jefferson, Madison, Mobile
    df = client.enrich_jurisdictions_bulk(fips_codes)
    print(df[["fips_code", "Count_Person", "Median_Income_Household"]])
    print()
    
    # Example 3: Time series
    print("Example 3: Income trends for Birmingham, AL")
    df_ts = client.get_time_series(
        "0107000",  # Birmingham city
        variables=["Median_Income_Household"],
        start_year=2015
    )
    print(df_ts)
    print()
    
    # Example 4: Search for dental health variables
    print("Example 4: Search for dental health variables")
    vars = client.search_variables("dental health")
    for v in vars[:5]:
        print(f"  - {v['dcid']}: {v['name']}")


if __name__ == "__main__":
    if DATACOMMONS_AVAILABLE:
        example_usage()
    else:
        print("Install datacommons: pip install datacommons datacommons-pandas")
