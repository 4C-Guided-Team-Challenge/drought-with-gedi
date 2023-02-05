# for GEDI query
# psql query for L2B 
python3 -m pdb drought/data/gedi_query_psql.py`` \
        --product_level level_2b --fields pai l2b_quality_flag
# # psql query for L2A (L2A currently not available for PSQL query)
# python3 -m pdb query_psql.py \
#         --product_level level_2a --fields rh quality_flag --rh_percentiles 80 100

# python3 -m pdb query_h5.py