/*
 * ER/Studio Data Architect SQL Code Generation
 * Project :      CommunityOne Schema - Generic Community Engagement Data Platform
 *
 * Date Created : Monday, April 28, 2026
 * Target DBMS : Databricks
 * 
 * Description: Comprehensive schema for tracking civic engagement including:
 *   - Government jurisdictions and officials
 *   - Nonprofit organizations and grants
 *   - Meetings, legislation, and policy decisions
 *   - Community health and social outcome observations
 */

/* ========================================
 * DIMENSION TABLES
 * ======================================== */

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
COMMENT 'Data source metadata and lineage tracking'
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
COMMENT 'Time dimension for temporal analysis and trend tracking'
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
    state_code                   string,
    record_start_dttm            timestamp,
    record_end_dttm              timestamp,
    current_record_ind           smallint,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_geography PRIMARY KEY (geography_key) NOT ENFORCED 
)
COMMENT 'Geographic dimension - cities, counties, states, districts'
;

/* 
 * TABLE: dim_jurisdiction 
 */
CREATE TABLE dim_jurisdiction
(
    jurisdiction_key             string         NOT NULL,
    jurisdiction_id              string,
    jurisdiction_name            string,
    jurisdiction_type            string,
    geography_key                string,
    ocd_id                       string,
    website_url                  string,
    population                   int,
    record_start_dttm            timestamp,
    record_end_dttm              timestamp,
    current_record_ind           smallint,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_jurisdiction PRIMARY KEY (jurisdiction_key) NOT ENFORCED
)
COMMENT 'Government jurisdictions - cities, counties, states, school districts'
;

/* 
 * TABLE: dim_organization 
 */
CREATE TABLE dim_organization
(
    organization_key             string         NOT NULL,
    ein                          string,
    organization_name            string,
    organization_type            string,
    ntee_code                    string,
    ntee_description             string,
    subsection_code              string,
    foundation_code              string,
    deductibility_status         string,
    exempt_status_code           string,
    geography_key                string,
    state_code                   string,
    city                         string,
    zip_code                     string,
    asset_amount                 decimal(18, 2),
    income_amount                decimal(18, 2),
    revenue_amount               decimal(18, 2),
    ruling_date                  string,
    tax_period                   string,
    mission_statement            string,
    is_private_foundation        boolean,
    record_start_dttm            timestamp,
    record_end_dttm              timestamp,
    current_record_ind           smallint,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_dim_organization PRIMARY KEY (organization_key) NOT ENFORCED
)
COMMENT 'Nonprofit organizations, churches, private foundations (IRS EO-BMF)'
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
    indicator_nbr                 string,
    indicator_group_type          string,
    indicator_desc                string,
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
COMMENT 'Community outcome measures - health, economic, education, social indicators'
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
    state_abbr                   string,
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
COMMENT 'Demographic stratification - age, race, income, education levels'
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

/* ========================================
 * FACT TABLES
 * ======================================== */

/* 
 * TABLE: fact_communityone_observation 
 * Generic community outcome observations - health, economic, social, education
 */
CREATE TABLE fact_communityone_observation
(
    observation_key              string              NOT NULL,
    measure_key                  string,
    geography_key                string,
    jurisdiction_key             string,
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
    CONSTRAINT pk_fact_communityone PRIMARY KEY (observation_key) NOT ENFORCED 
)
COMMENT 'Community outcome observations - health, education, economic, social indicators'
;

/* 
 * TABLE: fact_grant 
 * Individual grant transactions - foundation grants, government grants, federal funding
 */
CREATE TABLE fact_grant
(
    grant_key                    string              NOT NULL,
    grant_id                     string,
    recipient_org_key            string,
    recipient_jurisdiction_key   string,
    funder_org_key               string,
    funder_jurisdiction_key      string,
    recipient_ein                string,
    recipient_name               string,
    recipient_type               string,
    funder_ein                   string,
    funder_name                  string,
    funder_type                  string,
    grant_amount                 decimal(18, 2),
    grant_purpose                string,
    program_area                 string,
    award_date_key               int,
    start_date_key               int,
    end_date_key                 int,
    grant_duration_months        int,
    grant_status                 string,
    funding_source               string,
    is_multi_year                boolean,
    restrictions                 string,
    reporting_requirements       string,
    source_key                   string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_fact_grant PRIMARY KEY (grant_key) NOT ENFORCED
)
COMMENT 'Grant transactions from 990 Schedule I, 990-PF, USASpending.gov, state grant databases'
;

