/*
 * ER/Studio Data Architect SQL Code Generation
 * Project :      NOHDP_Oral_Health_Schema_Databricks_Std_Naming_Key_TypeApplied.DM1
 *
 * Date Created : Wednesday, April 22, 2026 07:19:07
 * Target DBMS : Databricks
 */

/* 
 * TABLE: dim_data_source 
 */

CREATE TABLE dim_data_source
(
    source_key                   string         NOT NULL,
    data_steward_desc            string,
    data_steward_code            string,
    dataset_desc                 string,
    dataset_code                 string,
    collection_mode_type         string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_data_source PRIMARY KEY (source_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_date 
 */

CREATE TABLE dim_date
(
    date_key              int          NOT NULL,
    full_date             date         NOT NULL,
    day_of_month          int,
    day_of_week           int,
    day_of_week_name      string,
    is_weekend            boolean,
    week_of_year          int,
    iso_week              string,
    month_number          int,
    month_name            string,
    month_abbr            string,
    year_month            int,
    year_month_name       string,
    quarter_number        int,
    quarter_name          string,
    year                  int,
    fiscal_year           int,
    fiscal_quarter        int,
    fiscal_month          int,
    is_holiday            boolean     DEFAULT FALSE,
    holiday_name          string,
    is_pilot_period       boolean     DEFAULT FALSE,
    is_baseline_period    boolean     DEFAULT FALSE,
    CONSTRAINT dim_date_pk PRIMARY KEY (date_key) 
)
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'supported')
;

/* 
 * TABLE: dim_geography 
 */

CREATE TABLE dim_geography
(
    geography_key                string         NOT NULL,
    geo_type                     string,
    fips_code                    string,
    geo_name_desc                string,
    county_name_desc             string,
    record_start_dttm            timestamp,
    record_end_dttm              timestamp,
    current_record_ind           smallint,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_geography PRIMARY KEY (geography_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_measure 
 */

CREATE TABLE dim_measure
(
    measure_key                   string         NOT NULL,
    source_key                    string,
    measure_code                  string,
    measure_desc                  string,
    measure_long_desc             string,
    measure_category_type         string,
    measure_level_type            string,
    measure_tooltip_desc          string,
    base_unit_desc                string,
    unit_prefix_code              string,
    unit_suffix_code              string,
    nohss_indicator_nbr           string,
    nohss_indicator_group_type    string,
    nohss_indicator_desc          string,
    dashboard_trend_ind           boolean,
    dashboard_cross_ind           boolean,
    record_start_dttm             timestamp,
    record_end_dttm               timestamp,
    current_record_ind            smallint,
    record_created_dttm           timestamp,
    record_last_modified_dttm     timestamp,
    load_run_id                   bigint,
    CONSTRAINT pk_dim_measure PRIMARY KEY (measure_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_postal 
 */

CREATE TABLE dim_postal
(
    postal_key                   string         NOT NULL,
    postal_code                  string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_postal PRIMARY KEY (postal_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_state 
 */

CREATE TABLE dim_state
(
    state_key                    string         NOT NULL,
    state_fips_nbr               int,
    state_name_desc              string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_state PRIMARY KEY (state_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_statistic_type 
 */

CREATE TABLE dim_statistic_type
(
    statistic_key                string         NOT NULL,
    statistic_type               string,
    calculation_method_desc      string,
    adjustment_desc              string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_statistic_type PRIMARY KEY (statistic_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_stratification 
 */

CREATE TABLE dim_stratification
(
    stratification_key              string         NOT NULL,
    stratification_category_type    string,
    stratification_level_desc       string,
    stratification_group_type       string,
    record_created_dttm             timestamp,
    record_last_modified_dttm       timestamp,
    load_run_id                     bigint,
    CONSTRAINT pk_dim_stratification PRIMARY KEY (stratification_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_survey_period 
 */

CREATE TABLE dim_survey_period
(
    survey_period_key            string         NOT NULL,
    date_type                    string,
    year_nbr                     int,
    year_start_nbr               int,
    year_end_nbr                 int,
    approx_date                  date,
    duration_desc                string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_survey_period PRIMARY KEY (survey_period_key) NOT ENFORCED 
)
;

/* 
 * TABLE: fact_oral_health_observation 
 */

CREATE TABLE fact_oral_health_observation
(
    observation_key              string              NOT NULL,
    measure_key                  string,
    geography_key                string,
    stratification_key           string,
    statistic_key                string,
    postal_key                   string              NOT NULL,
    state_key                    string              NOT NULL,
    survey_period_key            string              NOT NULL,
    date_key                     int                 NOT NULL,
    population_desc              string,
    value_nbr                    decimal(18, 6),
    ci_present_ind               boolean,
    ci_lower_nbr                 decimal(18, 6),
    ci_upper_nbr                 decimal(18, 6),
    proportion_nbr               decimal(18, 6),
    prop_lower_ci_nbr            decimal(18, 6),
    prop_upper_ci_nbr            decimal(18, 6),
    cell_size_unweighted_nbr     int,
    direction_desc               string,
    source_row_id_nbr            bigint,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_fact_oral_health PRIMARY KEY (observation_key) NOT ENFORCED 
)
;

/* 
 * TABLE: dim_measure 
 */

ALTER TABLE dim_measure ADD CONSTRAINT fk_measure_source 
    FOREIGN KEY (source_key)
    REFERENCES dim_data_source  NOT ENFORCED
;


/* 
 * TABLE: fact_oral_health_observation 
 */

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT Refdim_postal11 
    FOREIGN KEY (postal_key)
    REFERENCES dim_postal
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT Refdim_state12 
    FOREIGN KEY (state_key)
    REFERENCES dim_state
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT Refdim_survey_period14 
    FOREIGN KEY (survey_period_key)
    REFERENCES dim_survey_period
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT Refdim_date15 
    FOREIGN KEY (date_key)
    REFERENCES dim_date
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT fk_fact_geography 
    FOREIGN KEY (geography_key)
    REFERENCES dim_geography  NOT ENFORCED
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT fk_fact_measure 
    FOREIGN KEY (measure_key)
    REFERENCES dim_measure  NOT ENFORCED
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT fk_fact_statistic 
    FOREIGN KEY (statistic_key)
    REFERENCES dim_statistic_type  NOT ENFORCED
;

ALTER TABLE fact_oral_health_observation ADD CONSTRAINT fk_fact_stratification 
    FOREIGN KEY (stratification_key)
    REFERENCES dim_stratification  NOT ENFORCED
;
