{% macro calculate_confidence(datasource_field) %}
    /*
        Calculate confidence score based on datasource
        
        Returns FLOAT between 0.0 and 1.0
        
        Usage:
            {{ calculate_confidence('datasource') }}
    */
    CASE 
        WHEN {{ datasource_field }} IN ('openstates_api', 'irs_bmf', 'irs_990') THEN 1.0
        WHEN {{ datasource_field }} IN ('localview', 'youtube_api') THEN 0.95
        WHEN {{ datasource_field }} = 'legistar_api' THEN 0.90
        WHEN {{ datasource_field }} = 'youtube_metadata' THEN 0.85
        WHEN {{ datasource_field }} = 'manual_entry' THEN 0.75
        WHEN {{ datasource_field }} = 'gemini_ai_extraction' THEN 0.60
        ELSE 0.50
    END::FLOAT
{% endmacro %}