/* 
 * TABLE: fact_nonprofit_finance 
 * Annual nonprofit financial filings from Form 990
 */
CREATE TABLE fact_nonprofit_finance
(
    filing_key                   string              NOT NULL,
    organization_key             string,
    ein                          string,
    tax_year                     int,
    fiscal_year_end_date_key     int,
    filing_date_key              int,
    total_revenue                decimal(18, 2),
    total_expenses               decimal(18, 2),
    total_assets                 decimal(18, 2),
    total_liabilities            decimal(18, 2),
    net_assets                   decimal(18, 2),
    program_expenses             decimal(18, 2),
    admin_expenses               decimal(18, 2),
    fundraising_expenses         decimal(18, 2),
    grants_paid                  decimal(18, 2),
    contributions_received       decimal(18, 2),
    government_grants            decimal(18, 2),
    foundation_grants            decimal(18, 2),
    corporate_donations          decimal(18, 2),
    individual_donations         decimal(18, 2),
    membership_dues              decimal(18, 2),
    special_events_revenue       decimal(18, 2),
    program_service_revenue      decimal(18, 2),
    investment_income            decimal(18, 2),
    rental_income                decimal(18, 2),
    other_revenue                decimal(18, 2),
    employee_count               int,
    volunteer_count              int,
    overhead_ratio               decimal(8, 4),
    fundraising_efficiency       decimal(8, 4),
    form_990_url                 string,
    source_key                   string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_fact_nonprofit_finance PRIMARY KEY (filing_key) NOT ENFORCED
)
COMMENT 'Annual nonprofit 990 filings with revenue breakdown and efficiency metrics'
;

/* 
 * TABLE: fact_jurisdiction_budget 
 * Government budgets and spending by jurisdiction
 */
CREATE TABLE fact_jurisdiction_budget
(
    budget_key                   string              NOT NULL,
    jurisdiction_key             string,
    fiscal_year                  int,
    fiscal_year_start_date_key   int,
    fiscal_year_end_date_key     int,
    budget_type                  string,
    total_revenue                decimal(18, 2),
    total_expenditures           decimal(18, 2),
    total_debt                   decimal(18, 2),
    property_tax_revenue         decimal(18, 2),
    sales_tax_revenue            decimal(18, 2),
    federal_grants               decimal(18, 2),
    state_grants                 decimal(18, 2),
    general_fund_balance         decimal(18, 2),
    budget_document_url          string,
    published_date_key           int,
    source_key                   string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_fact_jurisdiction_budget PRIMARY KEY (budget_key) NOT ENFORCED
)
COMMENT 'Government budgets and financial data by jurisdiction'
;

/* 
 * TABLE: fact_meeting 
 * Government meetings, hearings, trainings, community events
 */
CREATE TABLE fact_meeting
(
    meeting_key                  string              NOT NULL,
    meeting_id                   string,
    jurisdiction_key             string,
    meeting_date_key             int,
    meeting_type                 string,
    meeting_title                string,
    body_name                    string,
    status                       string,
    platform                     string,
    source_url                   string,
    has_agenda                   boolean,
    has_minutes                  boolean,
    has_video                    boolean,
    topic_tags                   array<string>,
    location_type                string,
    record_created_dttm          timestamp,
    record_last_modified_dttm    timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_fact_meeting PRIMARY KEY (meeting_key) NOT ENFORCED
)
COMMENT 'Government meetings, public hearings, trainings, community events'
;

/* 
 * TABLE: bridge_grant_program_area
 * Many-to-many relationship between grants and program areas (grants can support multiple areas)
 */
CREATE TABLE bridge_grant_program_area
(
    grant_key                    string              NOT NULL,
    program_area_code            string              NOT NULL,
    program_area_desc            string,
    allocation_pct               decimal(5, 2),
    record_created_dttm          timestamp,
    load_run_id                  bigint,
    CONSTRAINT pk_bridge_grant_program PRIMARY KEY (grant_key, program_area_code) NOT ENFORCED
)
COMMENT 'Bridge table for grant program areas (multi-purpose grants)'
;

/* ========================================
 * FOREIGN KEY CONSTRAINTS
 * ======================================== */

/* dim_measure */
ALTER TABLE dim_measure ADD CONSTRAINT fk_measure_source 
    FOREIGN KEY (source_key)
    REFERENCES dim_data_source  NOT ENFORCED
;

