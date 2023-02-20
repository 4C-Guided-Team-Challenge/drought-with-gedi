# for GEDI query
# psql query for L2B 
python3 -m pdb drought/data/gedi_query_psql.py \
        --year_range 2019 2023 --product_level level_2b --fields pai rh100 pai_z pavd_z

# python3 -m pdb query_h5.py