/* dim_jurisdiction */
ALTER TABLE dim_jurisdiction ADD CONSTRAINT fk_jurisdiction_geography
    FOREIGN KEY (geography_key)
    REFERENCES dim_geography  NOT ENFORCED
;

/* dim_organization */
ALTER TABLE dim_organization ADD CONSTRAINT fk_organization_geography
    FOREIGN KEY (geography_key)
    REFERENCES dim_geography  NOT ENFORCED
;

/* fact_communityone_observation */
ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_postal 
    FOREIGN KEY (postal_key)
    REFERENCES dim_postal  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_state 
    FOREIGN KEY (state_key)
    REFERENCES dim_state  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_survey_period 
    FOREIGN KEY (survey_period_key)
    REFERENCES dim_survey_period  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_date 
    FOREIGN KEY (date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_geography 
    FOREIGN KEY (geography_key)
    REFERENCES dim_geography  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_jurisdiction
    FOREIGN KEY (jurisdiction_key)
    REFERENCES dim_jurisdiction  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_measure 
    FOREIGN KEY (measure_key)
    REFERENCES dim_measure  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_statistic 
    FOREIGN KEY (statistic_key)
    REFERENCES dim_statistic_type  NOT ENFORCED
;

ALTER TABLE fact_communityone_observation ADD CONSTRAINT fk_observation_stratification 
    FOREIGN KEY (stratification_key)
    REFERENCES dim_stratification  NOT ENFORCED
;

/* fact_grant */
ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_recipient_org
    FOREIGN KEY (recipient_org_key)
    REFERENCES dim_organization  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_recipient_jurisdiction
    FOREIGN KEY (recipient_jurisdiction_key)
    REFERENCES dim_jurisdiction  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_funder_org
    FOREIGN KEY (funder_org_key)
    REFERENCES dim_organization  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_funder_jurisdiction
    FOREIGN KEY (funder_jurisdiction_key)
    REFERENCES dim_jurisdiction  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_award_date
    FOREIGN KEY (award_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_start_date
    FOREIGN KEY (start_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_end_date
    FOREIGN KEY (end_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_grant ADD CONSTRAINT fk_grant_source
    FOREIGN KEY (source_key)
    REFERENCES dim_data_source  NOT ENFORCED
;

/* fact_nonprofit_finance */
ALTER TABLE fact_nonprofit_finance ADD CONSTRAINT fk_finance_organization
    FOREIGN KEY (organization_key)
    REFERENCES dim_organization  NOT ENFORCED
;

ALTER TABLE fact_nonprofit_finance ADD CONSTRAINT fk_finance_fiscal_year_end
    FOREIGN KEY (fiscal_year_end_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_nonprofit_finance ADD CONSTRAINT fk_finance_filing_date
    FOREIGN KEY (filing_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_nonprofit_finance ADD CONSTRAINT fk_finance_source
    FOREIGN KEY (source_key)
    REFERENCES dim_data_source  NOT ENFORCED
;

/* fact_jurisdiction_budget */
ALTER TABLE fact_jurisdiction_budget ADD CONSTRAINT fk_budget_jurisdiction
    FOREIGN KEY (jurisdiction_key)
    REFERENCES dim_jurisdiction  NOT ENFORCED
;

ALTER TABLE fact_jurisdiction_budget ADD CONSTRAINT fk_budget_fiscal_year_start
    FOREIGN KEY (fiscal_year_start_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_jurisdiction_budget ADD CONSTRAINT fk_budget_fiscal_year_end
    FOREIGN KEY (fiscal_year_end_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_jurisdiction_budget ADD CONSTRAINT fk_budget_published_date
    FOREIGN KEY (published_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

ALTER TABLE fact_jurisdiction_budget ADD CONSTRAINT fk_budget_source
    FOREIGN KEY (source_key)
    REFERENCES dim_data_source  NOT ENFORCED
;

/* fact_meeting */
ALTER TABLE fact_meeting ADD CONSTRAINT fk_meeting_jurisdiction
    FOREIGN KEY (jurisdiction_key)
    REFERENCES dim_jurisdiction  NOT ENFORCED
;

ALTER TABLE fact_meeting ADD CONSTRAINT fk_meeting_date
    FOREIGN KEY (meeting_date_key)
    REFERENCES dim_date  NOT ENFORCED
;

/* bridge_grant_program_area */
ALTER TABLE bridge_grant_program_area ADD CONSTRAINT fk_bridge_grant
    FOREIGN KEY (grant_key)
    REFERENCES fact_grant  NOT ENFORCED
;
